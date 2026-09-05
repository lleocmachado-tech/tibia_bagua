# -*- coding: utf-8 -*-
"""Gera o PDF do guia de edicao do TIBIA BAGUA."""
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether,
)
from PIL import Image as PILImage

GUIA = r"C:\dev\guia"
OUT = r"C:\Users\lleo_\OneDrive\Área de Trabalho\CODE\TIBIA BAGUA\GUIA-EDICAO.pdf"

PAGE = landscape(A4)
MARGIN = 16 * mm
USABLE_W = PAGE[0] - 2 * MARGIN

# ---------------------------------------------------------------- paleta
INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5b5b5b")
ACCENT = colors.HexColor("#8b2f2f")
BOXBG = colors.HexColor("#f4f1ec")
WARNBG = colors.HexColor("#fdf3e7")
WARNBORDER = colors.HexColor("#c98a3c")
CODEBG = colors.HexColor("#eeeae3")

ss = getSampleStyleSheet()

def st(name, **kw):
    base = dict(fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK,
                alignment=TA_LEFT, spaceAfter=6)
    base.update(kw)
    return ParagraphStyle(name, **base)

S_TITLE   = st("t",  fontName="Helvetica-Bold", fontSize=30, leading=35, spaceAfter=10)
S_SUB     = st("sb", fontSize=13, leading=18, textColor=MUTED, spaceAfter=4)
S_H1      = st("h1", fontName="Helvetica-Bold", fontSize=20, leading=25,
               textColor=ACCENT, spaceBefore=6, spaceAfter=10)
S_H2      = st("h2", fontName="Helvetica-Bold", fontSize=13.5, leading=18,
               spaceBefore=10, spaceAfter=5)
S_BODY    = st("b")
S_SMALL   = st("sm", fontSize=9, leading=12.5, textColor=MUTED)
S_CAP     = st("cap", fontSize=8.8, leading=12, textColor=MUTED, spaceAfter=2)
S_CODE    = st("code", fontName="Courier-Bold", fontSize=9.5, leading=13,
               textColor=colors.HexColor("#333333"))
S_STEP    = st("step", fontName="Helvetica-Bold", fontSize=11.5, leading=15,
               spaceBefore=8, spaceAfter=3)


IMG_W = USABLE_W * 0.93  # deixa cabecalho + texto + imagem na mesma pagina


def img(fname, width=None, caption=None):
    """Imagem escalada mantendo proporcao, centralizada."""
    path = os.path.join(GUIA, fname)
    w, h = PILImage.open(path).size
    tw = width or IMG_W
    th = tw * h / w
    im = Image(path, width=tw, height=th)
    im.hAlign = "CENTER"
    parts = [im]
    if caption:
        parts.append(Spacer(1, 3))
        cap = ParagraphStyle("capc", parent=S_CAP, alignment=TA_CENTER)
        parts.append(Paragraph(caption, cap))
    return parts


def box(text, bg=BOXBG, border=None, style=None):
    p = Paragraph(text, style or S_BODY)
    t = Table([[p]], colWidths=[USABLE_W])
    cmds = [("BACKGROUND", (0, 0), (-1, -1), bg),
            ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]
    if border:
        cmds.append(("LINEBEFORE", (0, 0), (0, -1), 3, border))
    t.setStyle(TableStyle(cmds))
    return t


def code(text):
    return box(text.replace("\\", "\\"), bg=CODEBG, style=S_CODE)


def warn(text):
    return box(text, bg=WARNBG, border=WARNBORDER)


