# -*- coding: utf-8 -*-
"""
Gera o site a partir dos arquivos de conteudo.

    python build.py

Le  conteudo/*.md  e escreve  index.html, criterios.html  e  eixo-NN/*.html.
Nao depende de nenhuma biblioteca externa.
"""

import io
import os
import re
import shutil
import unicodedata

RAIZ = os.path.dirname(os.path.abspath(__file__))
CONTEUDO = os.path.join(RAIZ, 'conteudo')

EIXOS = [
    ('eixo-01', 'eixo-01-revelacao.md'),
    ('eixo-02', 'eixo-02-trindade.md'),
]

SITE = 'Magistério temático'
SUBTITULO = 'Os textos que formam a doutrina católica, em tradução própria e ordenados por assunto'


# --------------------------------------------------------------------------
# utilidades
# --------------------------------------------------------------------------

def slug(texto):
    t = unicodedata.normalize('NFKD', texto)
    t = u''.join(c for c in t if not unicodedata.combining(c))
    t = t.replace(u'—', '-').replace(u'–', '-')
    t = re.sub(r'[^A-Za-z0-9]+', '-', t).strip('-').lower()
    return re.sub(r'-{2,}', '-', t)[:60]


def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def inline(t):
    """Converte a marcacao inline usada no corpus."""
    t = esc(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)', r'<i>\1</i>', t)
    t = re.sub(r'(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)', r'<i>\1</i>', t)
    return t


def so_italico(par):
    p = par.strip()
    return (p.startswith('_') and p.endswith('_')) or \
           (p.startswith('*') and p.endswith('*') and not p.startswith('**'))


# --------------------------------------------------------------------------
# leitura do markdown
# --------------------------------------------------------------------------

def ler_eixo(caminho, pasta):
    txt = io.open(caminho, encoding='utf-8').read()
    # trechos comentados com <!-- ... --> ficam fora do site
    txt = re.sub(r'<!--.*?-->', '', txt, flags=re.S)
    linhas = txt.split('\n')

    eixo = {'pasta': pasta, 'titulo': '', 'resumo': '', 'trechos': []}
    secao = ''
    atual = None
    buf = []

    def fecha():
        if atual is not None:
            atual['corpo'] = '\n'.join(buf).strip()
            eixo['trechos'].append(atual)

    i = 0
    while i < len(linhas):
        ln = linhas[i]
        if ln.startswith('# Eixo'):
            eixo['titulo'] = ln[2:].strip()
            j = i + 1
            while j < len(linhas) and not linhas[j].strip():
                j += 1
            if j < len(linhas) and not linhas[j].startswith('#'):
                eixo['resumo'] = linhas[j].strip()
        elif ln.startswith('# ') and not ln.startswith('# Eixo'):
            secao = ln[2:].strip()
        elif ln.startswith('## '):
            fecha()
            atual = {'titulo': ln[3:].strip(), 'secao': secao}
            buf = []
        elif atual is not None:
            if ln.strip() != '---':
                buf.append(ln)
        i += 1
    fecha()

    for n, tr in enumerate(eixo['trechos'], 1):
        tr['arquivo'] = '%02d-%s.html' % (n, slug(re.sub(r'[*_]', '', tr['titulo'])))
        tr['url'] = '%s/%s' % (pasta, tr['arquivo'])
        tr['eixo'] = eixo
    return eixo


def partes(corpo):
    """Separa cabecalho (metadados e resumo) do corpo propriamente dito."""
    blocos = [b.strip() for b in re.split(r'\n\s*\n', corpo) if b.strip()]
    cabeca, resto, no_corpo = [], [], False
    for b in blocos:
        if not no_corpo and so_italico(b) and '\n' not in b:
            cabeca.append(b)
        else:
            no_corpo = True
            resto.append(b)
    return cabeca, resto


