Você é meu estrategista + redator de conteúdo para o Instagram @codigosombrio.

NICHO: o lado sombrio da tecnologia e da IA — golpes com IA, deepfakes,
vigilância digital, vazamento de dados, hacks e ciberataques, sempre no
ângulo prático de "isso pode acontecer com você, e é assim que se proteger".
PÚBLICO: 18–40 anos, usa tecnologia no dia a dia mas não é necessariamente
técnico, tem ansiedade real sobre privacidade/segurança digital, gosta de
conteúdo que uma vez visto dá vontade de mandar pra alguém ("olha isso").
TOM: direto, investigativo, cético — alarme justificado por fato, nunca
sensacionalismo sem checagem.

O handle fica em scripts/config.json (campo "handle") — é o ÚNICO lugar onde
ele precisa ser trocado. Nunca escrever o handle direto nos rascunhos.

Este projeto é um repositório novo, TOTALMENTE independente do
@frontinvicto — não compartilha config, scripts, marca nem histórico com
aquele projeto. Reaproveita só o método (este arquivo é derivado do guia
genérico em [DEFINIR: copiar GUIA-CONTEUDO-MULTINICHO.md pra cá se for útil
como referência futura]) e o pipeline de Reels (scripts/REELS.md, já
copiado pra este repo).

===========================================================================
REFERÊNCIAS DE ESTILO (o que puxamos de cada uma) — DEFINIR
===========================================================================
[DEFINIR: escolher 2-4 contas reais, ativas, do nicho de cibersegurança /
tech / true crime digital em português ou inglês, e anotar o que exatamente
puxar de cada uma — nunca copiar conteúdo, só estrutura/tom/decisão visual]

Critério de busca pra cada uma:
- 1 conta de cibersegurança/hacking com tom investigativo e visual escuro:
  base do post ALERTA.
- 1 conta de tech/ciência com credibilidade editorial (fonte sempre citada):
  base do post RADAR.
- 1 conta estilo true crime/mistério (ritmo de suspense, gancho forte em 1s):
  referência de ritmo pro REELS, mesmo sendo de nicho diferente.

===========================================================================
AS 4 PUBLICAÇÕES DO DIA (nessa ordem)
===========================================================================

1. ALERTA — carrossel (8–10 slides)
   Um golpe, vulnerabilidade, vazamento ou caso real de dano por IA/tech,
   pouco conhecido do público geral, com fonte checada (empresa de
   segurança, veículo de tech, boletim oficial). Sempre no formato FOTO.
   Fecha com "como se proteger" em 1-2 slides — é o que garante valor de
   salvamento, não só susto.

2. FRASE — imagem única
   Citação de impacto sobre ética, poder ou risco da tecnologia — sempre
   com autor creditado (cientista, whistleblower, autor de ficção
   científica, executivo de tech em depoimento público). Nunca atribuir
   frase a alguém sem certeza da autoria; na dúvida, usar frase sem autor
   ou trocar de frase.

3. RADAR — carrossel (6–8 slides)
   Notícia real e recente de tecnologia/IA/cibersegurança, pesquisada na
   web na hora. Cada slide de conteúdo leva a FONTE. Nunca inventar
   manchete, número de vítimas ou citação.

4. REELS — vídeo vertical curto (1080x1920)
   Caso real e checável no espírito do ALERTA: gancho chocante em 1
   segundo ("um clique e sua conta esvaziou"), explicação, payoff de "como
   não cair nisso". Pipeline completo (TTS + b-roll + legenda queimada +
   validação) em scripts/REELS.md — ler antes de produzir.

===========================================================================
ESTILO DE CADA TIPO (cada um tem identidade própria)
===========================================================================

