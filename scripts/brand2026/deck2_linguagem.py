#!/usr/bin/env python3
"""Deck 2 - LINGUAGEM DA MARCA terceirizou 2026."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from deck_kit import *  # noqa

OUT = "artifacts/apresentacao-linguagem-terceirizou-2026.pptx"
prs = new_deck()

# 01 capa
capa(prs, "linguagem da marca",
     ["como a terceirizou", "fala, escreve e cobra."],
     "o tom, as palavras e os limites de quem fala em nome da marca. guia para o marketing e para quem atende cliente.",
     "documento de marca · v1 2026")

# 02 regra de ouro
s = blank(prs)
eyebrow(s, "a regra de ouro", "conversa")
title(s, ["falamos como quem senta", "na mesa do dono."], y=1.0, size=31, w=9.4)
txt(s, 6.9, 1.15, 5.4, 4.0,
    ["não falamos como fornecedor que manda recado.",
     "não falamos como consultor que só aponta o problema.",
     "falamos como o especialista que já viu isso antes, sabe o caminho e vai junto."], 16, GREY, ls=1.5, space=14)
card(s, 0.6, 3.55, 5.9, 1.9, fill=DARK, line=None)
txt(s, 0.95, 3.8, 5.2, 1.4,
    ["toda frase passa por um teste:",
     "“o dono da empresa entenderia isso e saberia o que fazer depois?”"], 14, WHITE, ls=1.4)
txt(s, 0.6, 5.75, 5.9, 0.8, "se a resposta for não, reescreve.", 13, ORANGE)
symbol(s)
page(s, 2)

# 03 divisor princípios
divisor(prs, "os três princípios", ["clareza, proximidade", "e autoridade."],
        "não é estilo pessoal de quem escreve. é o que a marca precisa que aconteça em qualquer canal, de post a cobrança.", n=3)

# 04 princípios detalhados
s = blank(prs)
eyebrow(s, "princípios", "bussola")
title(s, ["o que cada princípio", "obriga a fazer."], y=0.95, size=29, w=8.6)
itens = [("clareza", "frase curta, uma ideia por frase, verbo no lugar de substantivo abstrato. número quando existir número."),
         ("proximidade", "falamos com pessoa, não com cargo. “você” e “a gente”. sem tratamento cerimonioso e sem gíria de internet."),
         ("autoridade", "opinião com fundamento: o que vimos, o que o número mostra, o que costuma acontecer. nunca “achismo com convicção”.")]
x = 0.6
for i, (t, c) in enumerate(itens, 1):
    card(s, x, 2.5, 3.85, 3.2)
    txt(s, x + 0.32, 2.78, 0.8, 0.4, str(i).zfill(2), 12, ORANGE)
    txt(s, x + 0.32, 3.2, 3.2, 0.5, t, 19, DARK)
    txt(s, x + 0.32, 3.85, 3.2, 1.6, c, 13, GREY, ls=1.4)
    x += 4.07
txt(s, 0.6, 6.0, 11.6, 0.7, "quando dois princípios brigarem, a clareza ganha. sempre.", 13, ORANGE)
symbol(s)
page(s, 4)

# 05 tom de voz
s = blank(prs)
eyebrow(s, "tom de voz", "pessoas")
title(s, ["quatro traços.", "oito decisões de escrita."], y=0.95, size=29, w=8.8)
pares = [("direto", "vai ao ponto na primeira linha", "não abre com contexto longo nem agradece antes de dizer"),
         ("próximo", "fala com você, usa “a gente”", "não usa “prezado”, “venho por meio desta”, “cordialmente”"),
         ("técnico sem jargão", "traduz o termo na mesma frase", "não empilha sigla para parecer profundo"),
         ("firme", "diz o que precisa ser dito, com data", "não amacia com “talvez”, “quem sabe”, “se possível”")]
y = 2.45
for t, sim, nao in pares:
    txt(s, 0.6, y, 2.0, 0.4, t, 15, DARK)
    txt(s, 2.65, y, 4.55, 0.75, sim, 12.5, GREY, ls=1.3)
    txt(s, 7.55, y, 4.9, 0.75, nao, 12.5, LGREY, ls=1.3)
    hline(s, 0.6, y + 0.82, 11.9, LINE)
    y += 0.98
txt(s, 2.65, 2.12, 4.5, 0.3, "faz", 10.5, ORANGE)
txt(s, 7.55, 2.12, 4.5, 0.3, "não faz", 10.5, LGREY)
symbol(s)
page(s, 5)

# 06 o que nunca dizemos
s = blank(prs, "dark")
txt(s, 0.6, 1.1, 9.0, 0.3, "lista negra", 12, ORANGE)
txt(s, 0.6, 1.6, 11.0, 1.2, "o que a marca nunca diz.", 32, WHITE)
itens = ["“solução completa para sua empresa”",
         "“transforme sua gestão em 30 dias”",
         "“o melhor bpo do mercado”",
         "“parceria de sucesso” e “vestir a camisa”",
         "“reduza seus custos em até 40%” sem prova",
         "emoji em proposta, contrato e cobrança",
         "“estamos à disposição para esclarecimentos” no fim de tudo",
         "superlativo sem número atrás"]
y = 2.95
for it in itens:
    txt(s, 0.6, y, 0.35, 0.3, "×", 15, ORANGE)
    txt(s, 1.0, y, 10.6, 0.4, it, 15, WHITE)
    y += 0.47
txt(s, 0.6, 6.85, 11.0, 0.3, "quem promete tudo não é especialista em nada. e o cliente já ouviu isso de todo mundo.", 11.5, RGBColor(0x9A, 0x9B, 0x9D))
symbol(s, dark=True, h=2.0, x=11.62, y=4.75)
page(s, 6, dark=True)

# 07 estilo de escrita
s = blank(prs)
eyebrow(s, "estilo de escrita", "documento-grafico")
title(s, ["cinco hábitos que fazem", "o texto soar nosso."], y=0.95, size=29, w=9.0)
habitos = [("frase curta", "se tem duas ideias, são duas frases. ponto final resolve mais que vírgula."),
           ("verbo na frente", "“organizamos o caixa” em vez de “realizamos a organização do fluxo de caixa”."),
           ("número no lugar do adjetivo", "“7 contas, 312 lançamentos” diz mais que “grande volume”."),
           ("uma ideia por parágrafo", "três linhas é o limite confortável. texto longo só quando o assunto exige."),
           ("fecho com ação", "toda mensagem termina com o próximo passo, não com despedida.")]
y = 2.4
for i, (t, c) in enumerate(habitos, 1):
    txt(s, 0.6, y, 0.5, 0.4, str(i).zfill(2), 12, ORANGE)
    txt(s, 1.15, y - 0.04, 2.9, 0.4, t, 15, DARK)
    txt(s, 4.15, y - 0.04, 8.2, 0.7, c, 12.5, GREY, ls=1.3)
    hline(s, 0.6, y + 0.72, 11.9, LINE)
    y += 0.87
symbol(s)
page(s, 7)

# 08 léxico
s = blank(prs)
eyebrow(s, "léxico", "tag")
title(s, ["dizemos assim.", "não dizemos assado."], y=0.95, size=29, w=8.0)
cols = ["em vez de", "escrevemos"]
rows = [["bpo operacional", "operação do financeiro"],
        ["funcionário", "time, equipe"],
        ["operacionalizar", "colocar em prática"],
        ["realizar a implantação", "implantar"],
        ["cliente satisfeito", "cliente que decidiu com número"],
        ["solução sob medida", "escopo definido com você"],
        ["prestação de serviços", "quem vive de prestar serviço"],
        ["a terceirizou oferece", "a gente faz, a gente entrega"]]
tabela(s, 0.6, 2.35, 8.6, cols, rows, cw=[3.9, 4.7], rh=0.5, size=12.5)
card(s, 9.55, 2.35, 3.18, 4.1, fill=DARK, line=None)
txt(s, 9.85, 2.6, 2.6, 0.35, "regra", 11.5, ORANGE)
txt(s, 9.85, 3.0, 2.6, 3.2,
    ["palavra difícil não é sinal de competência. é ruído.",
     "se existe palavra simples, ela vence.",
     "nome de sistema e de tributo pode e deve aparecer: é o vocabulário do cliente."], 12, WHITE, ls=1.4)
symbol(s)
page(s, 8)

# 09 nuvem de palavras
s = blank(prs)
eyebrow(s, "campo semântico", "camadas")
title(s, ["as palavras que são", "nossas."], y=0.95, size=29, w=7.6)
nuvem = [("direção", 34), ("clareza", 30), ("controle", 26), ("tempo", 24), ("decisão", 32),
         ("número", 22), ("rotina", 18), ("leitura", 24), ("autonomia", 20), ("consciência", 18),
         ("mês fechado", 20), ("conciliação", 16), ("previsibilidade", 18), ("profissionalização", 16),
         ("time", 18), ("fazer acontecer", 16)]
x, y, lim = 0.6, 2.35, 7.0
for p, sz in nuvem:
    w = 0.14 * len(p) * (sz / 20.0) + 0.3
    if x + w > 0.6 + lim:
        x = 0.6
        y += 0.62
    card(s, x, y, w, 0.46, fill=(PINK if sz >= 26 else CARD), line=None, radius=50000)
    txt(s, x, y, w, 0.46, p, 11.5 if sz < 26 else 12.5, DARK if sz >= 26 else GREY,
        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    x += w + 0.12
txt(s, 8.15, 2.4, 4.6, 0.35, "e as que não são", 12, ORANGE)
txt(s, 8.15, 2.85, 4.6, 2.6,
    ["inovação disruptiva · ecossistema · sinergia · jornada · mindset · growth · escala · disruptivo · empoderamento · excelência operacional",
     "essas palavras são de outra empresa. não da nossa."], 13, GREY, ls=1.45, space=10)
symbol(s)
page(s, 9)

# 10 headline
s = blank(prs)
eyebrow(s, "como escrever título", "seta")
title(s, ["título bom carrega", "uma tensão e um caminho."], y=0.95, size=28, w=8.8)
card(s, 0.6, 2.4, 5.9, 2.2)
txt(s, 0.9, 2.6, 5.3, 0.3, "fórmula", 11, ORANGE)
txt(s, 0.9, 3.0, 5.3, 1.4,
    ["[o que dói] + [o que muda]", "ou", "[o número] + [a leitura dele]"], 17, DARK, ls=1.45)
txt(s, 0.6, 4.85, 5.9, 0.3, "exemplos que funcionam", 11, ORANGE)
txt(s, 0.6, 5.2, 5.9, 1.3,
    ["seu dinheiro sai todo mês. você sabe para onde vai?",
     "o caro não é o serviço. é a desorganização.",
     "o mês fechou. você sabe o que ele disse?"], 13, GREY, ls=1.45, space=6)
txt(s, 6.9, 4.85, 5.4, 0.3, "exemplos que não funcionam", 11, LGREY)
txt(s, 6.9, 5.2, 5.4, 1.4,
    ["gestão financeira estratégica para o seu negócio",
     "conheça nossos serviços",
     "venha ser nosso cliente"], 13, LGREY, ls=1.45, space=6)
card(s, 6.9, 2.4, 5.4, 2.2, fill=DARK, line=None)
txt(s, 7.2, 2.6, 4.8, 0.3, "regra de tamanho", 11, ORANGE)
txt(s, 7.2, 3.0, 4.8, 1.4, ["título: até 8 palavras.", "subtítulo: até 20.", "se não couber, o problema é a ideia."], 15, WHITE, ls=1.45)
symbol(s)
page(s, 10)

# 11 CTA
s = blank(prs)
eyebrow(s, "chamada para ação", "seta")
title(s, ["toda peça termina", "com um próximo passo."], y=0.95, size=29, w=8.8)
itens = [("marca", "uma conversa sobre o seu financeiro.", "site, perfil, institucional"),
         ("conteúdo", "se o seu mês fecha no escuro, o problema não é o sistema.", "post, carrossel, reel"),
         ("comercial", "vamos marcar 30 minutos e olhar o seu número.", "proposta, whatsapp, e-mail"),
         ("cliente", "o relatório fecha dia 05. preciso da conciliação até dia 03.", "rotina, cobrança")]
cols = ["onde", "como termina", "contexto"]
tabela(s, 0.6, 2.35, 12.13, cols, [[a, b, c] for a, b, c in itens], cw=[2.2, 6.4, 3.53], rh=0.72, size=12.5, bold_col0=True)
txt(s, 0.6, 5.7, 11.9, 0.9,
    ["nunca “clique aqui” sozinho. nunca “saiba mais” sem dizer mais sobre o quê.",
     "a ação tem que ser a coisa mais concreta da peça."], 13, GREY, ls=1.35)
symbol(s)
page(s, 11)

# 12 estrutura de mensagem
s = blank(prs)
eyebrow(s, "estrutura", "envelope")
title(s, ["a mensagem padrão", "tem quatro blocos."], y=0.95, size=29, w=8.4)
blocos = [("1. assunto", "contexto em uma linha. o que aconteceu ou o que precisa."),
          ("2. o pedido", "o que você precisa, com data. sem rodeio e sem justificativa longa."),
          ("3. a saída", "a solução ou o caminho que você propõe. não só o problema."),
          ("4. o fecho", "a pergunta que devolve a decisão: “consegue até quinta?”")]
y = 2.4
for t, c in blocos:
    txt(s, 0.6, y, 2.4, 0.4, t, 14.5, ORANGE)
    txt(s, 3.1, y, 9.4, 0.7, c, 13, GREY, ls=1.3)
    hline(s, 0.6, y + 0.72, 11.9, LINE)
    y += 0.88
card(s, 0.6, 6.0, 12.13, 0.85, fill=CARD, line=None)
txt(s, 0.9, 6.14, 11.5, 0.6, "vale para whatsapp, e-mail, proposta e cobrança. o que muda é o tamanho, não a ordem.", 12.5, GREY)
symbol(s)
page(s, 12)

# 13 exemplo real
s = blank(prs)
eyebrow(s, "na prática", "conversa")
title(s, ["antes e depois:", "a mesma cobrança."], y=0.95, size=28, w=8.0)
card(s, 0.6, 2.35, 5.9, 3.5, fill=None, line=LINE)
txt(s, 0.9, 2.55, 5.3, 0.3, "antes", 11, LGREY)
txt(s, 0.9, 2.95, 5.3, 2.7,
    ["“Prezados, bom dia. Venho por meio desta solicitar, se possível, que sejam verificadas as pendências financeiras referentes ao mês corrente, uma vez que não identificamos o repasse das informações necessárias para a realização dos lançamentos.”"], 12.5, LGREY, ls=1.45)
card(s, 6.85, 2.35, 5.88, 3.5, fill=DARK, line=None)
txt(s, 7.15, 2.55, 5.3, 0.3, "depois", 11, ORANGE)
txt(s, 7.15, 2.95, 5.3, 2.7,
    ["“bom dia, cris. o extrato de setembro não chegou e sem ele o fechamento não fecha.",
     "consegue mandar até quinta? se preferir, subo no drive e você anexa por lá.”"], 13, WHITE, ls=1.45)
txt(s, 0.6, 6.05, 11.9, 0.9,
    ["mesmo pedido, mesma urgência. a segunda versão tem nome, data, motivo e saída.",
     "e ainda oferece o caminho mais fácil para o cliente responder."], 12.5, GREY, ls=1.35)
symbol(s)
page(s, 13)

# 14 whatsapp
s = blank(prs)
eyebrow(s, "whatsapp", "telefone")
title(s, ["o canal mais próximo", "exige o texto mais curto."], y=0.95, size=28, w=9.0)
regras = ["uma mensagem, um assunto. se tem dois, são duas mensagens.",
          "nome da pessoa na primeira linha. sem “bom dia” solto.",
          "número, data e valor exatos. nada de “aquele valor”.",
          "áudio só quando o assunto é sensível e já existe relação.",
          "sem emoji em cobrança, contrato e assunto de dinheiro.",
          "quem recebe precisa saber o que fazer sem perguntar de volta."]
bullets(s, 0.6, 2.4, 6.6, regras, size=13, gap=0.58)
card(s, 7.6, 2.35, 5.13, 3.9, fill=CARD)
txt(s, 7.9, 2.55, 4.6, 0.3, "modelo curto", 11, ORANGE)
txt(s, 7.9, 2.95, 4.55, 3.1,
    ["“bom dia, aline.", "o fechamento de outubro fechou no centavo.",
     "faltam duas notas de serviço para encerrar o mês.",
     "consegue lançar hoje? se não, me diz o que travou e eu resolvo com o cliente.”"], 12.5, DARK, ls=1.45, space=8)
symbol(s)
page(s, 14)

# 15 apresentar número
s = blank(prs)
eyebrow(s, "falar de número", "documento-grafico")
title(s, ["o número não fala", "sozinho. a leitura é nossa."], y=0.95, size=29, w=9.2)
itens = [("o que é", "o dado, em uma frase, sem adjetivo."),
         ("o que aconteceu", "a comparação: com o mês anterior, com o previsto, com o mesmo mês do ano passado."),
         ("o que isso quer dizer", "a leitura. é aqui que a marca entrega valor."),
         ("o que fazer", "a decisão ou o teste que se propõe. com responsável e prazo.")]
x = 0.6
for i, (t, c) in enumerate(itens, 1):
    card(s, x, 2.4, 2.92, 2.9)
    txt(s, x + 0.28, 2.65, 2.4, 0.3, str(i).zfill(2), 11.5, ORANGE)
    txt(s, x + 0.28, 3.02, 2.45, 0.75, t, 14.5, DARK, ls=1.12)
    txt(s, x + 0.28, 3.85, 2.42, 1.3, c, 12, GREY, ls=1.4)
    x += 3.07
card(s, 0.6, 5.55, 12.13, 1.0, fill=DARK, line=None)
txt(s, 0.9, 5.75, 11.5, 0.7,
    "é proibido apresentar número sem dizer o que ele significa. relatório não é entrega de pdf: é conversa com pauta.", 13, WHITE)
symbol(s, dark=True, h=0.72, x=11.85, y=5.72)
page(s, 15)

# 16 assunto difícil
s = blank(prs)
eyebrow(s, "assunto difícil", "escudo")
title(s, ["falar o que precisa ser dito", "sem perder o cliente."], y=0.95, size=28, w=9.6)
passos = [("fato", "“o repasse de setembro veio 12 dias depois do combinado.”"),
          ("impacto", "“isso empurra o fechamento e o relatório que você usa para decidir.”"),
          ("regra", "“nosso prazo é dia 03. depois disso, o mês seguinte já começa atrasado.”"),
          ("saída", "“posso receber até dia 05 e recupero o calendário. ou ajustamos o dia do repasse de vez.”")]
y = 2.4
for i, (t, c) in enumerate(passos, 1):
    txt(s, 0.6, y, 1.3, 0.4, t, 12.5, ORANGE)
    txt(s, 2.0, y, 10.4, 0.7, c, 13.5, DARK, ls=1.3)
    hline(s, 0.6, y + 0.74, 11.9, LINE)
    y += 0.92
txt(s, 0.6, 6.25, 11.9, 0.6, "nunca ameaçar, nunca sumir, nunca resolver por e-mail o que precisa de conversa.", 12.5, GREY)
symbol(s)
page(s, 16)

# 17 social
s = blank(prs)
eyebrow(s, "conteúdo e social", "instagram")
title(s, ["o feed começa uma conversa.", "o direct fecha."], y=0.95, size=28, w=9.0)
card(s, 0.6, 2.4, 5.9, 3.6)
txt(s, 0.9, 2.6, 5.3, 0.3, "o que o post faz", 11, ORANGE)
txt(s, 0.9, 3.0, 5.3, 2.8,
    ["nomeia uma dor concreta do dono de prestador de serviço.",
     "mostra o número ou o mecanismo por trás dela.",
     "termina com uma ação: comentar, salvar, chamar no direct ou pedir o material.",
     "nunca termina em “siga para mais dicas”."], 12.5, GREY, ls=1.4, space=9)
card(s, 6.85, 2.4, 5.88, 3.6, fill=DARK, line=None)
txt(s, 7.15, 2.6, 5.3, 0.3, "estrutura do carrossel", 11, ORANGE)
txt(s, 7.15, 3.0, 5.3, 2.9,
    ["1. uma frase que dói.", "2. o erro que a maioria comete.", "3. o número que mostra o tamanho.",
     "4. o que muda quando está organizado.", "5. o convite para a conversa."], 12.5, WHITE, ls=1.45, space=7)
txt(s, 0.6, 6.15, 11.9, 0.6, "uma ideia por peça. post que explica tudo não é lido até o fim.", 12.5, GREY)
symbol(s)
page(s, 17)

# 18 erros
s = blank(prs)
eyebrow(s, "erros que custam caro", "alerta")
title(s, ["quatro coisas que fazem", "a marca parecer genérica."], y=0.95, size=28, w=9.4)
erros = [("falar de nós, não dele", "“somos especialistas com 20 anos de mercado” não diz nada ao dono. comece pelo problema dele."),
         ("prometer resultado sem prova", "“reduza 40% dos custos” é promessa que não se sustenta na segunda reunião."),
         ("esconder o preço", "“valores sob consulta” afasta o lead qualificado e atrai curioso."),
         ("explicar o bpo", "o cliente não quer saber o que é bpo. quer saber o que muda na segunda-feira.")]
x = 0.6
for t, c in erros:
    card(s, x, 2.45, 2.92, 3.1)
    txt(s, x + 0.28, 2.68, 0.5, 0.3, "×", 14, ORANGE)
    txt(s, x + 0.6, 2.68, 2.1, 0.75, t, 12.5, DARK, ls=1.15)
    txt(s, x + 0.28, 3.55, 2.45, 1.85, c, 11.5, GREY, ls=1.4)
    x += 3.07
symbol(s)
page(s, 18)

# 19 checklist
s = blank(prs)
eyebrow(s, "checklist", "check-circulo")
title(s, ["antes de publicar,", "passa por aqui."], y=0.95, size=29, w=8.0)
checks = ["a primeira linha diz o assunto?",
          "tem número, data ou valor concreto?",
          "cabe em menos de 8 palavras o título?",
          "diz o que a pessoa deve fazer depois?",
          "tem prova do que está sendo afirmado?",
          "alguém que não é do financeiro entende?",
          "tem palavra da lista negra?",
          "soa como alguém que senta na mesa do dono?"]
x, y = 0.6, 2.4
for i, c in enumerate(checks):
    col = 0 if i < 4 else 1
    yy = 2.4 + (i % 4) * 0.86
    xx = 0.6 + col * 6.2
    pic(s, os.path.join(ICONES, "check-circulo.png"), xx, yy + 0.02, 0.26, 0.26)
    txt(s, xx + 0.4, yy, 5.4, 0.7, c, 13, DARK, ls=1.3)
txt(s, 0.6, 6.15, 11.9, 0.6, "oito “sim” e a peça está pronta. um “não” e volta para a mesa.", 12.5, GREY)
symbol(s)
page(s, 19)

# 20 fecho
s = blank(prs, "dark")
logo(s, "horizontal-branco", 0.6, 0.55, 3.0)
txt(s, 0.6, 2.6, 10.6, 1.6, ["a marca é o que sobra", "quando a peça é esquecida."], 36, WHITE, ls=1.12)
txt(s, 0.6, 4.65, 9.6, 1.0, ["documento de linguagem · v1 · 2026",
                              "terceirização financeira consultiva · florianópolis e tubarão/sc"], 12, RGBColor(0x9A, 0x9B, 0x9D), ls=1.4)
symbol(s, dark=True, h=2.1, x=11.55, y=4.55)
page(s, 20, dark=True)

cp = prs.core_properties
cp.title = "linguagem da marca · terceirizou · 2026"
cp.author = "terceirizou"
prs.save(OUT)
print("ok", OUT, len(prs.slides), "slides")