def corpo_html(blocos):
    out = []
    for b in blocos:
        if b.startswith('### '):
            out.append('<h2>%s</h2>' % inline(b[4:].strip()))
        elif so_italico(b) and '\n' not in b:
            out.append('<p class="nota">%s</p>' % inline(b.strip('_*')))
        else:
            out.append('<p>%s</p>' % inline(b.replace('\n', ' ')))
    return '\n'.join(out)


# --------------------------------------------------------------------------
# gabarito
# --------------------------------------------------------------------------

def pagina(titulo, corpo, prof=0, classe='', descricao=''):
    base = '../' * prof
    return u"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titulo)s</title>
<meta name="description" content="%(desc)s">
<link rel="stylesheet" href="%(base)sassets/style.css">
</head>
<body class="%(classe)s">
<header class="topo">
  <a class="marca" href="%(base)sindex.html">%(site)s</a>
  <a class="crit" href="%(base)scriterios.html">Critérios</a>
</header>
<main>
%(corpo)s
</main>
<footer class="rodape">
  <a href="%(base)sindex.html">Índice geral</a> ·
  <a href="https://github.com/gereneto/magisterio-tematico">Repositório</a>
</footer>
</body>
</html>
""" % {'titulo': esc(titulo), 'corpo': corpo, 'base': base, 'classe': classe,
       'site': esc(SITE), 'desc': esc(descricao or SUBTITULO)}


# --------------------------------------------------------------------------
# geracao
# --------------------------------------------------------------------------

def gerar():
    eixos = [ler_eixo(os.path.join(CONTEUDO, arq), pasta) for pasta, arq in EIXOS]
    seq = [tr for e in eixos for tr in e['trechos']]

    # --- paginas de trecho ---
    for n, tr in enumerate(seq):
        cabeca, resto = partes(tr['corpo'])
        h = ['<article class="trecho">']
        h.append('<p class="fio"><a href="index.html">%s</a> · %s</p>'
                 % (esc(tr['eixo']['titulo']), esc(tr['secao'])))
        h.append('<h1>%s</h1>' % inline(tr['titulo']))
        # a ultima linha do cabecalho e o resumo; as anteriores sao contexto
        for k, c in enumerate(cabeca):
            cls = 'resumo' if (k == len(cabeca) - 1 and c.startswith('_')) else 'fonte'
            h.append('<p class="%s">%s</p>' % (cls, inline(c.strip('_*'))))
        h.append('<div class="texto">')
        h.append(corpo_html(resto))
        h.append('</div>')

        ant = seq[n - 1] if n > 0 else None
        prox = seq[n + 1] if n < len(seq) - 1 else None
        h.append('<nav class="passo">')
        if ant:
            rel = ('../' + ant['url']) if ant['eixo'] is not tr['eixo'] else ant['arquivo']
            h.append('<a class="ant" href="%s"><span>Anterior</span>%s</a>'
                     % (rel, inline(ant['titulo'])))
        else:
            h.append('<span class="ant vazio"></span>')
        if prox:
            rel = ('../' + prox['url']) if prox['eixo'] is not tr['eixo'] else prox['arquivo']
            h.append('<a class="prox" href="%s"><span>Próximo</span>%s</a>'
                     % (rel, inline(prox['titulo'])))
        else:
            h.append('<span class="prox vazio"></span>')
        h.append('</nav>')
        h.append('</article>')

        dest = os.path.join(RAIZ, tr['eixo']['pasta'], tr['arquivo'])
        desc = re.sub(r'[*_]', '', cabeca[-1]) if cabeca else ''
        escreve(dest, pagina(re.sub(r'[*_]', '', tr['titulo']) + ' — ' + SITE,
                             '\n'.join(h), prof=1, classe='pg-trecho', descricao=desc))

    # --- indice de cada eixo ---
    for e in eixos:
        h = ['<h1>%s</h1>' % esc(e['titulo'])]
        if e['resumo']:
            h.append('<p class="resumo">%s</p>' % inline(e['resumo']))
        sec, aberta = None, False
        for tr in e['trechos']:
            if tr['secao'] != sec:
                if aberta:
                    h.append('</ol>')
                sec = tr['secao']
                h.append('<h2>%s</h2>' % esc(sec))
                h.append('<ol class="lista">')
                aberta = True
            cabeca, _ = partes(tr['corpo'])
            res = ''
            for c in cabeca:
                if c.startswith('_'):
                    res = c.strip('_')
            h.append('<li><a href="%s"><b>%s</b><span>%s</span></a></li>'
                     % (tr['arquivo'], inline(tr['titulo']), inline(res)))
        if aberta:
            h.append('</ol>')
        html = '\n'.join(h)
        escreve(os.path.join(RAIZ, e['pasta'], 'index.html'),
                pagina(e['titulo'] + ' — ' + SITE, html, prof=1,
                       classe='pg-indice', descricao=e['resumo']))

    # --- capa ---
    h = ['<h1 class="capa">%s</h1>' % esc(SITE),
         '<p class="resumo">%s</p>' % esc(SUBTITULO),
         '<div class="eixos">']
    for e in eixos:
        h.append('<a class="cartao" href="%s/index.html"><b>%s</b><span>%s</span>'
                 '<em>%d trechos</em></a>'
                 % (e['pasta'], esc(e['titulo']), esc(e['resumo']), len(e['trechos'])))
    h.append('</div>')
    h.append('<p class="obs">A ordem entre os eixos segue a estrutura da fé; '
             'dentro de cada eixo, a ordem é cronológica, e didática na seção bíblica. '
             'Todas as traduções são feitas do grego e do latim.</p>')
    escreve(os.path.join(RAIZ, 'index.html'),
            pagina(SITE, '\n'.join(h), prof=0, classe='pg-capa'))

    # --- criterios ---
    md = io.open(os.path.join(CONTEUDO, 'criterios-selecao.md'), encoding='utf-8').read()
    escreve(os.path.join(RAIZ, 'criterios.html'),
            pagina('Critérios — ' + SITE, criterios_html(md), prof=0, classe='pg-criterios'))

    print('paginas geradas: %d trechos, %d eixos' % (len(seq), len(eixos)))


def criterios_html(md):
    out, tabela = [], False
    for b in re.split(r'\n\s*\n', md):
        b = b.strip()
        if not b or b == '---':
            continue
        if b.startswith('# '):
            out.append('<h1>%s</h1>' % inline(b[2:]))
        elif b.startswith('### '):
            out.append('<h3>%s</h3>' % inline(b[4:]))
        elif b.startswith('## '):
            out.append('<h2>%s</h2>' % inline(b[3:]))
        elif b.startswith('|'):
            linhas = [l for l in b.split('\n') if l.strip().startswith('|')]
            out.append('<div class="tab"><table>')
            for k, l in enumerate(linhas):
                cels = [c.strip() for c in l.strip().strip('|').split('|')]
                if set(''.join(cels)) <= set('-: '):
                    continue
                tag = 'th' if k == 0 else 'td'
                out.append('<tr>' + ''.join('<%s>%s</%s>' % (tag, inline(c), tag)
                                            for c in cels) + '</tr>')
            out.append('</table></div>')
        elif b.startswith('- '):
            itens = [l[2:] for l in b.split('\n') if l.startswith('- ')]
            out.append('<ul>' + ''.join('<li>%s</li>' % inline(i) for i in itens) + '</ul>')
        else:
            out.append('<p>%s</p>' % inline(b.replace('\n', ' ')))
    return '<article class="doc">' + '\n'.join(out) + '</article>'


def escreve(caminho, texto):
    d = os.path.dirname(caminho)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    io.open(caminho, 'w', encoding='utf-8').write(texto)


if __name__ == '__main__':
    gerar()
