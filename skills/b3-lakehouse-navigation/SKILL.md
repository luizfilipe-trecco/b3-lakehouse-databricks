---
name: b3-lakehouse-navigation
description: Orienta o agente no projeto B3 Lakehouse (pipeline medalhão Bronze, Silver e Gold no Databricks). Use quando precisar entender a estrutura do repositório, qual notebook faz o quê, onde ficam as tabelas e qual a ordem de execução, antes de ler ou alterar qualquer código.
---

# Navegação no projeto B3 Lakehouse

## Passos
1. Leia `AGENTS.md` na raiz (regras e convenções).
2. Para o desenho geral, leia `docs/ARQUITETURA.md`. Para colunas e tipos, `docs/DICIONARIO_DE_DADOS.md`.
3. Identifique a camada do problema e abra o notebook correspondente:

| Camada | Notebook | Tabelas |
|---|---|---|
| Setup | `00_setup_unity_catalog` | schemas e volume |
| Dados brutos | `01_gerar_dados_brutos` | CSVs no volume |
| Bronze | `02_bronze_ingestao` | `bronze.empresas_raw`, `bronze.cotacoes_raw` |
| Diagnóstico | `03_perfilamento_bronze` | somente leitura |
| Silver | `04_silver_empresas`, `04_silver_cotacoes` | `silver.empresas`, `silver.cotacoes`, `silver.cotacoes_quarentena` |
| Gold | `05_gold` | cinco tabelas `gold.*` |

4. Ordem de execução: `00 → 01 → 02 → 04_silver_empresas → 04_silver_cotacoes → 05_gold`.
5. Antes de mudar um tratamento, leia `docs/QUALIDADE_DE_DADOS.md` (invariantes e contagens de referência; confirme-as no workspace).

## Regras
- A bronze é imutável. Correções ficam na silver.
- Não faça commit direto na `main`.
