# 🛍️ Sistema de Recomendação de Produtos

Este projeto gera uma **planilha com recomendações de produtos similares**, com base em um arquivo CSV contendo produtos. As recomendações consideram o nome do produto, o tamanho (quando aplicável), a marca e o grupo ao qual o item pertence.

---

## 📁 Estrutura do Projeto

- **Entrada:** Arquivo `seu_cadastro.csv` contendo os produtos
- **Saída:** Arquivo `recomendacoes.xlsx` com os produtos recomendados

---

## 📌 Funcionalidades

- **Normalização de texto:** remove acentos, palavras comuns e deixa o nome em minúsculas.
- **Extração de tamanho:** detecta medidas como polegadas, mm e cm a partir do nome.
- **Cálculo de similaridade:** usa TF-IDF + cosseno e distância de Levenshtein.
- **Filtros por grupo e marca:** garante que as recomendações sejam do mesmo grupo e, preferencialmente, da mesma marca.
- **Geração de Excel:** cria uma planilha organizada com as recomendações por GrupoPai e Grupo.

---

## 🧠 Lógica de Recomendação

### 🔸 GrupoPai = `550000`
- Recomendação baseada apenas no **tamanho do produto**.
- Ordena os produtos com **tamanho mais próximo**.

### 🔸 Outros GrupoPai
- Calcula a **similaridade textual** entre os nomes dos produtos.
- Usa:
  - **TF-IDF + similaridade de cosseno**
  - **Distância de Levenshtein**
- Prioriza produtos do **mesmo grupo** e da **mesma marca**.

---

## 📝 Como Usar

1. **Prepare o arquivo `seu_cadastro.csv`** com as colunas obrigatórias:
   - `SKU`, `Nome`, `Marca`, `Grupo`, `GrupoPai`, `Venda`

2. **Execute o script Python:**
   ```bash
   python nome_do_script.py
Deseja gerar uma planilha para um GrupoPai específico? (s/n): s
Digite os códigos dos GrupoPai separados por vírgula (ex: 550000,700000): 550000

Desenvolvido por JEAN ALEX DA SILVA.