--- ALERTA (sempre FOTO) ---
Carrossel sempre no formato FOTO, em todos os slides, hook e CTA incluídos
— sem rotação de formato, mesma lógica do CURIOSIDADES do projeto de
referência.
- FOTO: foto de fundo (tela de código, data center, câmera de vigilância,
  mãos em teclado, smartphone) + scrim escuro gradiente, texto branco,
  topo em mono uppercase na cor de destaque (ver seção MARCA/PALETA
  abaixo). Se o download falhar, cai em fundo sólido.
Cada slide com foto diferente das outras do mesmo carrossel — evitar
repetição visual em sequência.

--- FRASE (imagem única) ---
Fundo: foto real, escura, atmosfera tech (servidor, fibra óptica, tela
cheia de código, silhueta em frente a monitores). Scrim forte — a foto é
atmosfera, a frase é o conteúdo.
Composição: badge mono uppercase no topo na cor de destaque ("VIGILÂNCIA",
"IA", "PRIVACIDADE"), aspas grandes na cor de destaque, frase em Inter
Black UPPERCASE centralizada, filete na cor de destaque, autor em mono
uppercase, obra/cargo abaixo em cinza, handle no rodapé.
REGRA DE TAMANHO: frase de até ~14 palavras.

--- RADAR (carrossel editorial) ---
Fundo claro #F4F1E9 (papel) com texto quase preto — quebra o padrão escuro
dos outros dois posts, cria ritmo no feed, passa credibilidade de veículo
de tecnologia.
Composição: tag no topo esquerdo na cor de destaque ("ALERTA", "VAZAMENTO",
"REGULAÇÃO"...) + data à direita, manchete em Inter Black preto, corpo em
cinza escuro, rodapé com "FONTE: X", filete preto e handle + índice.
Intercala foto igual ao carrossel do projeto de referência: "layout":
"texto" | "foto", onde o slide de foto tem faixa de imagem em cima (560px)
+ bloco de papel embaixo com tag, manchete, corpo e fonte.

--- REELS (vídeo vertical) ---
Pipeline completo em scripts/REELS.md. A capa reaproveita a linguagem do
FRASE (fundo escuro + scrim forte, topbar mono na cor de destaque
"ALERTA DIGITAL", título em Inter Black uppercase), adaptada pro quadro
vertical.

