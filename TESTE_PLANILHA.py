import pandas as pd
import unicodedata
import re
from Levenshtein import distance as levenshtein_distance
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from openpyxl import Workbook
import os

def normalizar_texto(texto):
    texto = ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c)).lower()
    texto = re.sub(r'\b(de|para|com|e|a|o|os|as)\b', '', texto)
    return texto.strip()

def extrair_tamanho(nome):
    match = re.findall(r'(\d{1,3})(\s?\"|\spol|\sp|\smm|\scm|\sm)', nome.lower())
    if match:
        return int(match[0][0])
    return None

try:
    produtos_df = pd.read_csv('seu_cadastro.csv', encoding='utf-8', on_bad_lines='skip', dtype=str, sep=';')
except FileNotFoundError:
    print("Arquivo 'seu_cadastro.csv' não encontrado.")
    exit()
except Exception as e:
    print(f"Erro ao carregar o CSV: {e}")
    exit()

colunas_necessarias = {'SKU', 'Nome', 'Marca', 'Grupo', 'GrupoPai', 'Venda'}
if not colunas_necessarias.issubset(produtos_df.columns):
    print(f"Erro: O arquivo CSV deve conter as colunas {colunas_necessarias}. Encontradas: {set(produtos_df.columns)}")
    exit()

produtos_df = produtos_df.dropna(subset=['Nome'])
produtos_df['Nome_Normalizado'] = produtos_df['Nome'].apply(normalizar_texto)
produtos_df['Tamanho'] = produtos_df['Nome'].apply(extrair_tamanho)

def calcular_similaridade(produto_sku, produtos_df):
    if produto_sku not in produtos_df['SKU'].values:
        print(f"SKU '{produto_sku}' não encontrado.")
        return [], "Ruim"

    produto = produtos_df[produtos_df['SKU'] == produto_sku].iloc[0]
    nome_ref = produto['Nome_Normalizado']

    outros_produtos = produtos_df[produtos_df['SKU'] != produto_sku]
    corpus = [nome_ref] + outros_produtos['Nome_Normalizado'].tolist()

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(corpus)

    ref_vector = tfidf_matrix[0]
    outros_vectors = tfidf_matrix[1:]

    cosine_sim = cosine_similarity(ref_vector, outros_vectors)[0]
    sim_scores_cosseno = dict(zip(outros_produtos['SKU'], cosine_sim))

    sim_scores_levenshtein = {}
    for _, row in outros_produtos.iterrows():
        dist = levenshtein_distance(nome_ref, row['Nome_Normalizado'])
        sim_scores_levenshtein[row['SKU']] = 1 - (dist / max(len(nome_ref), len(row['Nome_Normalizado'])))

    scaler = MinMaxScaler()
    cos_values = list(sim_scores_cosseno.values())
    lev_values = list(sim_scores_levenshtein.values())
    if cos_values and lev_values:
        scaled_cos = scaler.fit_transform([[v] for v in cos_values])
        scaled_lev = scaler.fit_transform([[v] for v in lev_values])
        sim_scores_combinados = {
            sku: 0.6 * scaled_cos[i][0] + 0.4 * scaled_lev[i][0]
            for i, sku in enumerate(sim_scores_cosseno.keys())
        }
    else:
        sim_scores_combinados = {}

    return sorted(sim_scores_combinados.items(), key=lambda x: x[1], reverse=True), "Bom"

