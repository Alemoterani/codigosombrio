#Requires -Version 5.1
param([string]$Date)
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Gera as 3 publicacoes de imagem do dia a partir dos rascunhos em scripts/:
#   post-1-alerta.json  -> carrossel FOTO (golpes/riscos de tech e IA)
#   post-2-frase.json   -> imagem unica (citacao + autor)
#   post-3-radar.json   -> carrossel editorial (fundo claro)
#
# Adaptado do motor do projeto agencia-conteudo/@frontinvicto para o
# @codigosombrio -- mesma logica, troca so o nome dos tipos de post e a
# cor de destaque (vermelho -> ciano, ver CLAUDE.md secao MARCA E PALETA).
#
# Saida: publicacoes/AAAA-MM-DD/<n>-<tipo>/ com _html/, _assets/,
# legenda.txt e data.json. A conversao pra PNG e' feita por
# scripts/run.ps1 (Playwright). Ultima linha do stdout = pasta do dia.
#
# -Date AAAA-MM-DD (opcional): gera pra essa data em vez da data do sistema.
# ---------------------------------------------------------------------------

$Root = Split-Path -Parent $PSScriptRoot
$Config = Get-Content (Join-Path $PSScriptRoot "config.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$Handle = $Config.handle
$Accent = if ($Config.accent_color) { $Config.accent_color } else { "#00D9FF" }
$AccentDark = "#0A7A94"   # variante mais escura do destaque, usada onde precisa de texto branco por cima (pill do RADAR)
$ProcessDate = if ($Date) { [datetime]::ParseExact($Date, 'yyyy-MM-dd', $null) } else { Get-Date }
$DateStr = $ProcessDate.ToString("yyyy-MM-dd")
$DateLabel = $ProcessDate.ToString("dd.MM.yyyy")
$DayDir = Join-Path (Join-Path $Root "publicacoes") $DateStr

$PostDefs = @(
    @{ Key = 'alerta'; File = 'post-1-alerta.json'; Folder = '1-alerta' },
    @{ Key = 'frase';  File = 'post-2-frase.json';  Folder = '2-frase' },
    @{ Key = 'radar';  File = 'post-3-radar.json';  Folder = '3-radar' }
)

function Esc([string]$s) { return [System.Security.SecurityElement]::Escape($s) }

# ---------------------------------------------------------------------------
# Marca d'agua discreta (canto inferior direito de todo slide).
# scripts/brand/logo.png = so' o simbolo, fundo transparente. Opcional:
# logo-escuro.png pro RADAR (fundo claro). Se nao existir, sai sem marca,
# sem quebrar a geracao.
# ---------------------------------------------------------------------------
$BrandDir      = Join-Path $PSScriptRoot "brand"
$HasLogo       = Test-Path (Join-Path $BrandDir "logo.png")
$HasLogoEscuro = Test-Path (Join-Path $BrandDir "logo-escuro.png")
$LogoHtml      = if ($HasLogo) { '    <img class="brandmark" src="../../../../scripts/brand/logo.png" alt="">' } else { "" }
$LogoHtmlDark  = if ($HasLogoEscuro) { '    <img class="brandmark" src="../../../../scripts/brand/logo-escuro.png" alt="">' } elseif ($HasLogo) { $LogoHtml } else { "" }
if (-not $HasLogo) { Write-Warning "scripts/brand/logo.png nao encontrado -- os slides vao sair sem a marca." }

# ---------------------------------------------------------------------------
# CSS: base comum + bloco especifico de cada tipo de post
# ---------------------------------------------------------------------------
function Get-BaseCss {
    @"
  @font-face{ font-family:'Inter'; font-weight:400; src:url('../../../../scripts/fonts/Inter-Regular.ttf') format('truetype'); }
  @font-face{ font-family:'Inter'; font-weight:700; src:url('../../../../scripts/fonts/Inter-Bold.ttf') format('truetype'); }
  @font-face{ font-family:'Inter Black'; font-weight:900; src:url('../../../../scripts/fonts/Inter-Black.ttf') format('truetype'); }
  @font-face{ font-family:'JetBrains Mono'; font-weight:400; src:url('../../../../scripts/fonts/JetBrainsMono-Regular.ttf') format('truetype'); }
  @font-face{ font-family:'JetBrains Mono'; font-weight:500; src:url('../../../../scripts/fonts/JetBrainsMono-Medium.ttf') format('truetype'); }
  @font-face{ font-family:'JetBrains Mono'; font-weight:700; src:url('../../../../scripts/fonts/JetBrainsMono-Bold.ttf') format('truetype'); }
  *{box-sizing:border-box;margin:0;padding:0;}
  html,body{width:1080px;height:1350px;overflow:hidden;}
  .slide{
    width:1080px;height:1350px;position:relative;overflow:hidden;
    font-family:'Inter',sans-serif;
    display:flex;flex-direction:column;justify-content:space-between;
    padding:96px 84px 74px;
    background-color:#0A0A0C;
  }
  .content{ display:flex; flex-direction:column; }
  .brandmark{ position:absolute; right:84px; bottom:62px; height:52px; width:auto;
              opacity:.92; z-index:2; }
  .fmt-radar .brandmark{ opacity:1; }
"@
}

function Get-AlertaCss {
    @"
  /* ===== FOTO (unico formato do ALERTA) ===== */
  .slide.fmt-foto{ background-size:cover; background-position:center; background-repeat:no-repeat; background-color:#1a1d24; }
  .fmt-foto .scrim{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.62) 0%, rgba(0,0,0,.12) 30%, rgba(0,0,0,.18) 55%, rgba(0,0,0,.82) 100%); }
  .fmt-foto .topbar, .fmt-foto .content, .fmt-foto .handle{ position:relative; z-index:1; }
  .fmt-foto .topbar{ font-family:'JetBrains Mono',monospace; font-size:32px; letter-spacing:0.06em; text-transform:uppercase; color:$Accent; display:block; }
  .fmt-foto .headline{ font-family:'Inter Black','Inter',sans-serif; font-weight:900; font-size:112px; line-height:1.02; letter-spacing:-0.015em; color:#fff; text-shadow:0 2px 16px rgba(0,0,0,.6); }
  .fmt-foto .body-txt{ font-size:50px; line-height:1.35; color:#fff; margin-top:36px; text-shadow:0 1px 10px rgba(0,0,0,.7); }
  .fmt-foto .handle{ font-family:'JetBrains Mono',monospace; font-size:32px; color:rgba(255,255,255,.65); display:block; }
"@
}

function Get-FraseCss {
    @"
  /* ===== FRASE (imagem unica, foto + citacao dominante) ===== */
  .slide.fmt-frase{ background-size:cover; background-position:center; background-repeat:no-repeat; background-color:#08080A; }
  .fmt-frase .scrim{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.80) 0%, rgba(0,0,0,.58) 32%, rgba(0,0,0,.68) 62%, rgba(0,0,0,.93) 100%); }
  .fmt-frase .topbar, .fmt-frase .content, .fmt-frase .footer-row{ position:relative; z-index:1; }
  .fmt-frase .topbar{ font-family:'JetBrains Mono',monospace; font-size:32px; letter-spacing:0.16em; text-transform:uppercase; color:$Accent; display:block; }
  .fmt-frase .content{ flex:1; justify-content:center; }
  .fmt-frase .mark{ font-family:'Inter Black','Inter',sans-serif; font-weight:900; font-size:170px; line-height:0.55; color:$Accent; }
  .fmt-frase .headline{ font-family:'Inter Black','Inter',sans-serif; font-weight:900; font-size:116px; line-height:1.0; letter-spacing:-0.02em; text-transform:uppercase; color:#fff; text-shadow:0 4px 28px rgba(0,0,0,.8); margin-top:34px; }
  .fmt-frase .rule{ width:104px; height:7px; background:$Accent; margin:46px 0 26px; }
  .fmt-frase .autor{ font-family:'JetBrains Mono',monospace; font-weight:700; font-size:38px; letter-spacing:0.10em; text-transform:uppercase; color:#fff; }
  .fmt-frase .fonte{ font-family:'JetBrains Mono',monospace; font-size:29px; letter-spacing:0.06em; color:rgba(255,255,255,.55); margin-top:12px; }
  .fmt-frase .handle{ font-family:'JetBrains Mono',monospace; font-size:32px; color:rgba(255,255,255,.6); }
"@
}

function Get-RadarCss {
    @"
  /* ===== RADAR (editorial, fundo claro = credibilidade e contraste no feed) ===== */
  .slide.fmt-radar{ background:#F4F1E9; }
  .fmt-radar .topbar{ display:flex; justify-content:space-between; align-items:center; }
  .fmt-radar .tag{ background:$AccentDark; color:#fff; font-family:'JetBrains Mono',monospace; font-weight:700; font-size:29px; letter-spacing:0.10em; text-transform:uppercase; padding:15px 28px; border-radius:6px; }
  .fmt-radar .data{ font-family:'JetBrains Mono',monospace; font-size:29px; letter-spacing:0.06em; color:#6B6B73; }
  .fmt-radar .headline{ font-family:'Inter Black','Inter',sans-serif; font-weight:900; font-size:120px; line-height:1.0; letter-spacing:-0.025em; color:#0A0A0C; }
  .fmt-radar .body-txt{ font-size:50px; line-height:1.35; color:#3A3A42; margin-top:38px; }
  .fmt-radar .fonte{ font-family:'JetBrains Mono',monospace; font-size:27px; letter-spacing:0.04em; color:#6B6B73; text-transform:uppercase; }
  .fmt-radar .rule{ height:3px; background:#0A0A0C; margin:20px 0; }
  .fmt-radar .meta{ display:flex; justify-content:space-between; align-items:baseline; font-family:'JetBrains Mono',monospace; font-size:30px; color:#0A0A0C; }

  /* ===== RADAR COM FOTO (foto em cima, papel embaixo = leitura de jornal) ===== */
  .slide.fmt-radar-foto{ background:#F4F1E9; padding:0; }
  .fmt-radar-foto .foto{ flex:none; height:560px; background-color:#1A1D24; background-size:cover; background-position:center; background-repeat:no-repeat; }
  .fmt-radar-foto .painel{ flex:1; display:flex; flex-direction:column; justify-content:space-between; padding:52px 84px 74px; min-height:0; }
  .fmt-radar-foto .topbar{ display:flex; justify-content:space-between; align-items:center; }
  .fmt-radar-foto .tag{ background:$AccentDark; color:#fff; font-family:'JetBrains Mono',monospace; font-weight:700; font-size:29px; letter-spacing:0.10em; text-transform:uppercase; padding:15px 28px; border-radius:6px; }
  .fmt-radar-foto .data{ font-family:'JetBrains Mono',monospace; font-size:29px; letter-spacing:0.06em; color:#6B6B73; }
  .fmt-radar-foto .headline{ font-family:'Inter Black','Inter',sans-serif; font-weight:900; font-size:88px; line-height:1.02; letter-spacing:-0.02em; color:#0A0A0C; }
  .fmt-radar-foto .body-txt{ font-size:44px; line-height:1.32; color:#3A3A42; margin-top:24px; }
  .fmt-radar-foto .footer-row{ margin-top:30px; }
  .fmt-radar-foto .fonte{ font-family:'JetBrains Mono',monospace; font-size:27px; letter-spacing:0.04em; color:#6B6B73; text-transform:uppercase; }
  .fmt-radar-foto .rule{ height:3px; background:#0A0A0C; margin:18px 0; }
  .fmt-radar-foto .meta{ display:flex; justify-content:space-between; align-items:baseline; font-family:'JetBrains Mono',monospace; font-size:30px; color:#0A0A0C; }
"@
}

# script de protecao contra estouro -- roda em TODO slide
function Get-FitScript {
    @"
  <script>
    (function(){
      var slide = document.querySelector('.slide');
      var headline = document.querySelector('.headline');
      var bodyTxt = document.querySelector('.body-txt');
      if (!slide || !headline) { document.body.setAttribute('data-fit-done','1'); return; }

      var size = parseFloat(getComputedStyle(headline).fontSize);
      while (headline.scrollWidth > headline.clientWidth + 1 && size > 52) {
        size -= 4; headline.style.fontSize = size + 'px';
      }
      var hs = parseFloat(getComputedStyle(headline).fontSize);
      var bs = bodyTxt ? parseFloat(getComputedStyle(bodyTxt).fontSize) : 0;
      var guard = 0;
      while (slide.scrollHeight > slide.clientHeight + 1 && guard < 50 && (hs > 52 || bs > 32)) {
        if (hs > 52) { hs -= 4; headline.style.fontSize = hs + 'px'; }
        if (bodyTxt && bs > 32) { bs -= 2; bodyTxt.style.fontSize = bs + 'px'; }
        guard++;
      }
      document.body.setAttribute('data-fit-done','1');
    })();
  </script>
"@
}

function Write-SlideHtml {
    param([string]$SlideClass, [string]$Css, [string]$Inner, [string]$InlineStyle, [string]$OutputPath)
    $html = @"
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
$(Get-BaseCss)
$Css
</style>
</head>
<body>
  <div class="slide $SlideClass" style="$InlineStyle">
$Inner
  </div>
$(Get-FitScript)
</body>
</html>
"@
    [System.IO.File]::WriteAllText($OutputPath, $html, [System.Text.UTF8Encoding]::new($false))
}

function Get-Photo {
    param([string]$Url, [string]$Dest, [string]$Label)
    if (-not $Url) { return $null }
    $tentativas = 0
    while ($tentativas -lt 4) {
        $tentativas++
        try {
            Write-Host "  baixando foto ($Label)..."
            Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing -ErrorAction Stop -Headers @{ "User-Agent" = "codigosombrio-content-tool/1.0 (contato: alemoterani@hotmail.com)" }
            Start-Sleep -Milliseconds 1500
            return $Dest
        } catch {
            $ehRateLimit = $_.Exception.Message -match '429'
            if ($ehRateLimit -and $tentativas -lt 4) {
                $espera = 8 * $tentativas
                Write-Warning "  429 (rate limit) em $Label -- esperando ${espera}s e tentando de novo (tentativa $tentativas/4)..."
                Start-Sleep -Seconds $espera
                continue
            }
            Write-Warning "  falha ao baixar foto ($Label): $($_.Exception.Message) -- vai usar fundo solido."
            return $null
        }
    }
    return $null
}

# ---------------------------------------------------------------------------
$built = @()
foreach ($def in $PostDefs) {
    $dataPath = Join-Path $PSScriptRoot $def.File
    if (-not (Test-Path $dataPath)) {
        Write-Warning "Rascunho nao encontrado: $($def.File) -- pulando post '$($def.Key)'."
        continue
    }
    $post = Get-Content $dataPath -Raw -Encoding UTF8 | ConvertFrom-Json

    $postDir   = Join-Path $DayDir $def.Folder
    $htmlDir   = Join-Path $postDir "_html"
    $assetsDir = Join-Path $postDir "_assets"
    $outDirName = if ($def.Key -eq 'frase') { "imagem" } else { "slides" }
    $outDir    = Join-Path $postDir $outDirName

    foreach ($d in @($htmlDir, $assetsDir, $outDir)) {
        if (Test-Path $d) { Remove-Item $d -Recurse -Force }
        New-Item -ItemType Directory -Force -Path $d | Out-Null
    }

    $legendaCompleta = $post.legenda.TrimEnd() + "`n`n" + ($post.hashtags -join ' ')
    [System.IO.File]::WriteAllText((Join-Path $postDir "legenda.txt"), $legendaCompleta, [System.Text.UTF8Encoding]::new($false))
    Copy-Item $dataPath (Join-Path $postDir "data.json") -Force

    Write-Host "== $($def.Folder) =="

    if ($def.Key -eq 'alerta') {
        # alerta e' sempre FOTO -- ignora "formato" no rascunho, se vier
        if ($post.formato -and $post.formato -ne 'foto') {
            Write-Warning "post-1-alerta.json pede '$($post.formato)', mas alerta e' sempre 'foto'."
        }
        $total = $post.slides.Count
        $idx = 0
        foreach ($s in $post.slides) {
            $idx++
            $idxLabel = "{0:D2} / {1:D2}" -f $idx, $total
            $photo = Get-Photo -Url $s.photo_url -Dest (Join-Path $assetsDir "slide-$($s.id).jpg") -Label "slide-$($s.id)"
            $inline = if ($photo) { "background-image:url('../_assets/slide-$($s.id).jpg');" } else { "" }
            $inner = @"
    <div class="scrim"></div>
    <span class="topbar">$(Esc $s.topbar)</span>
    <div class="content">
      <div class="headline">$(Esc $s.title)</div>
      <div class="body-txt">$(Esc $s.body)</div>
    </div>
    <span class="handle">$Handle &middot; $idxLabel</span>
$LogoHtml
"@
            Write-SlideHtml -SlideClass "fmt-foto" -Css (Get-AlertaCss) -Inner $inner -InlineStyle $inline `
                -OutputPath (Join-Path $htmlDir "slide-$($s.id).html")
        }
        $semFoto = @($post.slides | Where-Object { -not $_.photo_url }).Count
        if ($semFoto -gt 0) { Write-Warning "$semFoto slide(s) sem photo_url -- vao sair com fundo solido." }
        Write-Host "  $total slides [foto]"

    } elseif ($def.Key -eq 'frase') {
        $photo = Get-Photo -Url $post.photo_url -Dest (Join-Path $assetsDir "fundo.jpg") -Label "fundo"
        $inline = if ($photo) { "background-image:url('../_assets/fundo.jpg');" } else { "" }
        $fonteHtml = if ($post.fonte) { "<div class=`"fonte`">$(Esc $post.fonte)</div>" } else { "" }
        $inner = @"
    <div class="scrim"></div>
    <span class="topbar">$(Esc $post.topbar)</span>
    <div class="content">
      <div class="mark">&ldquo;</div>
      <div class="headline">$(Esc $post.frase)</div>
      <div class="rule"></div>
      <div class="autor">$(Esc $post.autor)</div>
      $fonteHtml
    </div>
    <div class="footer-row"><span class="handle">$Handle</span></div>
$LogoHtml
"@
        Write-SlideHtml -SlideClass "fmt-frase" -Css (Get-FraseCss) -Inner $inner -InlineStyle $inline `
            -OutputPath (Join-Path $htmlDir "post.html")
        Write-Host "  1 imagem"

    } else {
        # radar
        $total = $post.slides.Count
        $idx = 0
        foreach ($s in $post.slides) {
            $idx++
            $idxLabel = "{0:D2} / {1:D2}" -f $idx, $total
            $fonteTxt = if ($s.fonte) { "FONTE: $(Esc $s.fonte)" } else { "" }
            $miolo = @"
    <div class="topbar"><span class="tag">$(Esc $s.tag)</span><span class="data">$DateLabel</span></div>
    <div class="content">
      <div class="headline">$(Esc $s.title)</div>
      <div class="body-txt">$(Esc $s.body)</div>
    </div>
    <div class="footer-row">
      <div class="fonte">$fonteTxt</div>
      <div class="rule"></div>
      <div class="meta"><span>$Handle &middot; $idxLabel</span></div>
    </div>
"@
            if ($s.layout -eq 'foto') {
                $foto = Get-Photo -Url $s.photo_url -Dest (Join-Path $assetsDir "slide-$($s.id).jpg") -Label "slide-$($s.id)"
                $estiloFoto = if ($foto) { " style=`"background-image:url('../_assets/slide-$($s.id).jpg');`"" } else { "" }
                $inner = @"
    <div class="foto"$estiloFoto></div>
    <div class="painel">
$miolo
    </div>
$LogoHtmlDark
"@
                $classe = "fmt-radar-foto"
            } else {
                $inner = "$miolo$LogoHtmlDark"
                $classe = "fmt-radar"
            }
            Write-SlideHtml -SlideClass $classe -Css (Get-RadarCss) -Inner $inner -InlineStyle "" `
                -OutputPath (Join-Path $htmlDir "slide-$($s.id).html")
        }
        $nFotoN = @($post.slides | Where-Object { $_.layout -eq 'foto' }).Count
        Write-Host "  $total slides [editorial + $nFotoN com foto]"
    }

    $built += $def.Folder
}

if ($built.Count -eq 0) { throw "Nenhum post foi gerado -- verifique os rascunhos em scripts/." }

Write-Host "`nPosts montados: $($built -join ', ')"
$DayDir