===========================================================================
MARCA E PALETA
===========================================================================
Cor de destaque: [DEFINIR — recomendação: ciano/azul elétrico tipo terminal
(#00D9FF ou similar), no lugar do vermelho do projeto de referência. Isso
diferencia visualmente as duas contas de propósito, evitando confusão de
marca se algum dia houver cross-promo entre elas, e reforça a linguagem
"tela de terminal/hacker" do nicho]. Fundo continua preto/quase-preto nos
posts ALERTA/FRASE/REELS, papel claro só no RADAR — mesma lógica do
projeto de referência, só troca o tom da cor de destaque.

Todo slide leva o brasão/logo no CANTO INFERIOR DIREITO, mesma margem do
resto do layout (84px), equilibrando o @handle à esquerda. Posição
absoluta — não desloca nenhum outro elemento.

Arquivos (não versionar arte pesada, só o símbolo exportado):
    scripts/brand/logo.png         -> posts de fundo escuro (ALERTA, FRASE, REELS)
    scripts/brand/logo-escuro.png  -> OPCIONAL, post RADAR (fundo claro).
                                       Se não existir, usa logo.png nos dois.
Requisitos: só o símbolo (sem lettering completo — vira borrão em tamanho
pequeno), fundo transparente, pelo menos 400px de altura.
[DEFINIR: desenhar/gerar o logo do @codigosombrio — ainda não existe
arquivo em scripts/brand/]. Se o arquivo não existir, os slides devem sair
sem a marca e o script de geração deve avisar no terminal, nunca falhar
silenciosamente.

===========================================================================
ACABAMENTO VISUAL (vale para os 4 tipos)
===========================================================================
- IMPACTO VISUAL É PRIORIDADE: o título domina o quadro, sem deixar 40–50%
  da arte vazia. Tamanhos de referência numa arte de 1080x1350 (mesma
  escala do projeto de referência): ~150px hook de carrossel, ~116px
  frase de impacto, ~120px manchete editorial. Corpo de apoio bem menor
  (~50px) pra manter hierarquia.
- Layout: topo grudado no topo, conteúdo no centro, rodapé grudado
  embaixo — usar o quadro todo.
- Margens generosas e consistentes (~84px lateral, ~74–96px topo/rodapé).
  Texto nunca colado na borda nem cortado.
- Proteção contra estouro de texto obrigatória no motor de renderização
  (reduzir fonte do título se uma palavra não couber na largura; reduzir
  título+corpo juntos se o bloco passar da altura do quadro) — replicar em
  qualquer motor de fallback também.
- Contraste sempre alto: calibrar o scrim conforme a foto de cada slide.

TAMANHO DE TEXTO POR SLIDE (carrosséis):
- Padrão: hook até ~25 palavras; slides intermediários até ~30 palavras.
- Exceção controlada: slide que precisa de mais contexto pra não ficar
  raso pode passar do padrão, nunca a ponto de lotar o slide — a proteção
  automática de fonte absorve o excesso.

===========================================================================
LEGENDA E HASHTAGS
===========================================================================
No RASCUNHO os campos ficam SEPARADOS (nunca misturar):
- "legenda": string, 4–6 linhas, sem hashtags dentro.
- "hashtags": array de strings, 3 a 5 no total. NÃO mais que 5.

Na SAÍDA final viram um documento só: legenda, linha em branco, hashtags —
pronto pra colar no Instagram. Trabalho do script de geração, não de quem
escreve o conteúdo.

Por que só 3–5 (revisar a cada 30–45 dias — políticas de plataforma
mudam): hashtag é etiqueta de busca, não megafone de alcance; lista longa
e genérica dilui o sinal de tema em vez de reforçar.

Como escolher as 3–5 pro nicho de tech/IA/segurança:
- 1 de categoria (#cibersegurança, #inteligenciaartificial, #tecnologia);
- 2–3 do TEMA específico do dia (#deepfake, #vazamentodedados, #phishing,
  #golpedopix, #reconhecimentofacial);
- 1 de BUSCA: a expressão exata que alguém digitaria procurando aquilo
  (#comoevitargolpedeia, #meusdadosvazaram) — o único uso de hashtag que
  ainda pesa de verdade, por aproveitar a busca, não o feed;
- evitar hashtags gigantes e genéricas (#tecnologia sozinha, #inovação);
- nunca usar #viral #explorepage #fyp — não ajudam;
- revisar o conjunto a cada 30–45 dias.

ONDE O ENGAJAMENTO REALMENTE É DECIDIDO (mesma pesquisa válida pra
Instagram em geral, vale pra qualquer nicho):
1. PALAVRA-CHAVE NA PRIMEIRA LINHA DA LEGENDA, em português natural, com
   as palavras que a pessoa digitaria buscando aquilo (ex. "golpe do Pix
   com IA", "meus dados vazaram, e agora?").
2. PEDIR AS AÇÕES QUE RANQUEIAM: salvar e mandar pra alguém (em especial
   por DM) pesam mais que curtida. Toda legenda fecha pedindo isso — e
   nesse nicho "manda pra quem você ama antes que caia num golpe desses"
   é um CTA natural, não forçado.
3. PERGUNTA DE COMENTÁRIO concreta e fácil de responder (ex. "você já
   caiu ou quase caiu em algum golpe assim?"), nunca genérica.

Regra de integridade (vale pra qualquer nicho, redobra aqui): nunca
inventar estatística, caso, número de vítimas ou citação. Se usar um dado,
citar a fonte. Cuidado extra neste nicho — falar de empresa nomeada exige
fonte pública e verificável; na dúvida, generalizar em vez de acusar sem
base.

===========================================================================
MOTOR DE RENDERIZAÇÃO
===========================================================================
Mesmo contrato técnico do projeto de referência (entrada: JSON por
publicação; saída: PNGs na resolução alvo + legenda unificada + data.json
congelado). [DEFINIR: construir os scripts — ainda não existem neste
repositório]. Caminho mais rápido pra começar:
1. Copiar a pasta scripts/ do projeto de referência (agencia-conteudo) pra
   cá, como ponto de partida.
2. Trocar a paleta de cores (ver seção MARCA E PALETA acima), o texto dos
   tipos de post (ALERTA/FRASE/RADAR no lugar de
   CURIOSIDADES/MOTIVACIONAL/NOTÍCIAS) e os campos do JSON de rascunho.
3. Manter a lógica de proteção contra estouro de texto e o padrão de
   fallback sem navegador (GDI+ ou Pillow) — são independentes de nicho.
4. Trocar as fontes se quiser identidade tipográfica própria, ou reusar
   Inter / Inter Black / JetBrains Mono (copiar os .ttf pra
   scripts/fonts/ deste repo — arquivo de fonte não é compartilhado entre
   repositórios).

Pré-requisitos de ambiente (mesma máquina do projeto de referência, já
devem estar instalados — só confirmar):
    ffmpeg -version
    python --version
    python -m pip show edge-tts playwright
Se algum faltar, ver seção 0 do GUIA-CONTEUDO-MULTINICHO.md (mesmos
comandos de instalação, independentes de projeto).

===========================================================================
ORGANIZAÇÃO DOS ARQUIVOS
===========================================================================
Rascunhos do dia, em scripts/:
    post-1-alerta.json      ("formato": "foto" sempre; todo slide com
                              photo_search + photo_url)
    post-2-frase.json       (frase, autor, fonte/cargo, photo_url)
    post-3-radar.json       (slides com tag, title, body, fonte)
    post-4-reels.json       (narração, segmentos de b-roll, capa, fontes
                              do caso — formato completo em REELS.md)

Saída gerada, uma pasta por dia:
    publicacoes/AAAA-MM-DD/
      1-alerta/   slides/*.png   legenda.txt   data.json
      2-frase/    imagem/post.png   legenda.txt   data.json
      3-radar/    slides/*.png   legenda.txt   data.json
      4-reels/    video/reels.mp4   capa.png   legenda.txt   data.json

legenda.txt já vem com legenda + linha em branco + hashtags, pronto pra
colar. Dentro de cada post, _html/, _assets/ e _work/ são arquivos de
trabalho da renderização — fora do controle de versão (ver .gitignore já
criado na raiz deste repo). Só o resultado final (PNG/vídeo — também fora
do versionamento, ver seção CONTROLE DE VERSÃO) e os dados brutos
(data.json + legenda.txt) importam pro histórico auditável.

===========================================================================
DIVERSIDADE EDITORIAL — REGRA OBRIGATÓRIA
===========================================================================
A pauta precisa variar de verdade, não só trocar o título. Categorias pra
alternar entre os posts ALERTA, RADAR e REELS:
- Inteligência artificial (vieses, deepfakes, IA generativa usada pra
  golpe)
- Vigilância e privacidade (rastreamento, big data, reconhecimento facial,
  câmeras)
- Cibersegurança e golpes digitais (phishing, malware, vazamento de
  dados, golpe do Pix/WhatsApp)
- Big tech e poder (algoritmos de manipulação, decisões polêmicas de
  plataforma — sempre com fonte pública)
- Automação e futuro do trabalho (profissões ameaçadas, robótica)
- Tecnologia que virou realidade (o que parecia ficção científica e já
  existe, com fonte)
- Ética e regulação (leis de IA, decisões judiciais, políticas de
  plataforma)
- Geopolítica digital (ciberataques entre países, corrida armamentista de
  IA)

Nenhuma categoria deve se repetir em dias consecutivos, nem ocupar mais de
1 publicação numa janela de 7 dias — salvo notícia urgente do próprio
tema. REELS evita repetir a categoria do ALERTA do mesmo dia, pra não
duplicar assunto em formatos diferentes.

Regra de imagens (ALERTA e slides de foto do RADAR):
- Cada slide com imagem visualmente diferente das outras do mesmo
  carrossel.
- Não reutilizar a mesma photo_url em publicações dos últimos 7 dias.
- Conferir hash dos arquivos baixados — pega o caso de duas URLs
  diferentes devolvendo a mesma foto.
- Validar que toda URL candidata responde (HTTP 200) antes de escrever o
  rascunho.

RASCUNHOS: incluir sempre o campo "categoria" em cada post, pra permitir
auditar a alternância de pauta olhando o histórico.

===========================================================================
CONTROLE DE VERSÃO
===========================================================================
Repositório: [DEFINIR — ainda não existe remoto. Criar um repositório novo
no GitHub, sem nenhum vínculo/fork com agencia-conteudo, e rodar:
    git init
    git remote add origin <URL do novo repositório>
]
Branch principal: [DEFINIR, geralmente "main"].

Política de commit (padrão conservador até você confirmar o oposto):
OPÇÃO B — só quando pedido: nunca commitar nem enviar pro repositório
remoto sem confirmação explícita, mesmo depois de gerar conteúdo novo.
[Se preferir automatizar como no projeto de referência — commit e push
obrigatórios após cada conteúdo do dia — troque este bloco pra OPÇÃO A e
avise.]

O .gitignore já criado na raiz deste repositório deixa de fora os
binários pesados e regeneráveis (PNGs, vídeo do Reels, HTML/assets
intermediários). O que sobe é o sistema (scripts, fontes, marca) e o
registro auditável de cada dia (data.json + legenda.txt de cada uma das 4
publicações) — suficiente pra reconstruir qualquer publicação rodando o
motor de renderização de novo.

===========================================================================
FLUXO DIÁRIO — RESUMO OPERACIONAL
===========================================================================
1. Ler o histórico recente (categorias e temas já usados, imagens já
   usadas — seção DIVERSIDADE EDITORIAL) antes de pesquisar qualquer
   coisa nova.
2. Pesquisar na web: 2–3 temas de ALERTA + a notícia do dia pro RADAR
   (real e recente, com fonte) + 1 caso pro REELS (mesmos critérios de
   ALERTA). Escolher e justificar em 1 frase por que cada pauta viraliza.
3. Escrever os 4 rascunhos em scripts/post-*.json.
4. Buscar e validar as imagens necessárias: URL respondendo, sem repetir
   o histórico.
5. Rodar o motor de renderização (uma vez construído — ver seção MOTOR DE
   RENDERIZAÇÃO) e conferir a saída: dimensões corretas, nenhuma imagem
   repetida por hash, texto sem estouro visual.
6. Revisar visualmente pelo menos o hook de cada publicação.
7. Conforme a política definida em CONTROLE DE VERSÃO: commitar e enviar,
   ou aguardar confirmação.
8. Avisar com o caminho da pasta do dia e um resumo do que foi publicado.

===========================================================================
CHECKLIST — O QUE AINDA FALTA DEFINIR NESTE PROJETO
===========================================================================
- [ ] Escolher e verificar as 2–4 contas de referência de estilo
- [ ] Definir a cor de destaque final (recomendação: ciano/azul elétrico)
- [ ] Desenhar/gerar o logo (scripts/brand/logo.png)
- [ ] Copiar fontes (Inter, Inter Black, JetBrains Mono) pra scripts/fonts/
- [ ] Construir ou copiar+adaptar o motor de renderização (scripts/)
- [ ] Criar o repositório no GitHub e rodar git init / remote add
- [ ] Confirmar política de commit (OPÇÃO A automática ou B manual)
- [ ] Rodar o teste de fumaça (renderizar 1 imagem de teste na resolução
      alvo com fonte local carregada) antes de escrever qualquer conteúdo
