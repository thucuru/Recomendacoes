# Recomendacoes
Objetivo do codigo:
Este código lê uma tabela de produtos (CSV) e gera uma planilha Excel com sugestões de produtos similares, com base em critérios como:
•	Tamanho do produto
•	Texto do nome do produto
•	Grupo e marca
O que o código faz?
1.	Lê um arquivo CSV com os produtos
2.	Limpa e normaliza os nomes dos produtos
3.	Extrai o tamanho do nome do produto (como 12", 300mm, etc.)
4.	Compara os produtos entre si para encontrar os mais parecidos
5.	Gera uma planilha Excel com as recomendações
Como o tamanho é extraído?
Ele procura números no nome com unidades como:
•	Polegadas ("12", 12 pol, 12 p)
•	Milímetros ou centímetros (300 mm, 30 cm)
Exemplo: "Faca Corte 12\"" → tamanho = 12
Como ele decide os produtos mais parecidos?
Depende do tipo de produto (GrupoPai):
Se for do Grupo Pai 550000 “cutelaria”:
•	Usa apenas a diferença de tamanho.
•	Recomenda os produtos com tamanho mais próximo.
Para os outros grupos:
•	Compara o nome com outros produtos usando dois métodos:
o	Similaridade de palavras (TF-IDF e cosseno)
o	Distância entre letras (Levenshtein)
•	Prioriza pelo menos 1 da mesma marca, depois os de outras marcas, desde que estejam no mesmo grupo.
