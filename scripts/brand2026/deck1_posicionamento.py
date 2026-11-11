#!/usr/bin/env python3
"""Deck 1 - POSICIONAMENTO DA MARCA terceirizou 2026."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from deck_kit import *  # noqa

OUT = "artifacts/apresentacao-posicionamento-terceirizou-2026.pptx"
prs = new_deck()

# 01 ---------------------------------------------------------------- capa
capa(prs, "posicionamento de marca", ["nosso lugar é ser",
                                      "a direção do financeiro."],
     "o que a terceirizou é hoje, para quem serve e por que isso importa antes de qualquer campanha, post ou proposta.",
     "documento de marca · v1 2026")

# 02 ---------------------------------------------------------------- como usar
s = blank(prs)
eyebrow(s, "antes de abrir", "bussola")
title(s, ["três perguntas que este documento responde."], y=1.0, size=30)
itens = [("onde a gente joga", "qual é o nosso território, contra o que competimos e o que nunca vamos ser."),
         ("com quem a gente fala", "quem é o cliente que queremos, por que ele compra e quem não é para nós."),
         ("o que sustenta a promessa", "prova, oferta, valores e a personalidade que a comunicação precisa carregar.")]
x = 0.6
for i, (t, c) in enumerate(itens, 1):
    card(s, x, 2.55, 3.85, 2.95)
    txt(s, x + 0.32, 2.85, 0.8, 0.4, str(i).zfill(2), 12, ORANGE)
    txt(s, x + 0.32, 3.28, 3.2, 0.6, t, 17, DARK, ls=1.1)
    txt(s, x + 0.32, 3.95, 3.2, 1.3, c, 13, GREY, ls=1.4)
    x += 4.07
txt(s, 0.6, 5.85, 11.6, 0.8,
    ["se este documento for bem feito, a equipe de marketing não precisa perguntar “posso falar disso?”.",
     "ela sabe o que é nosso, o que é de todo mundo e o que não é de ninguém."], 13.5, GREY, ls=1.35)
symbol(s)
page(s, 2)

# 03 ---------------------------------------------------------------- divisor
divisor(prs, "de onde viemos", ["a empresa mudou.", "o discurso ficou para trás."],
        "de 2019 para cá saímos de “terceirização do financeiro” para “direção do financeiro”. o material de venda precisa acompanhar.", n=3)

# 04 ---------------------------------------------------------------- de/para
s = blank(prs)
eyebrow(s, "o que mudou", "seta")
title(s, ["o que a terceirizou era", "e o que ela é hoje."], y=0.95, size=29, w=9.4)
cols = ["", "até 2021", "hoje, 2026"]
rows = [["categoria", "terceirização do financeiro", "terceirização financeira consultiva"],
        ["promessa", "profissionalizar a gestão", "organizar o dado e dar direção à decisão"],
        ["entrega", "rotina executada", "rotina executada, leitura gerencial e reunião de resultados"],
        ["público", "empresas em geral", "prestadores de serviço, em 8 nichos"],
        ["preço", "negociado caso a caso", "assinatura por volume de movimentações"],
        ["argumento", "substituir um funcionário", "ter um time de especialistas por menos que uma estrutura"],
        ["prova", "depoimento e confiança", "relatório, sistema, conciliação e histórico de carteira"],
        ["ambição", "atender bem", "ser a referência do segmento no sul do país"]]
tabela(s, 0.6, 2.35, 12.13, cols, rows, cw=[1.9, 4.05, 6.18], rh=0.5, size=12, bold_col0=True)
txt(s, 0.6, 6.85, 11.0, 0.4, "a mudança não é de tom. é de categoria, de entrega e de preço.", 12, ORANGE)
symbol(s)
page(s, 4)

# 05 ---------------------------------------------------------------- divisor mercado
divisor(prs, "o mercado", ["todo mundo virou bpo.", "quase ninguém virou direção."],
        "o serviço foi comoditizado por preço, por contador e por software. o espaço livre é o da leitura.", n=5)

# 06 ---------------------------------------------------------------- o que o mercado vende
s = blank(prs)
eyebrow(s, "o que está na prateleira", "camadas")
title(s, ["três jeitos de resolver o financeiro", "e o buraco que todos deixam."], y=0.95, size=28, w=10.2)
itens = [("bpo operacional", "paga conta, emite nota, manda o relatório. entrega tarefa. compete por preço e troca de fornecedor por R$ 100."),
         ("contador", "cuida do fiscal e do obrigatório. olha o passado. não entra na rotina, no caixa e na decisão do mês."),
         ("software e ia", "organiza, categoriza e acelera. não diz o que fazer com o número, nem assume a consequência da escolha.")]
x = 0.6
for t, c in itens:
    card(s, x, 2.45, 3.85, 2.5)
    txt(s, x + 0.32, 2.75, 3.2, 0.45, t, 16.5, DARK)
    txt(s, x + 0.32, 3.35, 3.2, 1.4, c, 12.5, GREY, ls=1.4)
    x += 4.07
card(s, 0.6, 5.3, 12.13, 1.25, fill=DARK, line=None)
txt(s, 0.95, 5.5, 11.3, 0.9,
    ["ninguém ocupa o lugar de quem senta do lado do dono, olha o número do mês e diz por onde começar.",
     "esse lugar está vago. é ali que a terceirizou joga."], 15, WHITE, ls=1.25)
symbol(s, dark=True, h=0.8, x=11.9, y=5.55)
page(s, 6)

# 07 ---------------------------------------------------------------- insight
s = blank(prs, "dark")
txt(s, 0.6, 1.15, 9.0, 0.3, "o que o cliente sente", 12, ORANGE)
txt(s, 0.6, 1.85, 10.9, 3.6,
    ["ele é excelente no que faz.",
     "e refém do que não sabe fazer."],
    38, WHITE, ls=1.1)
txt(s, 0.6, 5.15, 10.4, 1.1,
    ["o dono do prestador de serviço não tem problema de sistema. tem problema de leitura:",
     "não sabe se o mês fechou, não sabe de onde vem o aperto e decide no escuro."], 14.5, LGREY, ls=1.35)
symbol(s, dark=True, h=2.1, x=11.55, y=4.55)
page(s, 7, dark=True)

# 08 ---------------------------------------------------------------- matriz
s = blank(prs)
eyebrow(s, "o mapa", "caminho")
title(s, ["onde a gente está", "e onde não vale a pena estar."], y=0.95, size=29, w=9.0)
txt(s, 0.6, 2.24, 6.9, 0.3, "operação de verdade + leitura de gestão", 10.5, GREY)
matriz(s, 1.25, 2.6, 6.1, 3.55, [("bpo operacional", 0.1, 0.85), ("consultoria tradicional", 0.6, 0.85),
                                 ("contador", 0.1, 0.1), ("software", 0.6, 0.1)],
       "terceirizou", 0.74, 0.78, lx=-1.55, ly=0.16)
txt(s, 1.25, 6.24, 3.0, 0.3, "só executa", 10.5, GREY)
txt(s, 4.35, 6.24, 3.0, 0.3, "só orienta", 10.5, GREY, align=PP_ALIGN.RIGHT)
txt(s, 7.85, 2.55, 4.6, 0.4, "leitura do mapa", 13, ORANGE)
txt(s, 7.85, 3.0, 4.65, 3.6,
    ["o canto superior direito é caro de manter e tem pouca gente lá: entrega operação de verdade e leitura de gestão ao mesmo tempo.",
     "o canto inferior esquerdo é onde a concorrência briga por preço. não é nossa guerra.",
     "nosso risco não é o concorrente. é parecer igual a ele."], 13, GREY, ls=1.4, space=10)
symbol(s)
page(s, 8)

# 09 ---------------------------------------------------------------- divisor lugar
divisor(prs, "nosso lugar", ["o que a gente vende", "não é hora. é direção."],
        "a frase de posicionamento, a bandeira e a promessa andam juntas. daqui para frente, nenhuma peça sai sem elas.", n=9)

# 10 ---------------------------------------------------------------- statement
s = blank(prs)
eyebrow(s, "posicionamento", "bussola")
txt(s, 0.6, 1.55, 11.9, 3.2,
    ["somos o time de especialistas que organiza o financeiro",
     "e dá direção à decisão de quem presta serviço."],
    34, DARK, ls=1.12)
hline(s, 0.6, 4.55, 11.9, ORANGE, 2)
txt(s, 0.6, 4.85, 5.6, 1.5,
    ["posicionamento é escolha, não slogan.",
     "se a peça não deixa claro que existe leitura e direção, ela não é nossa."], 13, GREY, ls=1.4)
txt(s, 6.85, 4.85, 5.7, 1.6,
    ["o que somos: operação + leitura + decisão.",
     "o que não somos: mais um bpo, nem consultoria que só aponta."], 13, GREY, ls=1.4)
symbol(s)
page(s, 10)

# 11 ---------------------------------------------------------------- sistema de frases
s = blank(prs)
eyebrow(s, "o sistema de frases", "tag")
title(s, ["três frases, três funções.", "não trocar uma pela outra."], y=0.95, size=29, w=9.6)
blocos = [("bandeira", "terceirizar é ter mais.", "a causa. abre conversa, assina peça institucional, vive no topo da marca.", ORANGE),
          ("posicionamento", "seu financeiro organizado.\nsua decisão com direção.", "o lugar. é a frase que qualquer pessoa deve saber repetir sobre nós.", DARK),
          ("promessa de entrega", "o mês fechado, o número na mão\ne a próxima decisão encaminhada.", "o que acontece na prática. entra em proposta, onboarding e reunião.", GREY)]
y = 2.4
for tag, frase, uso, cor in blocos:
    card(s, 0.6, y, 12.13, 1.32)
    txt(s, 0.95, y + 0.2, 2.2, 0.3, tag, 11.5, ORANGE)
    txt(s, 0.95, y + 0.55, 6.6, 0.7, frase, 19, cor, ls=1.12)
    txt(s, 7.85, y + 0.35, 4.6, 0.8, uso, 12, GREY, ls=1.3)
    y += 1.47
symbol(s)
page(s, 11)

# 12 ---------------------------------------------------------------- proposito missao visao
s = blank(prs)
eyebrow(s, "o porquê", "seta-cima")
title(s, ["por que existimos, para onde vamos."], y=0.95, size=29)
itens = [("propósito", "democratizar a profissionalização das empresas.", "o motivo. não muda com o mercado."),
         ("missão", "levar informação que vira decisão para dentro da rotina de quem presta serviço.", "o trabalho. é o que fazemos todos os dias."),
         ("visão", "ser a referência nacional em terceirização financeira consultiva para prestadores de serviço.", "o horizonte. define o que recusamos crescer fazendo.")]
x = 0.6
for tag, frase, nota in itens:
    card(s, x, 2.4, 3.85, 3.35)
    txt(s, x + 0.32, 2.7, 3.2, 0.3, tag, 11.5, ORANGE)
    txt(s, x + 0.32, 3.1, 3.2, 1.75, frase, 16, DARK, ls=1.22)
    txt(s, x + 0.32, 4.95, 3.2, 0.6, nota, 11.5, GREY, ls=1.3)
    x += 4.07
txt(s, 0.6, 6.1, 11.6, 0.5, "visão sem número é intenção. o número é dos sócios, não do marketing.", 12, GREY)
symbol(s)
page(s, 12)

# 13 ---------------------------------------------------------------- valores 1
s = blank(prs)
eyebrow(s, "valores", "escudo")
title(s, ["sete valores continuam de pé.", "o que muda é como eles aparecem."], y=0.95, size=28, w=10.6)
vals = [("facilitar as coisas", "tirar do cliente o peso da rotina, não criar mais uma."),
        ("fazer acontecer", "entregar pronto, não recomendar."),
        ("agir diferente", "mudar hábito antes de mudar relatório."),
        ("somar para completar", "entrar no time, não ficar do lado de fora.")]
x = 0.6
for t, c in vals:
    card(s, x, 2.45, 2.92, 2.15)
    txt(s, x + 0.28, 2.72, 2.4, 0.55, t, 15.5, DARK, ls=1.12)
    txt(s, x + 0.28, 3.42, 2.4, 1.0, c, 12, GREY, ls=1.35)
    x += 3.07
vals2 = [("consciência que transforma", "o dono decide melhor quando entende o número."),
         ("autonomia", "executamos e informamos. a decisão é dele."),
         ("falar o que precisa ser dito", "a verdade do número, mesmo quando ela atrapalha a venda.")]
x = 0.6
for t, c in vals2:
    card(s, x, 4.8, 3.85, 1.55)
    txt(s, x + 0.28, 4.98, 3.2, 0.4, t, 14.5, DARK)
    txt(s, x + 0.28, 5.45, 3.3, 0.8, c, 11.5, GREY, ls=1.3)
    x += 4.07
symbol(s)
page(s, 13)

# 14 ---------------------------------------------------------------- bandeira
s = blank(prs, "dark")
txt(s, 0.6, 1.3, 9.0, 0.3, "a bandeira", 12, ORANGE)
txt(s, 0.6, 2.0, 11.2, 2.2, ["terceirizar", "é ter mais."], 64, WHITE, ls=1.02)
txt(s, 0.6, 4.75, 7.4, 0.9, ["mais tempo, mais leitura, mais controle, mais direção.",
                              "nunca “mais um fornecedor”."], 15, LGREY, ls=1.35)
txt(s, 8.55, 4.85, 3.9, 1.4, ["a bandeira não promete preço.", "promete o que o dinheiro do cliente compra: tempo e direção."], 12, RGBColor(0x9A, 0x9B, 0x9D), ls=1.35)
symbol(s, dark=True, h=2.1, x=11.55, y=4.55)
page(s, 14, dark=True)

# 15 ---------------------------------------------------------------- icp
s = blank(prs)
eyebrow(s, "com quem falamos", "pessoa-check")
title(s, ["prestador de serviço.", "oito nichos, um jeito de atender."], y=0.95, size=28, w=10.8)
nichos = ["casas de repouso (ilpi)", "proteção veicular", "vistoria veicular", "escritórios de arquitetura",
          "agências de marketing", "escritórios de advocacia", "clínicas de saúde e estética", "consultorias em geral"]
x, y = 0.6, 2.35
for i, n in enumerate(nichos):
    w = 2.92 if i % 4 != 3 else 2.92
    card(s, x, y, w, 0.62, radius=50000)
    txt(s, x, y, w, 0.62, n, 11.5, DARK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    x += 3.07
    if i % 4 == 3:
        x = 0.6
        y += 0.78
txt(s, 0.6, 4.35, 5.8, 0.35, "como qualificamos", 12, ORANGE)
txt(s, 0.6, 4.75, 5.8, 1.6,
    ["prestador de serviço, com receita recente, que já sente o financeiro apertar.",
     "segmento define a entrada. porte não é porta."], 13, GREY, ls=1.4)
txt(s, 6.85, 4.35, 5.8, 0.35, "quem não é nosso", 12, ORANGE)
txt(s, 6.85, 4.75, 5.8, 1.6,
    ["quem vende ou fabrica produto. quem quer crédito. quem procura o menor preço.",
     "esses três custam mais do que pagam."], 13, GREY, ls=1.4)
symbol(s)
page(s, 15)

# 16 ---------------------------------------------------------------- inegociaveis
s = blank(prs)
eyebrow(s, "inegociáveis", "chaves")
title(s, ["três coisas que a marca", "não faz por dinheiro nenhum."], y=0.95, size=29, w=10.2)
itens = [("não atendemos comércio e indústria", "nosso método foi feito para quem vive de serviço. fora disso, não entregamos o que prometemos."),
         ("não damos desconto", "desconto não é flexibilidade: é dizer que o preço era outro. quando o cliente não pode, ajustamos escopo, não valor."),
         ("não somos financeira", "não emprestamos, não antecipamos, não damos crédito. quem precisa disso não precisa de nós.")]
x = 0.6
for t, c in itens:
    card(s, x, 2.45, 3.85, 3.0)
    txt(s, x + 0.32, 2.75, 3.25, 0.95, t, 15.5, DARK, ls=1.15)
    txt(s, x + 0.32, 3.85, 3.2, 1.4, c, 12.5, GREY, ls=1.4)
    x += 4.07
txt(s, 0.6, 5.75, 11.6, 0.9,
    ["essas três regras não são rígidez comercial. são o que impede a marca de virar o que ela critica.",
     "o time de marketing pode usar isso como filtro de pauta e de lead."], 13, GREY, ls=1.35)
symbol(s)
page(s, 16)

# 17 ---------------------------------------------------------------- oferta
s = blank(prs)
eyebrow(s, "arquitetura de oferta", "cofrinho")
title(s, ["o que entra na assinatura", "e o que é projeto."], y=0.95, size=28, w=9.6)
cols = ["", "o que é", "como é vendido"]
rows = [["gestão financeira", "contas a pagar e a receber, banco, notas, boletos, conciliação e relatório mensal", "assinatura por volume de movimentações"],
        ["consultoria financeira", "leitura do resultado, análise de custo e de preço, plano de ação com o dono", "recorrente, dentro do plano"],
        ["implantação de sistema", "plano de contas, categorias, históricos e treino do time do cliente", "projeto, cobrado à parte"],
        ["mentoria de gestão", "formação do dono e do time para ler o próprio número", "projeto ou ciclo fechado"]]
tabela(s, 0.6, 2.4, 12.13, cols, rows, cw=[2.7, 6.0, 3.43], rh=0.62, size=12, bold_col0=True)
txt(s, 0.6, 6.0, 11.9, 0.8,
    ["planos por volume de R$ 299 a R$ 2.949, mais o plano personalizado acima de 300 movimentações.",
     "preço é consequência do volume, não da negociação."], 13, GREY, ls=1.35)
symbol(s)
page(s, 17)

# 18 ---------------------------------------------------------------- provas
s = blank(prs)
eyebrow(s, "razões para acreditar", "documento-grafico")
title(s, ["o discurso só vale", "se a prova estiver na mesa."], y=0.95, size=29, w=9.0)
itens = [("operação real", "seis operadoras financeiras, rotina diária, conciliação bancária e fechamento mensal."),
         ("sistema", "controlle como base: plano de contas, categorias e histórico do cliente, não planilha solta."),
         ("ritual de leitura", "relatório mensal e reunião de resultados. o número é apresentado e discutido, não enviado."),
         ("carteira", "clientes dos oito nichos, com casos de reorganização, corte de custo e recuperação de recebível.")]
x = 0.6
for t, c in itens:
    card(s, x, 2.45, 2.92, 2.85)
    txt(s, x + 0.28, 2.72, 2.4, 0.6, t, 15, DARK, ls=1.1)
    txt(s, x + 0.28, 3.45, 2.4, 1.6, c, 12, GREY, ls=1.4)
    x += 3.07
txt(s, 0.6, 5.6, 11.6, 0.8,
    "toda peça de marketing precisa de pelo menos uma dessas quatro provas. sem prova, é opinião.", 13, ORANGE)
symbol(s)
page(s, 18)

# 19 ---------------------------------------------------------------- personalidade
s = blank(prs)
eyebrow(s, "personalidade", "pessoas")
title(s, ["o conselheiro que executa.", "não o guru, não o fornecedor."], y=0.95, size=29, w=10.4)
card(s, 0.6, 2.45, 5.6, 3.5, fill=DARK, line=None)
txt(s, 0.95, 2.75, 5.0, 0.35, "arquétipo", 11.5, ORANGE)
txt(s, 0.95, 3.15, 4.95, 2.6,
    ["sábio + companheiro de time.",
     "sabe o caminho e caminha junto.",
     "fala com número, senta na mesa e põe a mão."], 17, WHITE, ls=1.35)
tracos = [("direto", "frase curta, sem rodeio, sem jargão."),
          ("técnico", "domina o assunto e traduz para quem não é do financeiro."),
          ("presente", "responde, aparece, cumpre data."),
          ("honesto", "diz o que o número mostra, mesmo quando é desconfortável.")]
y = 2.45
for t, c in tracos:
    txt(s, 6.85, y, 2.1, 0.35, t, 14.5, DARK)
    txt(s, 8.95, y, 3.7, 0.7, c, 12, GREY, ls=1.3)
    hline(s, 6.85, y + 0.68, 5.8, LINE)
    y += 0.86
symbol(s)
page(s, 19)

# 20 ---------------------------------------------------------------- manifesto
s = blank(prs, "dark")
txt(s, 0.6, 1.1, 9.0, 0.3, "manifesto", 12, ORANGE)
txt(s, 0.6, 1.6, 10.4, 4.9,
    ["terceirizar é ter mais.",
     "mais tempo para tocar o que você sabe fazer.",
     "mais clareza na hora de decidir.",
     "mais controle sobre o que entra e o que sai."], 27, WHITE, ls=1.22)
txt(s, 0.6, 5.95, 10.2, 1.0,
    "a gente não entra na empresa para virar mais um fornecedor. entra para fazer parte do time e levar profissionalização a quem vive de prestar serviço.", 12.5, LGREY, ls=1.35)
symbol(s, dark=True, h=2.0, x=11.62, y=4.7)
page(s, 20, dark=True)

# 21 ---------------------------------------------------------------- governanca
s = blank(prs)
eyebrow(s, "governança", "check-circulo")
title(s, ["como saber se o posicionamento", "está vivo ou só no papel."], y=0.95, size=28, w=10.6)
cols = ["onde olhar", "o que medir", "sinal de que está vivo"]
rows = [["discurso", "as peças repetem a mesma frase de lugar", "cliente repete a promessa sem consultar o material"],
        ["lead", "quantos chegam dizendo que querem “organizar e decidir”", "menos pedido de preço no primeiro contato"],
        ["venda", "quantas propostas fecham no preço cheio", "desconto deixa de ser assunto recorrente"],
        ["entrega", "reunião de resultados realizada no mês", "cliente chega na reunião com pergunta, não com queixa"]]
tabela(s, 0.6, 2.35, 12.13, cols, rows, cw=[2.3, 4.9, 4.93], rh=0.72, size=12, bold_col0=True)
txt(s, 0.6, 5.6, 11.9, 1.0,
    ["revisão a cada ciclo comercial, com os sócios. posicionamento não é campanha: é o que a empresa recusa fazer.",
     "quem cuida do arquivo: marketing, com aprovação de vinícius e henrique."], 12.5, GREY, ls=1.35)
symbol(s)
page(s, 21)

# 22 ---------------------------------------------------------------- fecho
s = blank(prs, "dark")
logo(s, "horizontal-branco", 0.6, 0.55, 3.0)
txt(s, 0.6, 2.5, 10.5, 1.8, ["terceirizar", "é ter mais."], 44, WHITE, ls=1.05)
txt(s, 0.6, 4.7, 9.4, 1.0,
    ["material de posicionamento · v1 · 2026",
     "terceirização financeira consultiva · florianópolis e tubarão/sc"], 12, RGBColor(0x9A, 0x9B, 0x9D), ls=1.4)
symbol(s, dark=True, h=2.1, x=11.55, y=4.55)
page(s, 22, dark=True)

cp = prs.core_properties
cp.title = "posicionamento da marca · terceirizou · 2026"
cp.author = "terceirizou"
prs.save(OUT)
print("ok", OUT, len(prs.slides), "slides")
