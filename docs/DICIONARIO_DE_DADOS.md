# Dicionário de dados

Colunas técnicas presentes em toda tabela da bronze: `_source_file` (string, caminho do arquivo de origem) e `_ingestion_ts` (timestamp da ingestão, igual para todas as linhas de uma execução).

## silver.empresas (450 linhas, uma por empresa)

| Coluna | Tipo | Observação |
|---|---|---|
| `id_empresa` | int | Chave natural |
| `razao_social` | string | `initcap` com `S.A.` corrigido |
| `nome_pregao` | string | `initcap` |
| `ticker` | string | MAIÚSCULAS |
| `cnpj` | string | Só dígitos |
| `cnpj_valido` | boolean | `true` se tem 14 dígitos |
| `setor`, `subsetor`, `cidade`, `segmento_listagem` | string | `initcap` |
| `situacao`, `uf` | string | MAIÚSCULAS |
| `data_fundacao`, `data_listagem` | date | "só ano" vira `NULL` |
| `valor_mercado` | double | Em reais (sem dividir) |
| `num_funcionarios` | int | Negativos viram `NULL` |
| `telefone` | string | Só dígitos, 11 dígitos, sem `55` |
| `telefone_valido`, `email_valido` | boolean | Validação de formato |
| `email_ri`, `site` | string | Minúsculas |

## silver.cotacoes (29.322 linhas, uma por empresa e dia)

`id_empresa` int · `ticker` string (MAIÚSCULAS) · `data_pregao` date · `preco_abertura`, `preco_maximo`, `preco_minimo`, `preco_fechamento`, `volume_financeiro` double · `qtd_negocios`, `qtd_titulos` bigint · metadados da bronze.

`silver.cotacoes_quarentena` (378 linhas) tem as mesmas colunas mais `motivo_rejeicao`.

## gold

| Tabela | Colunas principais |
|---|---|
| `dim_empresa` | `sk_empresa` (chave substituta), `id_empresa`, atributos da empresa, `data_inicio` (1900-01-01), `data_fim` (9999-12-31), `flag_atual` (true) |
| `fato_cotacao_diaria` | `sk_empresa`, `data_pregao`, preços, `volume_financeiro`, `qtd_negocios`, `qtd_titulos`, `retorno_diario_pct` (via `LAG`; nulo na 1ª cotação de cada empresa: 450 nulos) |
| `kpi_retorno_mensal` | `sk_empresa`, `ano_mes`, `fechamento_inicial`, `fechamento_final`, `qtd_pregoes`, `volume_total`, `volume_medio_diario`, `retorno_mensal_pct` |
| `ranking_setor_valor_mercado` | `sk_empresa`, `id_empresa`, `setor`, `razao_social`, `valor_mercado`, `rank_no_setor`, `pct_do_setor` |
| `resumo_por_setor` | `setor`, `qtd_empresas`, `valor_mercado_total`, `valor_mercado_medio`, `total_funcionarios`, `retorno_mensal_medio_pct` |
