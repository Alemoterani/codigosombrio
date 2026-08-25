# Guia técnico: Reels narrado com legenda sincronizada

> **STATUS: AGUARDANDO APROVAÇÃO.** Este documento descreve o pipeline que
> corrigiu um bug real de dessincronia entre áudio e legenda. A correção foi
> verificada por evidência visual (frame extraído exatamente no timestamp de
> palavras-chave, comparado contra o que deveria estar na tela naquele
> instante) — mas ainda **não foi confirmada por audição humana**. Só trate
> este processo como padrão definitivo depois de assistir ao vídeo com som e
> confirmar que está correto. Até lá, use como referência, não como regra
> fechada.
>
> Copiado do projeto de referência (agencia-conteudo / @frontinvicto) em
> 2026-08-25. O conteúdo abaixo é puramente técnico (TTS, timestamps,
> FFmpeg) e não depende de nicho — nada foi alterado na cópia. A seção
> "Capa" no fim, porém, referencia a linguagem visual do MOTIVACIONAL do
> projeto original; neste projeto (@codigosombrio) a capa deve seguir a
> linguagem do post FRASE, com a cor de destaque definida em CLAUDE.md no
> lugar do vermelho.

## O bug que este guia existe para evitar

Na primeira tentativa deste pipeline, a narração foi gerada em **N chamadas
separadas** de TTS — uma por bloco/cena do roteiro — e depois concatenadas
em um único arquivo de áudio.

Isso quebrou a sincronia porque cada chamada de TTS (edge-tts, e
provavelmente qualquer motor neural de síntese) adiciona uma pausa/cauda de
silêncio **depois da última palavra**, que não aparece nos timestamps de
"word boundary" — eles só reportam onde a última palavra termina, não onde
o arquivo de áudio realmente termina. Nesse caso a cauda era de ~0,73s por
chamada.

Ao tratar "fim da última palavra" como se fosse "duração do arquivo", cada
bloco seguinte, na hora de concatenar os áudios, começava mais tarde do que
a legenda e o corte de vídeo assumiam. O erro se acumulava a cada bloco —
no quinto bloco de um roteiro de 5 partes, a defasagem real já passava de
3 segundos — e o corte final de duração (pensado pra bater o tamanho total
do vídeo) **truncou parte da fala do último bloco**.

Resultado: legenda e áudio visivelmente fora de sincronia, e um pedaço do
final da narração cortado sem aviso.

## A regra de ouro

**Gere a narração inteira do Reels em UMA ÚNICA chamada de TTS, nunca uma
por bloco/cena.** Mesmo que o roteiro tenha 5, 8 ou 10 blocos visuais
diferentes, o texto falado deve ir para o motor de TTS de uma vez só, como
uma string contínua. Os limites de cada bloco são recuperados **depois**,
fatiando a lista de timestamps de palavra pela contagem de palavras de cada
trecho do roteiro — nunca gerando trechos de áudio separados e colando-os
depois.

Isso não é só sobre economizar uma etapa: é o que garante que existe **uma
única linha do tempo**, sem nenhuma emenda de codec entre falas. Concatenar
arquivos de áudio já codificados (MP3, mesmo com `-c copy`) introduz risco
de gaps de padding/delay do codec em cada emenda — é uma classe de bug
conhecida e evitável simplesmente não fazendo a emenda.

## Pipeline passo a passo

### 1. Pré-requisitos (instalar uma vez por máquina)
- **FFmpeg** — `winget install --id Gyan.FFmpeg --source winget`
- **edge-tts** — `pip install edge-tts` (Python 3.12+; motor de TTS
  gratuito da Microsoft, sem chave de API)

Confirme com `ffmpeg -version` e `python -m pip show edge-tts` antes de
começar.

### 2. Gerar a narração inteira de uma vez
Escreva o roteiro completo como uma lista de blocos (texto de cada
bloco/cena), mas concatene todo o texto numa string única antes de mandar
pro TTS:

