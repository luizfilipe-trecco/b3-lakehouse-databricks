# Arquitetura

```
Gerador Python -> Volume landing (CSV) -> BRONZE -> SILVER -> GOLD
```

| Camada | Local | Papel | Tabelas |
|---|---|---|---|
| Landing | `/Volumes/workspace/bronze/landing/raw` | Recebe arquivos como chegam | `empresas_raw_d1.csv`, `empresas_raw_d2.csv`, `cotacoes_raw_202607..202609.csv` |
| Bronze | `workspace.bronze` | Guarda o bruto, tudo `string`, com rastreabilidade | `empresas_raw`, `cotacoes_raw` |
| Silver | `workspace.silver` | Limpa, tipa, valida, deduplica | `empresas`, `cotacoes`, `cotacoes_quarentena` |
| Gold | `workspace.gold` | Modela para o negócio | `dim_empresa`, `fato_cotacao_diaria`, `kpi_retorno_mensal`, `ranking_setor_valor_mercado`, `resumo_por_setor` |

> **Contagens:** os números abaixo são referências do cenário gerado nos notebooks, não medições atuais do workspace.

## Princípio

**A Bronze acrescenta arquivos novos (identificados pelo caminho); Silver e Gold são recriadas a partir das entradas disponíveis.** Se uma regra mudar, reprocessa-se sem depender da fonte.

## Granularidade

| Tabela | Uma linha por | Linhas |
|---|---|---|
| `bronze.empresas_raw` | linha do arquivo (com duplicatas) | 476 |
| `bronze.cotacoes_raw` | linha do arquivo (com duplicatas) | 30.294 |
| `silver.empresas` | empresa | 450 |
| `silver.cotacoes` | empresa e dia | 29.322 |
| `silver.cotacoes_quarentena` | cotação rejeitada | 378 |
| `gold.dim_empresa` | empresa (versão atual) | 450 |
| `gold.fato_cotacao_diaria` | empresa e dia | 29.322 |
| `gold.kpi_retorno_mensal` | empresa e mês | 1.350 |
| `gold.ranking_setor_valor_mercado` | empresa | 450 |
| `gold.resumo_por_setor` | setor | 11 |

## Dependências entre notebooks

`00` → `01` → `02` → `04_silver_empresas` → `04_silver_cotacoes` → `05_gold`. O `04_silver_cotacoes` lê `silver.empresas` na validação de integridade, então a silver de empresas roda antes. O `03` é somente leitura.

## Linhagem

Registrada automaticamente pelo Unity Catalog (aba *Lineage* de cada tabela): `bronze.cotacoes_raw → silver.cotacoes → gold.fato_cotacao_diaria`.
