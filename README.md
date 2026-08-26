# Magistério temático

Os textos que formam a doutrina católica, em tradução própria do grego e do latim, ordenados por assunto.

O projeto reúne as definições dogmáticas e os documentos que as produziram, distribuídos em eixos temáticos. A ordem entre os eixos segue a estrutura da fé; dentro de cada eixo, a ordem é cronológica — e didática na seção bíblica, para que o desenvolvimento da doutrina fique visível.

Cada trecho tem a sua própria página, com a identificação da autoridade magisterial e uma frase que diz o seu cerne. As páginas são navegáveis na ordem do eixo.

## Estado

| Eixo | Situação |
|---|---|
| 1 — Revelação | 28 trechos |
| 2 — Trindade | 34 trechos |
| 3 a 12 | a fazer |

Os critérios de seleção e de tradução estão em [`conteudo/criterios-selecao.md`](conteudo/criterios-selecao.md) e publicados em `criterios.html`.

## Como o site é gerado

O conteúdo está em `conteudo/`, em Markdown. As páginas HTML são geradas a partir dele:

```bash
python build.py
```

Não há dependências: basta Python 3. O script lê os arquivos de `conteudo/`, escreve `index.html`, `criterios.html` e uma pasta por eixo com uma página por trecho, e refaz a navegação entre elas.

### Convenções dos arquivos de conteúdo

- `# Eixo N — Nome`, seguido de uma linha que descreve o eixo.
- `# I. Seção` divide o eixo (Escritura, Padres, concílios, etc.).
- `## Título` abre um trecho — é o que vira uma página.
- Logo abaixo do título, uma linha em `*itálico com asteriscos*` traz a fonte e a numeração DH; uma linha em `_itálico com sublinhados_` traz o resumo do trecho, que aparece destacado na página e no índice do eixo.
- `### Subtítulo` divide um trecho longo, e pode receber a sua própria linha de resumo.
- Linhas em `_sublinhado_` no meio do texto são notas, e aparecem em corpo menor.
- Um trecho envolvido em `<!-- ... -->` fica fora do site.

## Licença

As traduções são obra própria. O texto latino e grego das fontes é de domínio público.
