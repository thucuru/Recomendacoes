Apresentação do Código de Recomendação de Produtos
Objetivo
Este código lê uma tabela de produtos (CSV) e gera uma planilha Excel com sugestões de produtos similares, com base em critérios como:

Tamanho do produto

Texto do nome do produto

Grupo e marca

O que o código faz?
Lê um arquivo CSV com os produtos

Limpa e normaliza os nomes dos produtos

Extrai o tamanho do nome do produto (como 12", 300mm, etc.)

Compara os produtos entre si para encontrar os mais parecidos

Gera uma planilha Excel com as recomendações

Como o nome do produto é tratado?
Exemplo de nome original:
"Faca de Corte 12""

Passos:

Remove acentos: "Faca de Corte 12"

Coloca tudo em minúsculo: "faca de corte 12"

Remove palavras como "de", "com", "para": "faca corte 12"

Como o tamanho é extraído?
Ele procura números no nome com unidades como:

Polegadas ("12", 12 pol, 12 p)

Milímetros ou centímetros (300 mm, 30 cm)

Exemplo: "Faca Corte 12\"" → tamanho = 12

Como ele decide os produtos mais parecidos?
Depende do tipo de produto (GrupoPai):

Se for do GrupoPai 550000:
Usa apenas a diferença de tamanho.

Recomenda os produtos com tamanho mais próximo.

Para os outros grupos:
Compara o nome com outros produtos usando dois métodos:

Similaridade de palavras (TF-IDF e cosseno)

Distância entre letras (Levenshtein)

Prioriza os da mesma marca, depois os de outras marcas, desde que estejam no mesmo grupo.

Como funciona a geração da planilha?
O código pergunta se você quer gerar uma planilha para algum GrupoPai.

Para cada produto, ele cria uma lista de até 5 produtos recomendados.

Gera um arquivo Excel com:

Uma aba chamada "BaseProdutos" com todos os produtos

Abas separadas para cada grupo com os resultados

As colunas mostram:

Produto base: SKU, nome e valor

Produto recomendado: SKU, nome (usando fórmula do Excel), valor (também fórmula)
