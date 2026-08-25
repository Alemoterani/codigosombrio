"""
Gera o Reels do dia a partir de scripts/post-4-reels.json: narracao em TTS
(edge-tts, uma unica chamada, fatiada por WordBoundary -- evita o bug de
dessincronia de concatenar varias chamadas separadas), b-roll animado
(efeito Ken Burns via FFmpeg zoompan sobre fotos reais do Wikimedia Commons
-- ver GUIA-REELS-NARRACAO-SINCRONIZADA.md pra por que uma unica chamada de
TTS e' obrigatorio), legenda queimada (ASS, blocos de ate 4 palavras,
uppercase, branco com contorno preto), card final com o logo (se existir),
e a capa (via scripts/reels-capa/gerar_capa.py).

Adaptado do projeto agencia-conteudo/@frontinvicto: la' o b-roll vem de
video de banco de imagens (Pexels, precisa de API); aqui, como as fotos
do projeto ja vem do Wikimedia Commons (sem API key), o b-roll e' gerado
animando essas mesmas fotos em vez de baixar video de outro banco.

Uso: python gerar_reels.py [AAAA-MM-DD] [caminho_do_spec.json]
Sem argumentos: usa a data de hoje e scripts/post-4-reels.json.
"""
import asyncio
import json
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
FONTS_DIR = SCRIPTS_DIR / "fonts"
LOGO_PATH = SCRIPTS_DIR / "brand" / "logo.png"


def find_ffmpeg_bins():
    winget = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    candidates = list(winget.glob("Gyan.FFmpeg*/ffmpeg-*/bin")) if winget.exists() else []
    if candidates:
        b = candidates[0]
        return str(b / "ffmpeg.exe"), str(b / "ffprobe.exe")
    return "ffmpeg", "ffprobe"


FFMPEG, FFPROBE = find_ffmpeg_bins()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"Comando falhou ({r.returncode}): {' '.join(cmd)}\n--- stderr ---\n{r.stderr[-4000:]}")
    return r.stdout


def ffprobe_duration(path):
    out = run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", str(path)])
    return float(out.strip())