def recomendar_produtos(produto_sku, produtos_df, max_recomendacoes=5):
    produto = produtos_df[produtos_df['SKU'] == produto_sku].iloc[0]
    grupo_pai = produto['GrupoPai']

    if grupo_pai == '550000':
        tamanho_ref = extrair_tamanho(produto['Nome'])
        grupo_ref = produto['Grupo']

        similares = produtos_df[
            (produtos_df['Grupo'] == grupo_ref) &
            (produtos_df['SKU'] != produto_sku) &
            (produtos_df['Tamanho'].notna())
        ].copy()

        similares['Dif_Tamanho'] = similares['Tamanho'].astype(int).apply(lambda x: abs(x - tamanho_ref))
        similares = similares.sort_values(by=['Dif_Tamanho', 'Venda'], ascending=[True, True])

        recomendacoes = [(row['SKU'], row['Nome'], 1.0) for _, row in similares.head(max_recomendacoes).iterrows()]
        if not recomendacoes:
            recomendacoes = [(produto['SKU'], produto['Nome'], 1.0)]
        return recomendacoes
    else:
        recomendacoes, _ = calcular_similaridade(produto_sku, produtos_df)
        produto = produtos_df[produtos_df['SKU'] == produto_sku].iloc[0]
        grupo_ref = produto['Grupo']
        marca_ref = produto['Marca']

        recomendacoes_filtradas = [
            (sku, produtos_df[produtos_df['SKU'] == sku]['Nome'].values[0], score)
            for sku, score in recomendacoes
            if sku != produto_sku and produtos_df[produtos_df['SKU'] == sku]['Grupo'].values[0] == grupo_ref
        ]

        mesma_marca = [
            rec for rec in recomendacoes_filtradas
            if produtos_df[produtos_df['SKU'] == rec[0]]['Marca'].values[0] == marca_ref
        ]

        outras_marcas = [
            rec for rec in recomendacoes_filtradas
            if produtos_df[produtos_df['SKU'] == rec[0]]['Marca'].values[0] != marca_ref
        ]

        resultado_final = []
        if mesma_marca:
            resultado_final.append(mesma_marca[0])
        resultado_final.extend(outras_marcas[:4])
        if len(resultado_final) < max_recomendacoes:
            resultado_final.extend(mesma_marca[1:max_recomendacoes - len(resultado_final)])
        if len(resultado_final) < max_recomendacoes:
            resultado_final.extend(outras_marcas[:max_recomendacoes - len(resultado_final)])

        if not resultado_final:
            resultado_final = [(produto['SKU'], produto['Nome'], 1.0)]
        return resultado_final[:max_recomendacoes]

def gerar_planilha_por_grupopai(produtos_df):
    gerar_grupo_pai = input("Deseja gerar uma planilha para um GrupoPai específico? (s/n): ").strip().lower()
    if gerar_grupo_pai == 's':
        grupos_pai_digitados = input("Digite os códigos dos GrupoPai separados por vírgula (ex: 550000,700000): ").split(',')
        grupos_pai_digitados = [g.strip() for g in grupos_pai_digitados]

        nome_arquivo = 'recomendacoes.xlsx'
        with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
            base_df = produtos_df[['SKU', 'Nome', 'Venda']].dropna(subset=['SKU', 'Nome', 'Venda'])

            # ✅ Converte SKU para número na BaseProdutos
            base_df['SKU'] = pd.to_numeric(base_df['SKU'], errors='coerce')

            base_df.to_excel(writer, sheet_name='BaseProdutos', index=False)

            for grupo_pai in grupos_pai_digitados:
                produtos_gp = produtos_df[produtos_df['GrupoPai'] == grupo_pai]
                if produtos_gp.empty:
                    print(f"Nenhum produto encontrado para GrupoPai {grupo_pai}")
                    continue

                grupos = produtos_gp['Grupo'].unique()
                for grupo in grupos:
                    produtos_grupo = produtos_gp[produtos_gp['Grupo'] == grupo].copy()
                    linhas_resultado = []

                    for idx, sku in enumerate(produtos_grupo['SKU'].unique()):
                        try:
                            produto_base = produtos_df[produtos_df['SKU'] == sku].iloc[0]
                            nome_base = produto_base['Nome']
                            valor_base = produto_base['Venda']
                            recomendacoes = recomendar_produtos(sku, produtos_df, max_recomendacoes=5)

                            for i, (rec_sku, rec_nome, _) in enumerate(recomendacoes):
                                excel_row = len(linhas_resultado) + 2
                                formula_nome = f'=IFERROR(VLOOKUP(D{excel_row}, BaseProdutos!A:C, 2, FALSE), "")'
                                formula_valor = f'=IFERROR(VLOOKUP(D{excel_row}, BaseProdutos!A:C, 3, FALSE), "")'

                                linhas_resultado.append({
                                    'REFERENCIA': int(sku) if i == 0 else '',
                                    'DESCRPROD': nome_base if i == 0 else '',
                                    'VALOR': valor_base if i == 0 else '',
                                    'REFERENCIA - RECOMENDADO': int(rec_sku),
                                    'DESCRPROD - RECOMENDADO': formula_nome,
                                    'VALOR - RECOMENDADO': formula_valor
                                })
                        except:
                            continue

                    df_resultado = pd.DataFrame(linhas_resultado)
                    aba_nome = re.sub(r'[\\/*?:\[\]]', '-', f"{grupo_pai}_{grupo}")[:31]
                    df_resultado.to_excel(writer, sheet_name=aba_nome, index=False)
                    print(f"Planilha gerada para GrupoPai {grupo_pai} - Grupo {grupo}")
        print(f"Arquivo '{nome_arquivo}' gerado com sucesso.")
        print("\033[92m" + "="*68)
        print("PLANILHA PRONTA")
        print("="*68 + "\033[0m")

# Executa ao rodar
gerar_planilha_por_grupopai(produtos_df)