#Requires -Version 5.1
param([string]$Date)
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Orquestrador do dia: gera as 3 publicacoes de imagem (alerta, frase,
# radar), renderiza os PNGs via Playwright e valida as dimensoes.
#   1. generate-posts.ps1 -> pastas/HTML/legendas/fotos
#   2. render_slides.py (Playwright/Chromium) -> PNGs
#   3. valida 1080x1350 em todas as imagens
# Uso: powershell -File scripts/run.ps1
#      powershell -File scripts/run.ps1 -Date 2026-08-25
#
# Sem fallback GDI+ ainda (scripts/lib-render-gdi.ps1 nao foi portado pra
# este projeto -- ver checklist do CLAUDE.md). Se Playwright falhar, o
# script para com erro em vez de cair num fallback silencioso.
# ---------------------------------------------------------------------------

$ProcessDate = if ($Date) { [datetime]::ParseExact($Date, 'yyyy-MM-dd', $null) } else { Get-Date }

$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = @(
        "C:\Users\44428454848\AppData\Local\Programs\Python\Python312\python.exe",
        "C:\Python312\python.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
}

Write-Host "== 1/3: gerando conteudo, HTML, legendas e fotos =="
$out = if ($Date) { & (Join-Path $PSScriptRoot "generate-posts.ps1") -Date $Date } else { & (Join-Path $PSScriptRoot "generate-posts.ps1") }
$DayDir = ($out | Select-Object -Last 1).ToString().Trim()
if (-not $DayDir -or -not (Test-Path $DayDir)) { throw "generate-posts.ps1 nao retornou uma pasta valida." }
Write-Host "Pasta do dia: $DayDir`n"

$Config = Get-Content (Join-Path $PSScriptRoot "config.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$postDirs = Get-ChildItem $DayDir -Directory | Where-Object { Test-Path (Join-Path $_.FullName "_html") } | Sort-Object Name

Write-Host "== 2/3: renderizando imagens =="
if (-not (Test-Path $PythonExe)) {
    throw "Python nao encontrado em $PythonExe -- instale ou ajuste o caminho (ver GUIA-CONTEUDO-MULTINICHO.md secao 0)."
}
& $PythonExe (Join-Path $PSScriptRoot "render_slides.py") $DayDir
if ($LASTEXITCODE -ne 0) {
    throw "Playwright falhou (codigo $LASTEXITCODE). Fallback GDI+ ainda nao existe neste projeto."
}

Write-Host "`n== 3/3: validando dimensoes =="
Add-Type -AssemblyName System.Drawing
$allOk = $true; $count = 0
foreach ($pd in $postDirs) {
    foreach ($sub in @("slides", "imagem")) {
        $dir = Join-Path $pd.FullName $sub
        if (-not (Test-Path $dir)) { continue }
        foreach ($f in (Get-ChildItem $dir -Filter "*.png" | Sort-Object Name)) {
            $img = [System.Drawing.Image]::FromFile($f.FullName)
            $w = $img.Width; $h = $img.Height; $img.Dispose()
            $count++
            if ($w -ne 1080 -or $h -ne 1350) {
                Write-Warning "$($pd.Name)/$sub/$($f.Name) saiu ${w}x${h} (esperado 1080x1350)."
                $allOk = $false
            }
        }
    }
}
if ($count -eq 0) { Write-Warning "Nenhuma imagem gerada!" ; $allOk = $false }
elseif ($allOk) { Write-Host "Todas as $count imagens conferem: 1080x1350." }

Write-Host "`n============================================"
Write-Host "Concluido!  $DayDir"
foreach ($pd in $postDirs) {
    $n = 0
    foreach ($sub in @("slides", "imagem")) {
        $dir = Join-Path $pd.FullName $sub
        if (Test-Path $dir) { $n += (Get-ChildItem $dir -Filter "*.png").Count }
    }
    Write-Host ("  {0,-16} {1} imagem(ns) + legenda.txt" -f $pd.Name, $n)
}
Write-Host "Render:   Playwright/Chromium"
Write-Host "Handle:   $($Config.handle)"
Write-Host "============================================"
