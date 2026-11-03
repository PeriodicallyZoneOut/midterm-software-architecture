"""Editable diagrams placed inside the original Slidesgo layouts."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
INK, MUTED, BLUE, PALE, LIGHT, WHITE = '3D3D3D','494949','477797','D6EEFE','EEEEEE','FFFFFF'
ACCENT, MID, GREY = '77C6FC','BBE3FE','9E9E9E'
FONT = 'Aptos'
ops, plan, notes, layout_map = [], [], [], []
slide, shape_id = -1, 100

def op(name, **kw):
    ops.append({'op':name,**kw})

def emu(n): return int(round(n*914400))

def raw(xml, href=None):
    kw = dict(slide_index=slide,shape_xml=xml)
    if href:
        kw['rel_external'] = [['rIdLink','http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',href]]
    op('add_raw_shape_xml',**kw)

def absolute_text(s,x,y,w,h,size=14,color=INK,bold=False,align='l',href=None):
    global shape_id
    shape_id += 1
    paragraphs=[]
    for part in s.split('\n'):
        paragraphs.append(f'''<a:p><a:pPr algn="{align}"><a:lnSpc><a:spcPct val="106000"/></a:lnSpc><a:spcAft><a:spcPts val="150"/></a:spcAft></a:pPr><a:r><a:rPr lang="vi-VN" sz="{int(size*100)}" b="{int(bold)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/><a:cs typeface="{FONT}"/></a:rPr><a:t>{escape(part)}</a:t></a:r><a:endParaRPr lang="vi-VN" sz="{int(size*100)}"/></a:p>''')
    raw(f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:nvSpPr><p:cNvPr id="{shape_id}" name="Nội dung {shape_id}">{'<a:hlinkClick r:id="rIdLink"/>' if href else ''}</p:cNvPr><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" rIns="0" tIns="0" bIns="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>{''.join(paragraphs)}</p:txBody></p:sp>''',href)

# Diagrams use a virtual 9-inch-wide content area, fitted between the template's
# decorative side rails. The inherited template artwork is never covered.
def X(x): return 1.20+(x-.5)*(7.6/9)
def Y(y): return 1.52+(y-1.7)*.94
def W(w): return w*(7.6/9)
def H(h): return h*.94

def text(s,x,y,w,h,size=14,color=INK,bold=False,align='l',href=None):
    absolute_text(s,X(x),Y(y),W(w),H(h),max(9,size*.94),color,bold,align,href)

def rect(x,y,w,h,fill=PALE,border=None,rounded=False):
    global shape_id
    shape_id += 1
    ln=f'<a:solidFill><a:srgbClr val="{border}"/></a:solidFill>' if border else '<a:noFill/>'
    raw(f'''<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:nvSpPr><p:cNvPr id="{shape_id}" name="Khối {shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{emu(X(x))}" y="{emu(Y(y))}"/><a:ext cx="{emu(W(w))}" cy="{emu(H(h))}"/></a:xfrm><a:prstGeom prst="{'roundRect' if rounded else 'rect'}"><a:avLst><a:gd name="adj" fmla="val 5000"/></a:avLst></a:prstGeom><a:solidFill><a:srgbClr val="{fill}"/></a:solidFill><a:ln w="10000">{ln}</a:ln><a:effectLst/></p:spPr></p:sp>''')

def line(x1,y1,x2,y2,color=BLUE,arrow=False,dashed=False,width=1.4):
    global shape_id
    shape_id += 1
    flip=(' flipH="1"' if x2<x1 else '')+(' flipV="1"' if y2<y1 else '')
    raw(f'''<p:cxnSp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:nvCxnSpPr><p:cNvPr id="{shape_id}" name="Mũi tên {shape_id}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr><a:xfrm{flip}><a:off x="{emu(X(min(x1,x2)))}" y="{emu(Y(min(y1,y2)))}"/><a:ext cx="{emu(W(abs(x2-x1)))}" cy="{emu(H(abs(y2-y1)))}"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom><a:ln w="{int(width*12700)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:prstDash val="{'dash' if dashed else 'solid'}"/><a:headEnd type="none"/><a:tailEnd type="{'triangle' if arrow else 'none'}"/></a:ln></p:spPr></p:cxnSp>''')

def path(points,color=BLUE,dashed=False):
    for i,(a,b) in enumerate(zip(points,points[1:])):
        line(*a,*b,color=color,dashed=dashed,arrow=i==len(points)-2)

def node(title,body,x,y,w,h,fill=PALE,color=INK):
    rect(x,y,w,h,fill,BLUE,True)
    text(title,x+.13,y+.12,w-.26,.34,14,color,True)
    if body:
        text(body,x+.13,y+.55,w-.26,h-.63,12,color)

def card(title,body,x,y,w,h=2.75):
    rect(x,y,w,h,LIGHT,rounded=True)
    rect(x,y,w,.045,ACCENT)
    text(title,x+.16,y+.18,w-.32,.7,16,BLUE,True)
    text(body,x+.16,y+.99,w-.32,h-1.1,14)

def callout(s,y=4.95):
    rect(.5,y,9,.42,PALE,rounded=True)
    text(s,.64,y+.085,8.72,.28,11.7,BLUE,True)

def new(title,section,source,note,archetype='content_text',layout=None,special=False):
    global slide
    slide+=1
    if layout is None:
        layout='TITLE_AND_BODY_1' if slide%3==1 else 'TITLE_ONLY'
    op('add_slide',layout_name=layout)
    if not special:
        absolute_text(section.upper(),1.25,.18,7.4,.21,9,BLUE,True)
        display=title
        if len(title)>57 and '\n' not in title:
            split=min((i for i,c in enumerate(title) if c==' '),key=lambda i:abs(i-len(title)/2))
            display=title[:split]+'\n'+title[split+1:]
        absolute_text(display,1.27,.56,7.46,.89,21.5,INK,True)
    if layout == 'TITLE':
        absolute_text('Nguồn: '+source,6.25,5.12,2.65,.32,9,MUTED)
    elif layout == 'CUSTOM_9':
        absolute_text('Nguồn: '+source,2.72,5.13,5.5,.3,9,MUTED)
    elif layout == 'MAIN_POINT':
        absolute_text('Nguồn: '+source,1.25,.24,6,.26,9,MUTED)
    else:
        absolute_text('Nguồn: '+source,1.25,5.10,7.15,.30,9,MUTED)
    absolute_text(f'{slide+1:02}',9.25 if layout=='TITLE' else 8.6,5.14,.25,.20,9,BLUE,True,align='r')
    op('add_notes',slide_index=slide,text=note+'\n\nNguồn: '+source)
    role=archetype if archetype in {'title_slide','section_divider','end_slide'} else 'supporting'
    plan.append(dict(slide_number=slide+1,story_role=role,archetype_id=archetype,action_title=title,source_note=source,visual_hint='Sơ đồ kiến trúc có thể chỉnh sửa; bố cục gốc Slidesgo'))
    notes.append((title,note+'\n\nNguồn: '+source))
    layout_map.append({'trang':slide+1,'bo_cuc_goc':layout,'tieu_de':title})

def template_art(source_slide):
    """Keep authentic slide-level vector artwork in addition to layout graphics."""
    from pptx import Presentation
    template=Presentation(ROOT/'Technology Consulting  by Slidesgo.pptx')
    for shape in template.slides[source_slide-1].shapes:
        if not shape.is_placeholder:
            if shape._element.xpath('.//a:blip/@r:embed'):
                raise ValueError('The selected artwork needs image relationships.')
            raw(shape._element.xml)

def table(headers,rows,widths=None):
    widths=widths or [3,3,3]
    xs=[.5]
    for v in widths[:-1]: xs.append(xs[-1]+v)
    rh=min(.6,3.2/(len(rows)+1))
    for j,row in enumerate([headers]+rows):
        y=1.77+j*rh
        rect(.5,y,9,rh-.045,BLUE if j==0 else (LIGHT if j%2 else PALE))
        for x,w,s in zip(xs,widths,row):
            text(s,x+.13,y+.10,w-.26,rh-.13,12.5,WHITE if j==0 else INK,j==0)

def finish():
    project=ROOT/'project'
    out=ROOT/'output'
    out.mkdir(exist_ok=True)
    # Localize the native Thanks-layout attribution, preserving its hyperlinks.
    # The original supplied PPTX stays untouched.
    from pptx import Presentation
    from pptx.util import Pt
    from pptx.dml.color import RGBColor
    base=Presentation(project/'base_template.pptx')
    credit_translations={
        'CREDITS:':'GHI CÔNG:',
        ' This presentation template was created by ':' Mẫu trình chiếu do ',
        ', including icons by ':', biểu tượng: ',
        ', infographics & images by ':', đồ họa và hình ảnh: ',
        ' and illustrations by ':'; minh họa: ',
    }
    for shape in base.slide_layouts[17].shapes:
        if shape.has_text_frame and ('CREDITS:' in shape.text or 'GHI CÔNG:' in shape.text):
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    run.text=credit_translations.get(run.text,run.text)
                    run.font.name=FONT
                    run.font.size=Pt(9)
                    run.font.color.rgb=RGBColor.from_string(BLUE if run.hyperlink.address else MUTED)
                    run._r.get_or_add_rPr().set('lang','vi-VN')
    base.save(project/'base_template.pptx')
    op('set_core_properties',title='Kiến trúc Micro-frontend — Phân tích demo cửa hàng trái cây',subject='Kiến trúc phần mềm; mô hình 4+1; Webpack Module Federation',author='Bài thuyết trình Kiến trúc phần mềm',keywords='micro-frontend, kiến trúc, 4+1, tiếng Việt, Slidesgo')
    document={'plan':{'deck_title':'Kiến trúc Micro-frontend — Phân tích demo cửa hàng trái cây','brief':'Giới thiệu kiến trúc micro-frontend, phân tích mã nguồn demo bằng mô hình 4+1 và đánh giá mức độ độc lập. Dùng tiếng Việt và các bố cục gốc trong mẫu Technology Consulting by Slidesgo.','audience':'Sinh viên và giảng viên môn Kiến trúc phần mềm','objective':'Giải thích ranh giới trách nhiệm, phụ thuộc, thực thi và triển khai của demo','assumptions':['Rà soát mã nguồn tĩnh; không xác nhận hành vi triển khai thực tế','Giữ nguyên tên mô-đun, API và định danh trong mã nguồn','Các thay đổi đề xuất được ghi rõ và chưa triển khai'],'slides':plan},'ops':{'operations':ops}}
    (ROOT/'slides.json').write_text(json.dumps(document,ensure_ascii=False,indent=2),encoding='utf-8')
    profile={'name':'kien-truc-micro-frontend-tieng-viet','template_path':'base_template.pptx','content_layout_catalog_path':'content_layout_catalog.json','archetypes_catalog_path':'archetypes.json','primary_color_hex':ACCENT,'text_color_dark':INK,'text_color_light':WHITE,'default_font_size_pt':13,'min_font_size_pt':9,'max_font_size_pt':48,'allowed_fonts':[FONT],'min_margin_in':.1,'enforce_template_geometry':False,'enforce_template_placeholders':False,'require_source_for_data_slides':True,'require_visual_on_content_slides':True,'asset_roots':[str(ROOT/'assets'),str(project),str(out)],'slide_margin_left_in':1.2,'slide_margin_right_in':1.2,'slide_margin_top_in':1.5,'slide_margin_bottom_in':.55}
    (project/'design-profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'speaker-notes.md').write_text('# Ghi chú thuyết trình\n\nThời lượng dự kiến: 20–25 phút, chưa gồm thảo luận.\n\n'+'\n\n'.join(f'## {i+1:02}. {title}\n\n{note}' for i,(title,note) in enumerate(notes)),encoding='utf-8')
    (out/'template-layout-map.json').write_text(json.dumps(layout_map,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Generated {len(plan)} Vietnamese slides in original Slidesgo layouts.')
