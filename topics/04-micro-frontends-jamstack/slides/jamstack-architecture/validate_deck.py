"""Run the requested agent-slides CLI with explicit JSON result checks."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

def run(name, *args, require_ok=True):
    result = subprocess.run([sys.executable, "-m", "slides_cli.cli", *args, "--compact", "--verbose"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    (OUT / f"{name}.json").write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        print(result.stdout, result.stderr)
        raise SystemExit(result.returncode)
    data = json.loads(result.stdout)
    if require_ok and data.get("ok") is False:
        print(f"{name}: failed; see output/{name}.json")
        print(json.dumps(data.get("summary", data.get("error", {})), indent=2))
        raise SystemExit(1)
    print(f"{name}: ok; {data.get('summary', '')}")
    return data

profile = ["--profile", "project/design-profile.json"]
run("preflight", "preflight", "--project-dir", "project", *profile)
run("dry-run", "render", "--slides-json", "@slides.json", *profile, "--dry-run")
run("render", "render", "--slides-json", "@slides.json", *profile, "--output", "output/jamstack-architecture.pptx")
run("plan-content", "plan-inspect", "--slides-json", "@slides.json")
run("lint", "lint", "output/jamstack-architecture.pptx", *profile, "--slides-json", "@slides.json", require_ok=False)
run("qa", "qa", "output/jamstack-architecture.pptx", *profile, "--slides-json", "@slides.json")
