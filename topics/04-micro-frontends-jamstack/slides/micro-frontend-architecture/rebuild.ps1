$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    uv run --project tools/agent-slides python build_deck.py
    if ($LASTEXITCODE -ne 0) { throw 'Slide generation failed.' }
    uv run --project tools/agent-slides python validate_deck.py
    if ($LASTEXITCODE -ne 0) { throw 'Slide rendering or validation failed.' }
    ./export-slides.ps1
    uv run --project tools/agent-slides python check_artifacts.py
    if ($LASTEXITCODE -ne 0) { throw 'Artifact checks failed.' }
} finally {
    Pop-Location
}
