---
name: gold-modeling
description: Convenções para criar ou alterar tabelas da camada Gold em Spark SQL neste projeto (dimensão com chave substituta, fato diária, KPI mensal, ranking e resumo por setor). Use ao modelar, consultar ou revisar a gold, ou ao discutir granularidade, SCD e joins entre fato e dimensão.
---

# Gold: modelagem

## Convenções
- `CREATE OR REPLACE TABLE workspace.gold.<tabela> AS SELECT ...` (reexecutável).
- Comentar a **granularidade** (uma linha por ...) no topo de cada SQL.
- A fato aponta para a dimensão pela **chave substituta** `sk_empresa`; o JOIN usa `id_empresa` como `INT` e `flag_atual = true`.
- Dimensão com `data_inicio` (1900-01-01), `data_fim` (9999-12-31) e `flag_atual`: preparada para SCD tipo 2 (não implementado na carga).

> As contagens seguintes são referências do cenário gerado, não verificações em execução.

## Tabelas e granularidade
| Tabela | Uma linha por | Linhas |
|---|---|---|
| `dim_empresa` | empresa | 450 |
| `fato_cotacao_diaria` | empresa e dia | 29.322 |
| `kpi_retorno_mensal` | empresa e mês | 1.350 |
| `ranking_setor_valor_mercado` | empresa | 450 |
| `resumo_por_setor` | setor | 11 |

## Padrões SQL
- Retorno diário: `fechamento / LAG(fechamento) OVER (PARTITION BY id_empresa ORDER BY data_pregao) - 1`. A 1ª cotação de cada empresa fica nula (450 nulos). Cotações em quarentena deixam buracos: o "anterior" é o último pregão disponível.
- KPI mensal: `ROW_NUMBER` crescente e decrescente para achar o primeiro e o último pregão do mês (mais seguro que `LAST_VALUE`).
- Ranking: `RANK() OVER (PARTITION BY setor ORDER BY valor_mercado DESC NULLS LAST)`.

## Validação
Linhas esperadas: 450 · 29.322 · 1.350 · 450 · 11. A soma de pregões do KPI deve ser 29.322 e o volume total da fato deve igualar o da silver.
