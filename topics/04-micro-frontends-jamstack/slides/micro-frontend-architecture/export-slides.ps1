# Native PowerPoint rendering also proves that the generated package opens.
param([string]$Deck = 'output/micro-frontend-architecture.pptx')
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
$taskPpt = $null
$taskPres = $null
try {
    $taskDeckPath = (Resolve-Path -LiteralPath $Deck).Path
    $taskOutputPath = (Resolve-Path -LiteralPath 'output').Path
    $taskPngPath = Join-Path $taskOutputPath 'slides'
    New-Item -ItemType Directory -Force -Path $taskPngPath | Out-Null
    $taskPpt = New-Object -ComObject PowerPoint.Application
    $taskPres = $taskPpt.Presentations.Open($taskDeckPath, -1, 0, 0)
    $taskOverflow = @()
    foreach ($taskSlide in $taskPres.Slides) {
        $taskSlide.Export((Join-Path $taskPngPath ('slide-{0:D2}.png' -f $taskSlide.SlideIndex)), 'PNG', 1600, 900)
        foreach ($taskShape in $taskSlide.Shapes) {
            if ($taskShape.HasTextFrame -eq -1 -and $taskShape.TextFrame.HasText -eq -1) {
                $taskRange = $taskShape.TextFrame2.TextRange
                if ($taskRange.BoundHeight -gt ($taskShape.Height + 1.5) -or $taskRange.BoundWidth -gt ($taskShape.Width + 1.5)) {
                    $taskOverflow += [pscustomobject]@{slide=$taskSlide.SlideIndex; shape=$taskShape.Name; text=$taskShape.TextFrame.TextRange.Text; boundHeight=$taskRange.BoundHeight; height=$taskShape.Height; boundWidth=$taskRange.BoundWidth; width=$taskShape.Width}
                }
            }
        }
    }
    $taskPres.SaveAs((Join-Path $taskOutputPath 'micro-frontend-architecture.pdf'), 32)
    $taskReport = [pscustomobject]@{opened=$true; slides=$taskPres.Slides.Count; exportedPng=$true; exportedPdf=$true; textOverflowCount=$taskOverflow.Count; textOverflow=$taskOverflow}
    $taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOutputPath 'powerpoint-check.json') -Encoding UTF8
    $taskReport | ConvertTo-Json -Depth 3
} finally {
    if ($taskPres) { $taskPres.Close(); [Runtime.InteropServices.Marshal]::ReleaseComObject($taskPres) | Out-Null }
    if ($taskPpt) { $taskPpt.Quit(); [Runtime.InteropServices.Marshal]::ReleaseComObject($taskPpt) | Out-Null }
    Pop-Location
}
