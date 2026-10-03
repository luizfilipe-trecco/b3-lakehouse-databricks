# B3 Lakehouse (dados fictícios) — Databricks + Unity Catalog + GitHub

Projeto de engenharia de dados em **arquitetura medalhão** (Bronze → Silver → Gold) no Databricks,
com dados **fictícios** de empresas listadas na B3, gerados com sujeira proposital para treino de tratamento.

## Stack
Python · PySpark · Spark SQL · Delta Lake · Unity Catalog (catalogs, schemas, volumes) · Git/GitHub

## Arquitetura
```
Gerador Python ─► Volume (landing/raw/*.csv)
                        │  02_bronze (PySpark, tudo string + metadados, idempotente)
                        ▼
                  BRONZE  (workspace.bronze.*)
                        │  silver: tipagem, datas, dedup, padronização, qualidade
                        ▼
                  SILVER  (workspace.silver.*)
                        │  gold: dim_empresa (SCD), fato_cotacao_diaria, KPIs
                        ▼
                  GOLD    (workspace.gold.*)
```

## Notebooks
| Notebook | O que faz |
|---|---|
| 00_setup_unity_catalog | Cria schemas bronze/silver/gold e o Volume `landing` |
| 01_gerar_dados_brutos | Gera CSVs sujos (cadastro D1/D2 e cotações mensais) |
| 02_bronze_ingestao | Ingestão idempotente para tabelas Delta |
| 03_perfilamento_bronze | Queries de diagnóstico da qualidade dos dados |

## Problemas planejados nos dados brutos
Duplicatas exatas e "quase" duplicatas, nulos disfarçados (`N/A`, `n/d`, vazio), datas em 5 formatos,
valores monetários em formato BR (`R$ 1.234,56`), CNPJ com formatos diferentes e inválido,
maiúsculas/minúsculas e espaços, colunas irrelevantes, preços negativos, e chave com tipos diferentes
entre tabelas (`'000123'` vs `123`).

## Como executar
Rodar os notebooks na ordem 00 → 01 → 02 → 03 no Databricks (compute serverless).