def ffprobe_resolution(path):
    out = run([FFPROBE, "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(path)])
    w, h = out.strip().split("x")
    return int(w), int(h)


async def gerar_narracao(texto, voz, velocidade, mp3_path):
    communicate = edge_tts.Communicate(texto, voz, rate=velocidade, boundary="WordBoundary")
    boundaries = []
    with open(mp3_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                boundaries.append({
                    "text": chunk["text"],
                    "start_s": chunk["offset"] / 10_000_000,
                    "dur_s": chunk["duration"] / 10_000_000,
                })
    return boundaries


def reportar_pausas(boundaries, limite_s=0.55):
    for i in range(1, len(boundaries)):
        fim_anterior = boundaries[i - 1]["start_s"] + boundaries[i - 1]["dur_s"]
        gap = boundaries[i]["start_s"] - fim_anterior
        if gap > limite_s:
            print(f"  aviso: pausa de {gap:.2f}s entre '{boundaries[i-1]['text']}' e '{boundaries[i]['text']}' ({fim_anterior:.2f}s)")


def calcular_limites_segmentos(boundaries, contagens_palavras, duracao_total):
    total_esperado = sum(contagens_palavras)
    escala = len(boundaries) / total_esperado if total_esperado else 1.0
    limites = []
    acumulado = 0.0
    idx_acumulado = 0
    for n in contagens_palavras:
        idx_acumulado += n * escala
        idx = min(int(round(idx_acumulado)), len(boundaries))
        fim = boundaries[idx]["start_s"] if idx < len(boundaries) else duracao_total
        limites.append((acumulado, fim))
        acumulado = fim
    return limites


def baixar_foto(url, dest, label, tentativas=4):
    ultimo_erro = None
    for tentativa in range(1, tentativas + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "codigosombrio-content-tool/1.0 (contato: alemoterani@hotmail.com)"})
            with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
                f.write(resp.read())
            return dest
        except Exception as e:  # noqa: BLE001 -- qualquer falha de rede tenta de novo
            ultimo_erro = e
            if "429" in str(e) and tentativa < tentativas:
                espera = 8 * tentativa
                print(f"  429 (rate limit) em {label} -- esperando {espera}s (tentativa {tentativa}/{tentativas})...")
                import time
                time.sleep(espera)
                continue
            break
    raise RuntimeError(f"falha ao baixar foto ({label}): {ultimo_erro}")


def gerar_segmento_ken_burns(foto_path, duracao, saida):
    """Anima uma foto parada com zoom lento (efeito Ken Burns), 1080x1920,
    30fps, mudo -- no lugar de b-roll de video de banco de imagens pago."""
    duracao = max(duracao, 0.3)
    zoom_final = 1.16
    incremento = (zoom_final - 1.0) / max(duracao * 30, 1)
    vf = (
        "scale=1600:2844:force_original_aspect_ratio=increase,"
        "crop=1600:2844,"
        f"zoompan=z='min(zoom+{incremento:.6f},{zoom_final})':d=1:"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
        "format=yuv420p"
    )
    cmd = [
        FFMPEG, "-y", "-loop", "1", "-i", str(foto_path), "-t", f"{duracao:.3f}",
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30",
        str(saida),
    ]
    run(cmd)


def gerar_card_final(duracao, saida_png, saida_mp4, handle):
    img = Image.new("RGB", (1080, 1920), (8, 8, 10))
    draw = ImageDraw.Draw(img)
    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        alvo_h = 300
        ratio = alvo_h / logo.height
        logo = logo.resize((int(logo.width * ratio), alvo_h))
        pos = ((1080 - logo.width) // 2, 820)
        img.paste(logo, pos, logo)
    font_path = FONTS_DIR / "JetBrainsMono-Bold.ttf"
    font = ImageFont.truetype(str(font_path), 44) if font_path.exists() else ImageFont.load_default()
    bbox = draw.textbbox((0, 0), handle, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((1080 - w) // 2, 1180), handle, font=font, fill=(255, 255, 255))
    img.save(saida_png)
    cmd = [FFMPEG, "-y", "-loop", "1", "-i", str(saida_png), "-t", f"{duracao:.3f}",
           "-vf", "fps=30,format=yuv420p,setsar=1", "-an", "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "20", str(saida_mp4)]
    run(cmd)


def concatenar(clipes, saida):
    n = len(clipes)
    inputs = []
    for c in clipes:
        inputs += ["-i", str(c)]
    filtro = "".join(f"[{i}:v]" for i in range(n)) + f"concat=n={n}:v=1:a=0[outv]"
    cmd = [FFMPEG, "-y", *inputs, "-filter_complex", filtro, "-map", "[outv]",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20", str(saida)]
    run(cmd)


def ass_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def gerar_ass(boundaries, duracao_narracao, saida_ass, accent_bgr="FFD900"):
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,72,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,7,0,2,60,60,460,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    blocos = [boundaries[i:i + 4] for i in range(0, len(boundaries), 4)]
    linhas = []
    for i, bloco in enumerate(blocos):
        ini = bloco[0]["start_s"]
        if i + 1 < len(blocos):
            fim = blocos[i + 1][0]["start_s"]
        else:
            fim = duracao_narracao
        texto = " ".join(w["text"] for w in bloco).upper()
        linhas.append(f"Dialogue: 0,{ass_time(ini)},{ass_time(fim)},Default,,0,0,0,,{texto}")
    saida_ass.write_text(header + "\n".join(linhas), encoding="utf-8")


def escapar_caminho_ass(p: Path) -> str:
    return str(p).replace("\\", "/").replace(":", "\\:")


def main():
    data_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    spec_path = Path(sys.argv[2]) if len(sys.argv) > 2 else SCRIPTS_DIR / "post-4-reels.json"

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    config = json.loads((SCRIPTS_DIR / "config.json").read_text(encoding="utf-8"))
    handle = config["handle"]

    pasta = REPO_ROOT / "publicacoes" / data_str / "4-reels"
    work = pasta / "_work"
    video_dir = pasta / "video"
    work.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)

    print("== 1/6: narracao (TTS) ==")
    mp3_path = work / "narracao.mp3"
    boundaries = asyncio.run(gerar_narracao(spec["narracao"], spec["voz"], spec["velocidade"], mp3_path))
    (work / "boundaries.json").write_text(json.dumps(boundaries, ensure_ascii=False, indent=2), encoding="utf-8")
    duracao_narracao = ffprobe_duration(mp3_path)
    print(f"  narracao: {duracao_narracao:.2f}s, {len(boundaries)} palavras (TTS)")
    reportar_pausas(boundaries)

    print("== 2/6: b-roll (fotos animadas, efeito Ken Burns) ==")
    contagens = [s["palavras"] for s in spec["segmentos_video"]]
    limites = calcular_limites_segmentos(boundaries, contagens, duracao_narracao)
    seg_paths = []
    for i, (seg, (ini, fim)) in enumerate(zip(spec["segmentos_video"], limites), start=1):
        foto_path = work / f"foto{i}.jpg"
        out = work / f"seg{i}.mp4"
        print(f"  seg{i}: {ini:.2f}s-{fim:.2f}s <- {seg['descricao']}")
        baixar_foto(seg["foto_url"], foto_path, f"seg{i}")
        gerar_segmento_ken_burns(foto_path, fim - ini, out)
        seg_paths.append(out)

    print("== 3/6: card final ==")
    card_dur = spec["card_final"]["duracao_segundos"]
    card_png = work / "card.png"
    card_mp4 = work / "card.mp4"
    gerar_card_final(card_dur, card_png, card_mp4, handle)

    print("== 4/6: concatenando video mudo ==")
    video_mudo = work / "video_mudo.mp4"
    concatenar(seg_paths + [card_mp4], video_mudo)
    duracao_total = duracao_narracao + card_dur

    print("== 5/6: legendas + mux final ==")
    ass_path = work / "legendas.ass"
    gerar_ass(boundaries, duracao_narracao, ass_path)
    final_path = video_dir / "reels.mp4"
    ass_filtro = f"ass='{escapar_caminho_ass(ass_path)}'"
    cmd = [
        FFMPEG, "-y", "-i", str(video_mudo), "-i", str(mp3_path),
        "-vf", ass_filtro, "-af", "apad", "-t", f"{duracao_total:.3f}",
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
        "-c:a", "aac", "-b:a", "160k",
        str(final_path),
    ]
    run(cmd)

    print("== 6/6: capa ==")
    foto_capa = work / "foto_capa.jpg"
    baixar_foto(spec["capa"]["foto_url"], foto_capa, "capa")
    py = sys.executable
    subprocess.run([py, str(SCRIPTS_DIR / "reels-capa" / "gerar_capa.py"),
                     str(pasta), spec["capa"]["topbar"], spec["capa"]["titulo"], str(foto_capa)],
                    check=True)

    w, h = ffprobe_resolution(final_path)
    dur_final = ffprobe_duration(final_path)
    ok = (w, h) == (1080, 1920)
    print(f"\nVideo final: {final_path}  {w}x{h}  {dur_final:.2f}s  {'OK' if ok else 'RESOLUCAO INESPERADA!'}")

    print("== gravando data.json e legenda.txt ==")
    data_json = {
        "tipo": "reels",
        "categoria": spec["categoria"],
        "tema": spec["tema"],
        "viral_reason": spec["viral_reason"],
        "duracao_segundos": round(dur_final, 2),
        "narracao": {"texto": spec["narracao"], "voz": spec["voz"], "velocidade": spec["velocidade"]},
        "legendas_na_tela": "queimadas no video, sincronizadas via WordBoundary do TTS (uma unica chamada), blocos de ate 4 palavras, uppercase, estilo ASS branco com contorno preto",
        "estrutura_visual": [
            {"trecho_s": f"{ini:.2f}-{fim:.2f}", "conteudo": seg["descricao"], "fonte_foto": seg["fonte"], "commons_page": seg.get("commons_page")}
            for seg, (ini, fim) in zip(spec["segmentos_video"], limites)
        ] + [{"trecho_s": f"{duracao_narracao:.2f}-{dur_final:.2f}", "conteudo": "card de encerramento: logo (se existir) + handle sobre fundo preto", "fonte": "gerado localmente (scripts/gerar_reels.py)"}],
        "capa": {"arquivo": "capa.png", "topbar": spec["capa"]["topbar"], "titulo": spec["capa"]["titulo"],
                  "foto_gancho": spec["capa"]["fonte_foto"], "gerador": "scripts/reels-capa/gerar_capa.py"},
        "fontes_do_fato": spec["fontes_do_fato"],
        "pipeline_tecnico": {
            "narracao": "edge-tts (Python), boundary=WordBoundary para sincronismo de legenda, uma unica chamada",
            "b_roll": "fotos reais do Wikimedia Commons (licenca aberta) animadas com FFmpeg zoompan (efeito Ken Burns), sem dependencia de API de video paga",
            "legenda": "ASS gerado a partir dos timestamps, queimado com o filtro subtitles do FFmpeg",
            "video": "FFmpeg: crop+zoompan de cada segmento para 1080x1920, concat via filter_complex, mux de audio com apad para preencher o card final em silencio",
            "script": "scripts/gerar_reels.py, a partir de scripts/post-4-reels.json",
        },
        "hashtags": spec["hashtags"],
    }
    (pasta / "data.json").write_text(json.dumps(data_json, ensure_ascii=False, indent=2), encoding="utf-8")
    legenda_txt = spec["legenda"] + "\n\n" + " ".join(spec["hashtags"])
    (pasta / "legenda.txt").write_text(legenda_txt, encoding="utf-8")

    print(f"\nConcluido: {pasta}")


if __name__ == "__main__":
    main()
