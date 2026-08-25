"""
Gera a capa de um Reels, na mesma linguagem visual do post FRASE
(scripts/generate-posts.ps1: Get-BaseCss + Get-FraseCss), adaptada para o
quadro vertical 1080x1920 do proprio Reels (em vez do 1080x1350 dos outros
posts). Nao altera generate-posts.ps1 -- e' um gerador a parte pro mesmo
padrao visual, porque capa de Reels e' um tipo de artefato novo.

Handle e cor de destaque vem de scripts/config.json, nao sao fixos no
codigo -- unico lugar onde precisam ser trocados se a marca mudar.

Uso: python gerar_capa.py <pasta_do_reel> <topbar> <titulo> <foto_gancho.jpg>
A pasta do reel deve conter legenda.txt/data.json (mesma pasta do video.mp4).
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[2]
FONTS_DIR = REPO_ROOT / "scripts" / "fonts"
LOGO_PATH = REPO_ROOT / "scripts" / "brand" / "logo.png"
CONFIG = json.loads((REPO_ROOT / "scripts" / "config.json").read_text(encoding="utf-8"))
HANDLE = CONFIG["handle"]
ACCENT = CONFIG.get("accent_color", "#00D9FF")

CSS_BASE = f"""
  @font-face{{ font-family:'Inter'; font-weight:400; src:url('{(FONTS_DIR / 'Inter-Regular.ttf').as_uri()}') format('truetype'); }}
  @font-face{{ font-family:'Inter Black'; font-weight:900; src:url('{(FONTS_DIR / 'Inter-Black.ttf').as_uri()}') format('truetype'); }}
  @font-face{{ font-family:'JetBrains Mono'; font-weight:700; src:url('{(FONTS_DIR / 'JetBrainsMono-Bold.ttf').as_uri()}') format('truetype'); }}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  html,body{{width:1080px;height:1920px;overflow:hidden;}}
  .slide{{
    width:1080px;height:1920px;position:relative;overflow:hidden;
    font-family:'Inter',sans-serif;
    display:flex;flex-direction:column;justify-content:space-between;
    padding:120px 84px 96px;
    background-color:#08080A;
    background-size:cover;background-position:center;background-repeat:no-repeat;
  }}
  .content{{ display:flex; flex-direction:column; flex:1; justify-content:center; }}
  .scrim{{ position:absolute; inset:0;
    background:linear-gradient(180deg, rgba(0,0,0,.82) 0%, rgba(0,0,0,.55) 30%, rgba(0,0,0,.62) 60%, rgba(0,0,0,.94) 100%); }}
  .topbar, .content, .footer-row {{ position:relative; z-index:1; }}
  .topbar{{ font-family:'JetBrains Mono',monospace; font-size:34px; letter-spacing:0.16em;
    text-transform:uppercase; color:{ACCENT}; display:inline-block; }}
  .reelbadge{{ font-family:'JetBrains Mono',monospace; font-size:26px; letter-spacing:0.14em;
    text-transform:uppercase; color:rgba(255,255,255,.75); background:rgba(0,0,0,.55);
    padding:10px 22px; border-radius:999px; border:1px solid rgba(255,255,255,.25); }}
  .headline{{ font-family:'Inter Black','Inter',sans-serif; font-weight:900; font-size:124px;
    line-height:1.02; letter-spacing:-0.02em; text-transform:uppercase; color:#fff;
    text-shadow:0 4px 28px rgba(0,0,0,.85); margin-top:40px; }}
  .rule{{ width:110px; height:8px; background:{ACCENT}; margin-top:46px; }}
  .footer-row{{ display:flex; justify-content:space-between; align-items:flex-end; }}
  .handle{{ font-family:'JetBrains Mono',monospace; font-size:34px; color:rgba(255,255,255,.65); }}
  .brandmark{{ position:absolute; right:84px; bottom:96px; height:58px; width:auto; opacity:.95; z-index:2; }}
"""

FIT_SCRIPT = """
  <script>
    (function(){
      var slide = document.querySelector('.slide');
      var headline = document.querySelector('.headline');
      if (!slide || !headline) { document.body.setAttribute('data-fit-done','1'); return; }
      var size = parseFloat(getComputedStyle(headline).fontSize);
      while (headline.scrollWidth > headline.clientWidth + 1 && size > 56) {
        size -= 4; headline.style.fontSize = size + 'px';
      }
      var hs = parseFloat(getComputedStyle(headline).fontSize);
      var guard = 0;
      while (slide.scrollHeight > slide.clientHeight + 1 && guard < 50 && hs > 56) {
        hs -= 4; headline.style.fontSize = hs + 'px'; guard++;
      }
      document.body.setAttribute('data-fit-done','1');
    })();
  </script>
"""

def build_html(topbar: str, titulo: str, foto_path: Path) -> str:
    bg = f"background-image:url('{foto_path.as_uri()}');" if foto_path.exists() else ""
    logo_html = f'<img class="brandmark" src="{LOGO_PATH.as_uri()}" alt="">' if LOGO_PATH.exists() else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><style>{CSS_BASE}</style></head>
<body>
  <div class="slide" style="{bg}">
    <div class="scrim"></div>
    <div class="topbar" style="display:flex;justify-content:space-between;width:100%;">
      <span>{topbar}</span>
      <span class="reelbadge">&#9654; REELS</span>
    </div>
    <div class="content">
      <div class="headline">{titulo}</div>
      <div class="rule"></div>
    </div>
    <div class="footer-row">
      <span class="handle">{HANDLE}</span>
    </div>
    {logo_html}
  </div>
  {FIT_SCRIPT}
</body>
</html>"""

def main():
    if len(sys.argv) != 5:
        print("Uso: gerar_capa.py <pasta_do_reel> <topbar> <titulo> <foto_gancho>")
        sys.exit(1)
    pasta_reel = Path(sys.argv[1]).resolve()
    topbar, titulo, foto = sys.argv[2], sys.argv[3], Path(sys.argv[4]).resolve()

    html_path = pasta_reel / "_work" / "capa.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(build_html(topbar, titulo, foto), encoding="utf-8")

    out_path = pasta_reel / "capa.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        page.goto(html_path.as_uri())
        page.wait_for_function("document.fonts.status === 'loaded'")
        page.wait_for_function("document.body.getAttribute('data-fit-done') === '1'")
        page.screenshot(path=str(out_path))
        browser.close()
    print(f"Capa gerada: {out_path}")

if __name__ == "__main__":
    main()