```python
import asyncio, json
import edge_tts

BLOCOS = [
    ("b1", "texto do bloco 1..."),
    ("b2", "texto do bloco 2..."),
    # ...
]
TEXTO_COMPLETO = " ".join(t for _, t in BLOCOS)
CONTAGEM_PALAVRAS = [len(t.split()) for _, t in BLOCOS]

async def gerar():
    communicate = edge_tts.Communicate(
        TEXTO_COMPLETO, "pt-BR-AntonioNeural", rate="+18%",
        boundary="WordBoundary",  # OBRIGATÓRIO -- sem isso não vem timestamp por palavra
    )
    boundaries = []
    with open("narracao.mp3", "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                boundaries.append({
                    "text": chunk["text"],
                    "start": chunk["offset"] / 10_000_000,
                    "end": (chunk["offset"] + chunk["duration"]) / 10_000_000,
                })
    json.dump(boundaries, open("boundaries.json", "w", encoding="utf-8"))

asyncio.run(gerar())
```

Detalhe que já causou bug antes: `boundary="WordBoundary"` precisa ser
passado explicitamente — o padrão da biblioteca é `SentenceBoundary`, que
não dá granularidade de palavra.

### 3. Recuperar os limites de cada bloco por contagem de palavras
```python
idx = 0
limites = {}
for (nome, _), n in zip(BLOCOS, CONTAGEM_PALAVRAS):
    fatia = boundaries[idx: idx + n]
    limites[nome] = {"start": fatia[0]["start"], "end": fatia[-1]["end"]}
    idx += n
```
Sempre confira que `idx` ao final bate com `len(boundaries)` — se não bater,
a tokenização do TTS separou palavras de um jeito diferente do
`texto.split()` (contrações, números, abreviações) e a fatia vai sair
errada silenciosamente.

### 4. Definir os limites de SEGMENTO DE VÍDEO (não confundir com os de fala)
Cada bloco de TTS termina numa palavra, mas o vídeo daquele bloco deve
continuar até o **início da fala do próximo bloco** — assim a pausa natural
entre frases fica dentro do clipe anterior, sem buraco visual:

```python
starts = [limites[n]["start"] for n in ordem]
seg_bounds = []
seg_start = 0.0
for i, nome in enumerate(ordem):
    seg_end = starts[i + 1] if i < len(ordem) - 1 else limites[nome]["end"] + 0.28
    seg_bounds.append((nome, seg_start, seg_end))
    seg_start = seg_end
```
O `+0.28` no último bloco é só um respiro antes do card final/CTA — ajuste
conforme o gosto, não é uma constante sagrada.

### 5. Cortar cada segmento de vídeo com a duração exata
Cada segmento vira um clipe silencioso (`-an`), na resolução alvo (ex.
1080x1920), com a duração = `seg_end - seg_start` daquele bloco. Efeitos
(zoom, cortes rápidos, grade de cor) entram aqui, por cima do corte de
duração — nunca alteram a duração calculada.

Diferenças de até ~1 frame (33ms a 30fps) entre a duração pedida e a
entregue pelo FFmpeg são normais (quantização de frame) e imperceptíveis.
Não vale a pena perseguir precisão além disso.

### 6. Montar a legenda (ASS) usando os timestamps ORIGINAIS, sem recalcular offset
Como agora existe uma única linha do tempo, os timestamps de
`boundaries.json` já estão no referencial correto — não precisa somar
offsets cumulativos manualmente (essa soma manual foi, por sinal, uma
segunda fonte de erro na primeira tentativa). Agrupe palavras em blocos de
legenda (3-5 palavras por card costuma funcionar bem), aplique destaque de
cor via `\c&HBBGGRR&` (atenção: ASS usa ordem BGR, não RGB) e escala via
`\fscx\fscy` nas palavras que o roteiro pedir.

### 7. Montar o áudio final SEM concatenar trechos de fala
```
narração completa (um único corte, do início até o fim do último bloco + respiro)
    +
card final / outro (silêncio, SFX sintetizado, etc.) -- ANEXADO uma única vez
```
Use o filtro `concat` de áudio do FFmpeg (`-filter_complex "[0:a][1:a]concat=n=2:v=0:a=1"`)
para esse único ponto de emenda, não o demuxer de concat por stream-copy —
o filtro decodifica e recodifica, evitando o problema de padding de codec
na emenda.

