# Decisões técnicas

| Decisão | Motivo |
|---|---|
| Bronze toda em `string` | Não perder nem quebrar a leitura com dado sujo; a interpretação é da silver |
| `_source_file` e `_ingestion_ts` na bronze | Rastreabilidade, idempotência por arquivo e desempate na deduplicação |
| Ingestão idempotente por caminho de arquivo | Reexecutar não duplica. Limitação: arquivo corrigido com o mesmo nome é ignorado |
| `try_cast` para entradas potencialmente inválidas | Retorna `NULL` em conversões inválidas; `cast` também pode ser adequado para dados previamente validados |
| Regra separada para `valor_mercado` BR e simples | O ponto é milhar no BR e decimal no simples |
| `valor_mercado` em reais na silver | A silver preserva o dado; escala de apresentação é da gold |
| Quarentena em vez de descarte | Preço inválido não serve para retorno, mas o motivo fica auditável |
| 4 funcionários negativos → `NULL` | Corrigir o sinal seria adivinhar |
| "Só ano" nas datas → `NULL` | Inventar dia e mês criaria data inexistente |
| CNPJ inválido marcado, não apagado | Preserva a informação para investigar |
| Deduplicar depois de limpar e converter | Quase-duplicatas só ficam iguais após `trim` e padronização |
| Chave substituta na dimensão | Prepara o SCD tipo 2 (várias versões por empresa) |
| `NULLS LAST` no ranking | Empresas sem valor de mercado ficam no fim, não fora |
| Sem particionar tabelas | ~30 mil linhas: partição geraria *small files* |
| `bigint` em `qtd_titulos` | Pode passar de 2 bilhões |
| Gold com `CREATE OR REPLACE TABLE` | Reexecutável sem duplicar (carga completa) |
