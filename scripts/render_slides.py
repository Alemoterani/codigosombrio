import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

if len(sys.argv) < 2:
    print("Uso: render_slides.py <pasta-do-dia>")
    sys.exit(1)

day_dir = Path(sys.argv[1]).resolve()
if not day_dir.is_dir():
    print(f"Pasta nao encontrada: {day_dir}")
    sys.exit(1)

# cada subpasta de post tem _html/ e data.json ("tipo" decide a pasta de saida)
post_dirs = sorted(p for p in day_dir.iterdir() if p.is_dir() and (p / "_html").is_dir())
if not post_dirs:
    print(f"Nenhuma subpasta de post com _html/ em {day_dir}")
    sys.exit(1)

total = 0
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
    for post_dir in post_dirs:
        tipo = ""
        data_file = post_dir / "data.json"
        if data_file.exists():
            try:
                tipo = json.loads(data_file.read_text(encoding="utf-8")).get("tipo", "")
            except (json.JSONDecodeError, OSError):
                tipo = ""
        out_dir = post_dir / ("imagem" if tipo == "frase" else "slides")
        out_dir.mkdir(exist_ok=True)

        html_files = sorted((post_dir / "_html").glob("*.html"))
        if not html_files:
            print(f"[{post_dir.name}] nenhum HTML encontrado, pulando.")
            continue

        print(f"[{post_dir.name}]")
        for html_file in html_files:
            page.goto(html_file.as_uri())
            page.wait_for_function("document.fonts.status === 'loaded'")
            page.wait_for_function("document.body.getAttribute('data-fit-done') === '1'")
            out_path = out_dir / (html_file.stem + ".png")
            page.screenshot(path=str(out_path))
            print(f"  {out_dir.name}/{out_path.name}")
            total += 1
    browser.close()

print(f"\nConcluido via Playwright/Chromium ({total} imagens).")
