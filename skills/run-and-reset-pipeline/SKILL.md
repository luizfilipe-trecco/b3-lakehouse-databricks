---
name: run-and-reset-pipeline
description: Como executar, reexecutar ou reiniciar do zero o pipeline B3 Lakehouse no Databricks, em que ordem rodar os notebooks e como resolver erros comuns de sessão e catálogo. Use quando o usuário pedir para rodar tudo de novo, demonstrar o pipeline ou resetar o ambiente.
---

# Executar e reiniciar

## Reexecutar por cima (condicionalmente idempotente)
Rodar `02 → 04_silver_empresas → 04_silver_cotacoes → 05_gold`. Os dados do volume já existem (não regerar o `01`). Contagens de referência, não medidas nesta auditoria. Conferir no workspace: bronze 476 e 30.294; silver 450, 29.322 e 378; gold 450, 29.322, 1.350, 450 e 11.

## Do zero (DESTRUTIVO)
Apaga tabelas e o volume com os CSVs. **Pedir confirmação explícita ao usuário antes.**
```sql
DROP SCHEMA IF EXISTS workspace.gold   CASCADE;
DROP SCHEMA IF EXISTS workspace.silver CASCADE;
DROP SCHEMA IF EXISTS workspace.bronze CASCADE;
```
Depois rodar do `00` ao `05`.

## Erros comuns
- `NameError: df`: a sessão caiu; use *Run all above*.
- `Path not found` no volume: rode o `00` e confira o nome do catálogo.
- Bronze não carregou arquivo novo: o nome do arquivo já foi carregado.
- `cache()` falha no serverless: grave o resultado intermediário em tabela.