Se o roteiro tiver efeito sonoro sem biblioteca configurada (ex.: um "bass
drop" no card final), é possível sintetizar no próprio FFmpeg sem depender
de nenhum asset de terceiros:
```bash
ffmpeg -f lavfi -i "aevalsrc=0.9*sin(2*PI*t*(130-125*t))*exp(-4*t):s=44100:d=0.6" saida.wav
```

### 8. Concatenar vídeo, queimar legenda, fazer o mux final
1. Concatene os segmentos de vídeo (todos silenciosos) com o demuxer de
   concat (`-c copy` é seguro aqui, é vídeo puro, sem o problema de padding
   de áudio).
2. Queime a legenda com `-vf "subtitles=legendas.ass"`.
3. Confirme que a duração do vídeo concatenado bate com a duração do áudio
   final (diferença esperada: menos de 50ms, vindo só de arredondamento de
   frame).
4. Faça o mux final: vídeo + áudio, com `-t` na duração exata do vídeo pra
   garantir que não sobra nem falta nada.

### 9. VERIFICAR ANTES DE ENTREGAR — não pular esta etapa
Bater os números de duração **não é verificação suficiente** — foi assim
que o bug anterior passou despercebido até a entrega. Antes de considerar
pronto:

1. Pegue 3 a 5 palavras específicas (de preferência incluindo a **última
   palavra do roteiro inteiro**, que é onde corte por truncamento é mais
   provável de acontecer) e extraia o timestamp exato de cada uma em
   `boundaries.json`.
2. Extraia um frame do vídeo final em cada um desses timestamps:
   ```bash
   ffmpeg -ss <timestamp> -i video_final.mp4 -frames:v 1 checagem.png
   ```
3. Confira visualmente que a legenda mostrada naquele frame é exatamente a
   que contém a palavra esperada — não "uma legenda parecida", a palavra
   exata.
4. Rode `ffmpeg -i video_final.mp4 -af volumedetect -f null -` e confirme
   que `mean_volume` e `max_volume` fazem sentido (áudio não está mudo nem
   estourando) — isso não substitui ouvir, mas pega arquivo corrompido ou
   trilha ausente.
5. **Assista ao vídeo final com som antes de entregar.** A checagem por
   frame-e-timestamp é evidência forte, mas não é o mesmo que confirmar
   com o ouvido que a cadência soa natural.

## Capa (obrigatória em todo Reels)

Sempre que um Reels for criado, ele sai com uma **imagem de capa** ao lado
do vídeo — não é opcional, faz parte da entrega. A capa segue a mesma
linguagem visual dos outros posts do feed (fundo escuro, foto de gancho com
escurecimento em gradiente, tag no topo em mono uppercase na cor de
destaque do projeto, título em Inter Black branco, filete na cor de
destaque, handle e logo no rodapé), na mesma composição do post FRASE — só
que na resolução vertical 1080x1920 do próprio Reels, em vez de 1080x1350.

[DEFINIR: construir o script gerador de capa deste projeto — no projeto de
referência ele vive em scripts/reels-capa/gerar_capa.py e reaproveita as
mesmas fontes/marca/proteção de estouro de texto do resto do pipeline,
adaptadas pro quadro vertical. Copiar como ponto de partida e trocar a cor
de destaque.]

Isso grava `capa.png` na raiz da pasta do Reels (ao lado de `video/`,
`legenda.txt` e `data.json`).

Regras de conteúdo da capa:
- **Topbar**: uma tag curta de tema (ex. "ALERTA DIGITAL", "SEUS DADOS"),
  igual ao badge de categoria usado nos outros formatos.
- **Título**: o gancho do Reels resumido em uma frase curta — o mesmo
  limite dos posts FRASE (até ~14 palavras, e prefira bem menos: 6-8
  palavras rende uma capa mais limpa e escaneável como thumbnail do que o
  máximo permitido).
- **Foto de gancho**: uma foto (não um frame de vídeo) relacionada ao tema,
  buscada e validada do mesmo jeito que as fotos dos outros posts (checar
  HTTP 200 antes de usar, evitar repetir foto já usada). Frame de vídeo
  costuma sair com motion blur/compressão pior que uma foto dedicada.
- **Logo**: sempre presente, mesma posição/tamanho dos outros formatos
  (canto inferior direito).

## O que NUNCA fazer
- Gerar áudio em múltiplas chamadas de TTS (uma por bloco/cena) e depois
  concatenar os arquivos — é a causa raiz do bug que este guia documenta.
- Calcular offsets de legenda somando durações de arquivos separados
  manualmente — sempre que existir uma linha do tempo única de origem, use
  ela diretamente.
- Considerar "a duração total bateu" como prova de sincronia. Duração total
  pode bater por coincidência (ou por um corte que trunca o fim) mesmo com
  o meio inteiro dessincronizado.
- Aceitar como pronto sem alguém assistir ao resultado com áudio ligado.
