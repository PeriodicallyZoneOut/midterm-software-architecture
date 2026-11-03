"""Content coverage and geometric checks supplement the upstream heuristics."""
import json
from collections import Counter
import math
from pathlib import Path

from PIL import Image, ImageDraw
from pptx import Presentation

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
prs = Presentation(OUT / "jamstack-architecture.pptx")
ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
overlaps = []
small_fonts = []
for i, page in enumerate(prs.slides):
    text_shapes = [s for s in page.shapes if s.has_text_frame and s.text.strip()]
    # Unlike the generic overlap lint, compare text only, not text-on-panel containment.
    for a, first in enumerate(text_shapes):
        for second in text_shapes[a+1:]:
            dx = min(first.left+first.width,second.left+second.width)-max(first.left,second.left)
            dy = min(first.top+first.height,second.top+second.height)-max(first.top,second.top)
            if dx > 9144 and dy > 9144:  # .01 inch numerical tolerance
                overlaps.append({"slide":i+1,"a":first.text,"b":second.text})
    for shape in text_shapes:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if run.font.size is not None and run.font.size.pt < 9:
                    small_fonts.append({"slide":i+1,"size":run.font.size.pt,"text":run.text})

coverage = {
    "slide_count": len(prs.slides),
    "all_slides_have_notes": all(p.has_notes_slide and p.notes_slide.notes_text_frame.text.strip() for p in prs.slides),
    "all_slides_have_sources": all(any(any(label in s.text.lower() for label in ("nguồn:","source:","sources:","case study:","evidence:")) for s in p.shapes if s.has_text_frame) for p in prs.slides),
    "template_layouts":dict(Counter(p.slide_layout.name for p in prs.slides)),
    "uses_original_cover_art":any(s.shape_type == 6 for s in prs.slides[0].shapes),
    "notes_in_vietnamese":all('Nguồn:' in p.notes_slide.notes_text_frame.text for p in prs.slides),
    "required_view_slides": {"logical":14,"development":16,"process":18,"physical":22,"scenarios":24},
    "text_box_overlap_count":len(overlaps),
    "text_box_overlaps":overlaps,
    "font_below_9pt_count":len(small_fonts),
    "small_fonts":small_fonts,
    "hyperlink_count":sum(len(p._element.findall('.//a:hlinkClick', ns)) for p in prs.slides),
    "qa_ok":json.loads((OUT/'qa.json').read_text(encoding='utf-8'))['ok'],
    "native_powerpoint":json.loads((OUT/'powerpoint-check.json').read_text(encoding='utf-8-sig')),
}
coverage["ok"] = coverage["slide_count"] == 35 and coverage["all_slides_have_notes"] and coverage["all_slides_have_sources"] and coverage['notes_in_vietnamese'] and coverage['uses_original_cover_art'] and len(coverage['template_layouts'])>=5 and not overlaps and not small_fonts and coverage["qa_ok"] and coverage["native_powerpoint"]["textOverflowCount"] == 0
(OUT / 'artifact-check.json').write_text(json.dumps(coverage,indent=2),encoding='utf-8')
print(json.dumps(coverage,indent=2))

files=sorted((OUT/'slides').glob('slide-*.png'))
canvas=Image.new('RGB',(2000,math.ceil(len(files)/4)*300),'#eeeeee')
draw=ImageDraw.Draw(canvas)
for i,file in enumerate(files):
    canvas.paste(Image.open(file).resize((500,281)),((i%4)*500,(i//4)*300))
    draw.text(((i%4)*500+6,(i//4)*300+282),file.stem,fill='black')
canvas.save(OUT/'contact-sheet.png')
if not coverage['ok']:
    raise SystemExit(1)
