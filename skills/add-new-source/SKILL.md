---
name: add-new-source
description: Passo a passo para adicionar uma nova fonte de dados (novo CSV ou nova tabela) ao pipeline B3 Lakehouse, da ingestão na bronze até a silver. Use quando o usuário pedir para ingerir, tratar ou incluir uma base nova, ou novos arquivos de dados.
---

# Adicionar uma nova fonte

Método reaproveitável: **ingerir como texto, perfilar, tratar, validar**. As regras da silver são específicas de cada base.

## Passos
1. **Pouso:** coloque o arquivo em `/Volumes/workspace/bronze/landing/raw` com **nome novo** (arquivo com nome já carregado é ignorado).
2. **Bronze:** chame `ingest(padrao_do_arquivo, separador, nome_da_tabela)` no notebook `02_bronze_ingestao`. Tudo entra como `string`, com `_source_file` e `_ingestion_ts`. Idempotente por arquivo.
3. **Perfilamento:** copie o modelo do notebook `03` e adapte aos nomes de coluna: duplicatas por chave, nulos disfarçados, valores distintos, formatos de data e de número, tamanhos.
4. **Contrato:** defina colunas, tipos e **chave natural** da nova fonte.
5. **Silver:** proponha criar `04_silver_<fonte>` seguindo a skill `silver-cleaning`. Grave com `overwrite` em `workspace.silver.<fonte>`.
6. **Validação:** defina invariantes e, quando apropriado, números de referência e valide (skill `data-quality-checks`).
7. **Documentação:** atualize `docs/DICIONARIO_DE_DADOS.md`, `docs/QUALIDADE_DE_DADOS.md` e `docs/ARQUITETURA.md`.
8. **Entrega:** branch `feature/...`, commit e pull request.

## Observações
- Se for um novo snapshot do **cadastro**, o notebook 02 lê um arquivo fixo (`empresas_raw_d1.csv`): troque por um padrão e decida como tratar mudanças (SCD).
- A carga é completa; incremental está no `docs/ROADMAP.md` como exploração opcional.
