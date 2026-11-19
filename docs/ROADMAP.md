# Roadmap e limitações

## Estado atual
Pipeline em **lote**, com ingestão Bronze por arquivo e reconstrução completa das camadas Silver e Gold, que atende bem à necessidade: a origem dos dados **não é tempo real** (NRT).

## Prioridade atual
1. **Preparar o repositório para agentes de IA** (este conjunto de documentos e skills).

## Exploração opcional (aprendizado)
- **Ingestão incremental** com Auto Loader e `MERGE INTO` (estudo; melhora a escala, não a necessidade atual).
- **Kafka / streaming**: usado **apenas como exemplo** para demonstrar conhecimento em streaming e mensageria. Não traz ganho relevante, já que a origem não é NRT.

## Limitações conhecidas
- Sem SCD implementado na carga (a dimensão já tem `sk_empresa`, `data_inicio`, `data_fim`, `flag_atual`; existe snapshot D2 e gabarito de mudanças no volume).
- Carga completa (`overwrite`), idempotência por nome de arquivo.
- `double` em valores financeiros (em produção, `DECIMAL`).
- CNPJ validado só pelo tamanho (dados fictícios).
- Execução manual e validações que imprimem resultados (sem `assert` nem testes automáticos).