def table(rows, widths, header=True):
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    cmds = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#d8d3cb")),
    ]
    if header:
        cmds += [("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                 ("BACKGROUND", (0, 0), (-1, 0), BOXBG),
                 ("LINEBELOW", (0, 0), (-1, 0), 0.8, MUTED)]
    t.setStyle(TableStyle(cmds))
    return t


def footer(canv, doc):
    canv.saveState()
    canv.setFont("Helvetica", 8)
    canv.setFillColor(MUTED)
    canv.drawString(MARGIN, 10 * mm, "TIBIA BAGUA - Guia de edicao de mapa e sprites")
    canv.drawRightString(PAGE[0] - MARGIN, 10 * mm, "%d" % doc.page)
    canv.setStrokeColor(colors.HexColor("#ddd8d0"))
    canv.setLineWidth(0.5)
    canv.line(MARGIN, 13 * mm, PAGE[0] - MARGIN, 13 * mm)
    canv.restoreState()


S = []
A = S.append

# =================================================================== CAPA
A(Spacer(1, 40 * mm))
A(Paragraph("Guia de edição", S_TITLE))
A(Paragraph("Mapa e sprites do seu servidor Tibia local", S_SUB))
A(Spacer(1, 6))
A(Paragraph("TIBIA BAGUA &nbsp;·&nbsp; Canary 15.25 &nbsp;·&nbsp; passo a passo com exemplos", S_SMALL))
A(Spacer(1, 14 * mm))
A(table([
    ["Ferramenta", "Para quê", "Atalho"],
    ["Canary's Map Editor 4.0", "Editar o mundo: terreno, prédios, itens, monstros e NPCs no mapa", "EDITOR-MAPA.bat"],
    ["Canary Studio", "Achar e trocar sprites, editar outfits, monstros e NPCs (.lua)", "EDITOR-SPRITE.bat"],
    ["LibreSprite 1.1", "Desenhar os pixels dos sprites", "EDITOR-SPRITE.bat"],
    ["Referência de monstros", "Descobrir o LookType (nº do outfit) de qualquer monstro ou NPC", "REFERENCIA-MONSTROS.html"],
    ["Backup / Restaurar", "Salvar e voltar atrás antes de qualquer edição", "BACKUP.bat / RESTAURAR.bat"],
], [58 * mm, 150 * mm, 55 * mm]))
A(Spacer(1, 8))
A(Paragraph(
    "Tudo roda em <b>127.0.0.1</b>. Nada é exposto para fora do computador. "
    "Este guia foi montado a partir das telas reais das ferramentas já instaladas na sua máquina.",
    S_SMALL))
A(PageBreak())

# ============================================================ COMO FUNCIONA
A(Paragraph("Antes de começar: como as peças se encaixam", S_H1))
A(Paragraph(
    "Entender isto evita 90% dos problemas. O servidor e o cliente precisam concordar sobre "
    "<b>quais itens existem e que aparência eles têm</b>. Se um lado conhece um item que o outro não conhece, "
    "o jogo quebra com erros de <i>invalid item id</i>.", S_BODY))
A(Spacer(1, 4))
A(table([
    ["Arquivo", "Onde fica", "O que é"],
    ["otservbr.otbm", "canary_run\\data-otservbr-global\\world\\", "O mundo: 184 MB de tiles, prédios e posições"],
    ["appearances.dat", "canary_run\\data\\items\\  (servidor)", "Protobuf com objetos, outfits, efeitos e missiles"],
    ["appearances-<hash>.dat", "otclient-src\\data\\things\\1525\\  (cliente)", "O MESMO arquivo do servidor (4.862.287 bytes)"],
    ["catalog-content.json", "otclient-src\\data\\things\\1525\\", "Índice que liga cada sprite ao seu spritesheet"],
    ["sprites-<hash>.bmp.lzma", "otclient-src\\data\\things\\1525\\", "Os spritesheets (4.927 arquivos, LZMA)"],
], [55 * mm, 90 * mm, 118 * mm]))
A(Spacer(1, 8))
A(box(
    "<b>Personagens e monstros são &quot;outfits&quot;.</b> Eles não são arquivos soltos: ficam dentro do "
    "<b>appearances.dat</b>, junto com os objetos. O seu servidor tem <b>1.443 outfits</b> preenchidos "
    "(de 1.949 IDs reservados). É isso que você vai editar."))
A(Spacer(1, 8))
A(Paragraph("A regra de ouro", S_H2))
A(warn(
    "<b>Editar os pixels de um outfit que já existe é seguro.</b> Você troca o desenho, o ID continua o mesmo, "
    "e servidor e cliente seguem concordando.<br/><br/>"
    "<b>Adicionar ou remover IDs é arriscado.</b> Aí você precisa atualizar o appearances.dat dos <b>dois lados</b> "
    "(cliente e servidor), senão volta o erro que impedia entrar no jogo."))
A(PageBreak())

# ================================================================ MAPA
A(Paragraph("Parte 1 — Editor de mapa", S_H1))
A(Paragraph(
    "Abra com <b>EDITOR-MAPA.bat</b>. Ele já sobe configurado: sprites 15.25, pasta de monstros e de NPCs "
    "apontando para o datapack do servidor. O mapa tem 184 MB — leva cerca de 40 segundos para abrir e "
    "ocupa ~5,8 GB de RAM.", S_BODY))
A(Spacer(1, 6))
A(Paragraph("Passo 1 — Ele já abre no templo de Thais", S_STEP))
A(Paragraph(
    "Deixei a posição inicial gravada em <b>32369, 32241, 7</b>. Por padrão o editor abria em "
    "<i>17587, 17424</i> — espaço vazio do mapa, tela toda preta, o que parece erro mas não é. "
    "Agora ele já cai direto no meio da cidade.", S_BODY))
A(Spacer(1, 4))
A(Paragraph(
    "Se um dia abrir preto de novo, é só isso: você está numa coordenada vazia. Use <b>Ctrl+G</b> "
    "(próximo passo) para voltar.", S_SMALL))
for e in img("50-rme-abre-no-templo.png", width=USABLE_W * 0.72,
             caption="Como o editor abre agora. Barra de status: x: 32369 y: 32240 z: 7."):
    A(e)
A(PageBreak())

A(Paragraph("Passo 2 — Pule para uma coordenada com Ctrl+G", S_STEP))
A(Paragraph(
    "Pressione <b>Ctrl+G</b>, digite a posição e confirme. O templo de Thais fica em "
    "<b>32369, 32241, 7</b> (X, Y, andar).", S_BODY))
for e in img("11-rme-goto-dialogo.png", width=USABLE_W * 0.82,
             caption="Ctrl+G abre o &quot;Go To Position&quot;. Os três campos são X, Y e Z (andar)."):
    A(e)
A(PageBreak())

A(Paragraph("Passo 3 — Agora sim, o mundo", S_STEP))
A(Paragraph(
    "Thais renderizada com os sprites 15.25. Repare em dois detalhes úteis da barra de status: "
    "à esquerda o item embaixo do cursor (<b>Item &quot;dirt&quot;, id: 4656</b>) e no meio a coordenada atual. "
    "É assim que você descobre o ID de qualquer coisa no mapa.", S_BODY))
for e in img("12-rme-templo.png", caption="Templo de Thais. As caixinhas de texto são placas e nomes de rua já existentes no mapa."):
    A(e)
A(PageBreak())

A(Paragraph("Exemplo prático — colocar um item no chão", S_H2))
A(Paragraph(
    "Digamos que você queira largar uma pilha de ouro perto do templo.", S_BODY))
A(Spacer(1, 3))
A(Paragraph("1. Vá até a posição com <b>Ctrl+G</b> (ex.: 32369, 32241, 7).", S_BODY))
A(Paragraph("2. Abra a paleta de itens no menu <b>View</b> e escolha a categoria.", S_BODY))
A(Paragraph("3. Selecione o item na paleta — ele vira o seu &quot;pincel&quot;.", S_BODY))
A(Paragraph("4. Clique no tile onde quer colocar. Clique com o botão direito para apagar.", S_BODY))
A(Paragraph("5. Salve com <b>Ctrl+S</b>.", S_BODY))
A(Spacer(1, 8))
A(Paragraph("Como a edição chega no jogo", S_H2))
A(warn(
    "O Canary lê o arquivo <b>.otbm</b> apenas <b>quando inicia</b>. Salvar no editor não muda o jogo que já está rodando.<br/><br/>"
    "<b>1.</b> Salve no editor (Ctrl+S) &nbsp; <b>2.</b> Feche a janela do servidor (Canary) &nbsp; <b>3.</b> Rode o <b>JOGAR.bat</b> de novo"))
A(Spacer(1, 8))
A(Paragraph("Se quebrar alguma coisa", S_H2))
A(Paragraph("Existe um backup do mapa original. Para restaurar, feche o servidor e rode:", S_BODY))
A(code('copy /Y "C:\\dev\\canary_run\\data-otservbr-global\\world\\otservbr.otbm.backup" ^<br/>'
       '        "C:\\dev\\canary_run\\data-otservbr-global\\world\\otservbr.otbm"'))
A(PageBreak())

# ================================================================ SPRITES
A(Paragraph("Parte 2 — Editor de sprites", S_H1))
A(Paragraph(
    "Abra com <b>EDITOR-SPRITE.bat</b>. Ele abre <b>dois</b> programas, porque nenhum faz o trabalho inteiro.", S_BODY))
A(Spacer(1, 4))
A(table([
    ["Programa", "O que faz", "O que NÃO faz"],
    ["Canary Studio", "Acha o outfit, exporta para PNG, importa de volta, compila os spritesheets, edita flags e .lua de monstros/NPCs",
     "Não desenha. Não tem pincel nem canvas."],
    ["LibreSprite", "Desenha os pixels, com timeline de animação",
     "Não sabe nada sobre Tibia nem sobre appearances.dat"],
], [42 * mm, 121 * mm, 100 * mm]))
A(Spacer(1, 8))
A(box(
    "<b>O ciclo é sempre este:</b><br/>"
    "Canary Studio (exporta PNG) &nbsp;→&nbsp; LibreSprite (desenha) &nbsp;→&nbsp; Canary Studio (importa e compila)"))
A(PageBreak())

A(Paragraph("Passo 1 — Apontar o Client Path", S_STEP))
A(Paragraph(
    "Na tela inicial do Canary Studio, clique em <b>Browse</b> ao lado de <b>Client Path</b>.", S_BODY))
for e in img("01-canary-studio-inicio.png",
             caption="Tela inicial. Enquanto o Client Path não estiver definido, os três editores ficam apagados."):
    A(e)
A(PageBreak())

A(Paragraph("Passo 2 — Escolher a pasta certa", S_STEP))
A(Paragraph(
    "No campo <b>Pasta:</b> escreva o caminho abaixo e clique em <b>Selecionar pasta</b>. "
    "É a <b>raiz</b>, não a subpasta <i>assets</i> — o programa procura por "
    "<i>&lt;pasta&gt;\\assets\\catalog-content.json</i>. É a mesma pasta que o editor de mapa usa.", S_BODY))
A(Spacer(1, 3))
A(code("C:\\dev\\tools\\rme-assets"))
A(Spacer(1, 6))
for e in img("02-canary-browse-dialogo.png", width=USABLE_W * 0.62,
             caption="O caminho vai no campo &quot;Pasta:&quot; embaixo."):
    A(e)
A(PageBreak())

A(Paragraph("Passo 3 — Caminho aceito, editores liberados", S_STEP))
A(Paragraph(
    "Com o Client Path preenchido, os três cartões acendem. Clique em <b>Assets editor</b>.", S_BODY))
for e in img("03-canary-path-definido.png",
             caption="Client Path definido. Agora Assets editor, Monster editor e NPC editor estão ativos."):
    A(e)
A(Spacer(1, 4))
A(box("O Client Path <b>fica salvo</b>: nas próximas vezes ele já abre preenchido e você pula direto para o Editor de Assets."))
A(PageBreak())

A(Paragraph("Passo 4 — O que tem lá dentro", S_STEP))
A(Paragraph(
    "Esta tela confirma que ele leu os seus assets de verdade. Os números batem com o servidor: "
    "<b>54.266 objetos</b>, <b>1.949 outfits</b>, 349 efeitos, 68 missiles. "
    "Embaixo aparecem ainda 812 criaturas, 438 bosses, 99 quests e 995 casas.", S_BODY))
for e in img("04-canary-assets-editor.png",
             caption="Para personagens e monstros, o que interessa é o cartão Outfits."):
    A(e)
A(PageBreak())

A(Paragraph("Passo 5 — Achar o personagem ou monstro", S_STEP))
A(Paragraph(
    "A lista de outfits vem paginada (100 por página, 15 páginas). Use <b>Search assets</b> ou "
    "<b>Jump to ID</b> se você já souber o número. Os botões que importam ficam no topo: "
    "<b>Exportar</b> e <b>Importar</b>.", S_BODY))
for e in img("05-canary-outfits.png",
             caption="Grid de outfits com os sprites reais. No topo: Jump to ID, Flags, Importar, Exportar, Duplicar, Create."):
    A(e)
A(PageBreak())

A(Paragraph("Passo 6 — Abrir o outfit", S_STEP))
A(Paragraph(
    "Clicando num outfit abre o detalhe, com quatro abas: <b>Detalhes do asset</b>, <b>Editar</b>, "
    "<b>Textura</b> e <b>Outros</b>. Em <i>Detalhes do asset</i> você vê o ID, todos os sprites do outfit "
    "(um cyclops, por exemplo, tem 36) e os <b>Grupos de Frame</b>.", S_BODY))
A(Spacer(1, 6))
for e in img("06-canary-outfit-detalhe.png", width=USABLE_W * 0.60,
             caption="Detalhe do outfit: ID, prévia e os grupos de quadros da animação."):
    A(e)
A(PageBreak())

A(Paragraph("Como achar o outfit de um monstro específico", S_H2))
A(Paragraph(
    "Se você quer editar um monstro pelo nome e não sabe o número do outfit, o caminho é este:", S_BODY))
A(Spacer(1, 3))
A(Paragraph("1. No Editor de Assets, desça até <b>World Data</b> e abra <b>criaturas</b>.", S_BODY))
A(Paragraph("2. Ache o monstro (ex.: <i>cyclops</i>) e clique nele.", S_BODY))
A(Paragraph("3. Anote o campo <b>LookType</b> — no cyclops é <b>22</b>. Esse número é o ID do outfit.", S_BODY))
A(Paragraph("4. Volte, entre em <b>Outfits</b> e use <b>Ir para ID</b> com esse número.", S_BODY))
A(Spacer(1, 6))
A(warn(
    "A tela de <b>criaturas</b> mostra dados do bestiário (dificuldade, ocorrência, LookType) e só tem o botão "
    "<b>Excluir</b>. <b>Ela não exporta sprite nenhum.</b> Ela serve para você descobrir o LookType — "
    "a edição de sprite acontece em <b>Outfits</b>."))
A(PageBreak())

A(Paragraph("Passo 7 — Exportar o PNG (aba Textura)", S_STEP))
A(Paragraph(
    "É aqui que fica a exportação: abra a aba <b>Textura</b> e use o botão <b>&#8595; PNG</b>, no canto "
    "superior direito da prévia. Os botões <b>N / L / S / O</b> trocam a direção do personagem (Norte, Leste, "
    "Sul, Oeste) e os controles <b>Addon</b> e <b>Quadro</b> percorrem os quadros da animação.", S_BODY))
A(Spacer(1, 3))
A(Paragraph("Salve os PNGs nesta pasta, que já está criada para isso:", S_BODY))
A(code("C:\\dev\\tools\\sprites-trabalho"))
A(Spacer(1, 6))
for e in img("40-canary-aba-textura.png", width=USABLE_W * 0.88,
             caption="Aba Textura do cyclops. O botão ↓ PNG (acima da prévia) é a exportação."):
    A(e)
A(PageBreak())

A(Paragraph("Passo 8 — Desenhar no LibreSprite", S_STEP))
A(Paragraph(
    "Abra o PNG exportado com <b>File &gt; Open File</b>. Um outfit tem 4 direções e vários quadros de "
    "caminhada — por isso use o menu <b>Frame</b>, que é a timeline de animação.", S_BODY))
A(Spacer(1, 3))
A(box(
    "<b>O importador aceita:</b> 32x32, 32x64, 64x32 e 64x64. Folhas maiores são fatiadas automaticamente.<br/>"
    "<b>Transparência = magenta puro (#FF00FF).</b> O que você pintar de magenta vira transparente na hora de importar."))
A(Spacer(1, 3))
A(Paragraph(
    "Dicas: <b>View &gt; Grid</b> para enxergar os limites de cada tile e zoom alto, porque o desenho é minúsculo.", S_BODY))
for e in img("20-libresprite-inicio.png", width=USABLE_W * 0.66,
             caption="LibreSprite. O menu Frame é o que você vai usar para animação."):
    A(e)
A(PageBreak())

A(Paragraph("Passo 9 — Voltar e compilar", S_STEP))
A(Paragraph(
    "De volta ao Canary Studio, no mesmo outfit:", S_BODY))
A(Spacer(1, 3))
A(Paragraph("1. Use <b>Importar</b> para trazer o PNG editado.", S_BODY))
A(Paragraph("2. Substitua os sprites do outfit (aba <b>Edit</b> / <b>Texture</b>).", S_BODY))
A(Paragraph("3. <b>Compile</b>. Este passo é o que regrava os spritesheets e o catalog-content.json.", S_BODY))
A(Paragraph("4. Feche o cliente do jogo e abra pelo <b>JOGAR.bat</b> para ver o resultado.", S_BODY))
A(Spacer(1, 8))
A(warn(
    "<b>Faça backup antes de compilar.</b> Já existem cópias do estado original:<br/>"
    "<font face='Courier'>otclient-src\\data\\things\\1525\\appearances-original.dat.backup</font><br/>"
    "<font face='Courier'>otclient-src\\data\\things\\1525\\catalog-content.json.backup</font><br/>"
    "<font face='Courier'>canary_run\\data\\items\\appearances.dat.backup</font><br/><br/>"
    "O Canary Studio está em <b>beta</b>, e o passo de compilar reescreve arquivos que o jogo depende para abrir."))
A(PageBreak())

# ============================================================== MONSTROS
A(Paragraph("Bônus — editar monstros e NPCs sem mexer em código", S_H1))
A(Paragraph(
    "As outras duas telas do Canary Studio abrem os scripts <b>.lua</b> do servidor numa interface, "
    "em vez de você editar texto na mão. Dá para mexer em vida, experiência, loot, ataques, defesas, "
    "elementos, imunidades, bestiary e bosstiary.", S_BODY))
A(Spacer(1, 4))
A(table([
    ["Tela", "Aponte para esta pasta"],
    ["Monster editor", "C:\\dev\\canary_run\\data-otservbr-global\\monster"],
    ["NPC editor", "C:\\dev\\canary_run\\data-otservbr-global\\npc"],
], [50 * mm, 213 * mm]))
A(Spacer(1, 8))
A(Paragraph(
    "Mudanças em <b>.lua</b> de monstro/NPC também só valem depois de reiniciar o servidor.", S_BODY))
A(Spacer(1, 10))
A(Paragraph("O resultado que você quer ver", S_H2))
for e in img("30-jogo-rodando.png", width=USABLE_W * 0.58,
             caption="O jogo rodando com os assets 15.25: sprites, itens, NPC e interface todos corretos."):
    A(e)
A(PageBreak())

# ====================================================== FERRAMENTAS EXTRA
A(Paragraph("Atalho — achar o LookType sem abrir nada", S_H1))
A(Paragraph(
    "Aquele vaivém de <i>abrir criaturas &rarr; achar o monstro &rarr; anotar o LookType</i> já está pronto "
    "num arquivo: dê duplo clique em <b>REFERENCIA-MONSTROS.html</b>. Ele abre no navegador, funciona "
    "offline e traz os <b>2.688</b> monstros e NPCs do seu servidor, com busca instantânea.", S_BODY))
A(Spacer(1, 4))
A(Paragraph(
    "Digite o nome (ou o próprio número) e o LookType aparece na hora. Clique em qualquer coluna para ordenar.", S_BODY))
A(Spacer(1, 5))
for e in img("60-referencia-monstros.png", width=USABLE_W * 0.76,
             caption="2.688 criaturas com LookType, classe, dificuldade, experiência, vida e o arquivo .lua de origem."):
    A(e)
A(PageBreak())

A(Paragraph("Dois detalhes úteis dessa lista", S_H2))
A(Spacer(1, 3))
A(box(
    "<b>LookType em amarelo (ex.: <i>item 516</i>)</b> quer dizer que a criatura usa a aparência de um "
    "<b>item</b>, não de um outfit. Essas não aparecem na lista de Outfits do Canary Studio — é assim mesmo. "
    "São <b>119</b> casos entre os 2.688 (outros 2.564 usam outfit; 5 não declaram aparência)."))
A(Spacer(1, 6))
A(Paragraph(
    "Monstros diferentes podem <b>compartilhar o mesmo LookType</b>. Procurando por <i>cyclops</i> você vê:", S_BODY))
A(Spacer(1, 3))
A(table([
    ["Nome", "Tipo", "LookType", "Observação"],
    ["Cyclops", "monstro", "22", "o clássico"],
    ["Animated Cyclops", "monstro", "22", "mesma aparência do Cyclops"],
    ["Juvenile Cyclops", "monstro", "22", "mesma aparência do Cyclops"],
    ["A Sweaty Cyclops", "npc", "22", "mesma aparência do Cyclops"],
    ["Cyclops Smith", "monstro", "277", "aparência própria"],
    ["Cyclops Drone", "monstro", "280", "aparência própria"],
], [55 * mm, 28 * mm, 30 * mm, 150 * mm]))
A(Spacer(1, 8))
A(warn(
    "Ou seja: redesenhar o outfit <b>22</b> muda <b>quatro</b> criaturas de uma vez — Cyclops, Animated "
    "Cyclops, Juvenile Cyclops e até o NPC A Sweaty Cyclops. Busque pelo número na lista para ver quem "
    "mais o usa antes de editar."))
A(PageBreak())

A(Paragraph("Backup e restauração em um clique", S_H1))
A(Paragraph(
    "O passo de <b>compilar</b> sprites reescreve arquivos que o jogo precisa para abrir. Antes de mexer, "
    "rode <b>BACKUP.bat</b>.", S_BODY))
A(Spacer(1, 5))
A(Paragraph("BACKUP.bat", S_H2))
A(Paragraph(
    "Cria uma cópia com data e hora em <i>C:\\dev\\backups\\</i>. Guarda o mapa, o appearances.dat do "
    "servidor, o do cliente e o catalog-content.json (~186 MB). Os 4.927 spritesheets (88 MB) são "
    "opcionais — ele pergunta, porque demora mais.", S_BODY))
A(Spacer(1, 3))
A(Paragraph("Ao final ele mostra quanto ocupou e quanto ainda resta de espaço em disco.", S_BODY))
A(Spacer(1, 8))
A(Paragraph("RESTAURAR.bat", S_H2))
A(Paragraph(
    "Lista os backups do mais novo para o mais antigo, com data, tamanho e o que cada um contém. "
    "Você digita o número e ele volta tudo.", S_BODY))
A(Spacer(1, 3))
A(Paragraph("Duas proteções embutidas:", S_BODY))
A(Spacer(1, 3))
A(Paragraph(
    "1. Se o servidor, o cliente ou algum editor estiver aberto (eles travam os arquivos), ele avisa e "
    "oferece fechar tudo antes.", S_BODY))
A(Paragraph(
    "2. Para confirmar, você precisa digitar <b>SIM</b> — assim não dá para sobrescrever sem querer.", S_BODY))
A(Spacer(1, 10))
A(box(
    "<b>Rotina recomendada:</b> BACKUP.bat &nbsp;&rarr;&nbsp; edite à vontade &nbsp;&rarr;&nbsp; teste no jogo "
    "&nbsp;&rarr;&nbsp; se algo quebrou, RESTAURAR.bat."))
A(PageBreak())

# =========================================================== REFERENCIA
A(Paragraph("Referência rápida", S_H1))
A(Paragraph("Atalhos", S_H2))
A(table([
    ["Arquivo", "O que faz"],
    ["JOGAR.bat", "Sobe MySQL, Canary e login-server, e entra no jogo com o personagem Admin"],
    ["EDITOR-MAPA.bat", "Abre o editor de mapa com otservbr.otbm, já no templo de Thais"],
    ["EDITOR-SPRITE.bat", "Abre o Canary Studio e o LibreSprite juntos"],
    ["REFERENCIA-MONSTROS.html", "Lista pesquisável: nome do monstro/NPC → LookType (nº do outfit)"],
    ["BACKUP.bat", "Snapshot com data/hora do mapa e dos assets"],
    ["RESTAURAR.bat", "Escolhe um backup da lista e volta tudo"],
], [55 * mm, 208 * mm]))
A(Spacer(1, 8))

A(Paragraph("Caminhos que você vai precisar", S_H2))
A(table([
    ["Para quê", "Caminho"],
    ["Client Path do Canary Studio", "C:\\dev\\tools\\rme-assets"],
    ["PNGs exportados (trabalho)", "C:\\dev\\tools\\sprites-trabalho"],
    ["Assets do cliente (15.25)", "TIBIA BAGUA\\otclient-src\\data\\things\\1525"],
    ["Mapa do servidor", "C:\\dev\\canary_run\\data-otservbr-global\\world\\otservbr.otbm"],
    ["Monstros (.lua)", "C:\\dev\\canary_run\\data-otservbr-global\\monster"],
    ["NPCs (.lua)", "C:\\dev\\canary_run\\data-otservbr-global\\npc"],
], [65 * mm, 198 * mm]))
A(Spacer(1, 8))

A(Paragraph("Conta do jogo", S_H2))
A(table([
    ["Conta", "Senha", "Personagem"],
    ["admin", "admin123", "Admin (level 100)"],
], [60 * mm, 60 * mm, 143 * mm]))
A(Spacer(1, 8))

A(Paragraph("Se der problema", S_H2))
A(table([
    ["Sintoma", "Causa provável e solução"],
    ["ERRO 10061 ao abrir o jogo", "O cliente abriu antes do servidor terminar de carregar. Feche tudo e rode o JOGAR.bat de novo."],
    ['Sprites errados ou "invalid item id"', "appearances.dat do cliente e do servidor deixaram de bater. Rode RESTAURAR.bat."],
    ["Mapa não mostra as mudanças", "O Canary só lê o .otbm ao iniciar. Feche o servidor e rode o JOGAR.bat."],
    ["Editor de mapa abre preto", "Coordenada vazia. Use Ctrl+G e vá para 32369, 32241, 7."],
    ["Editores apagados no Canary Studio", "O Client Path não está definido. Refaça o Passo 1 e 2."],
    ["Só aparece o botão Excluir, sem exportar", "Você está na tela de criaturas (bestiário). O sprite se edita em Outfits: anote o LookType e use Ir para ID."],
    ["Editei um outfit e mudou outro monstro", "Vários monstros dividem o mesmo LookType. Busque o número em REFERENCIA-MONSTROS.html para ver quem mais usa."],
    ["O monstro não aparece na lista de Outfits", "Ele usa aparência de item (lookTypeEx) — aparece em amarelo na referência. Esses não são editáveis como outfit."],
], [70 * mm, 193 * mm]))
A(Spacer(1, 10))
A(box(
    "Portas usadas, todas em 127.0.0.1: <b>3306</b> (MySQL) &nbsp;·&nbsp; <b>7171</b> e <b>7172</b> (Canary) "
    "&nbsp;·&nbsp; <b>8088</b> (login-server).", style=S_SMALL))

doc = SimpleDocTemplate(
    OUT, pagesize=PAGE,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=14 * mm, bottomMargin=18 * mm,
    title="TIBIA BAGUA - Guia de edicao de mapa e sprites",
    author="Guia gerado localmente",
)
doc.build(S, onFirstPage=footer, onLaterPages=footer)
print("PDF gerado:", OUT)
print("tamanho:", os.path.getsize(OUT), "bytes")
