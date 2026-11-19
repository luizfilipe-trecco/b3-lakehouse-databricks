# Runbook

## Pré-requisitos
Databricks (Free Edition serve), compute serverless e Git folder apontando para o repositório. Confirmar em *Catalog* que o catálogo se chama `workspace` (senão, trocar o nome nos notebooks).

> **Atenção:** comandos destrutivos abaixo são apenas documentação. Não execute `DROP SCHEMA ... CASCADE` sem confirmação explícita e cópia dos dados necessários.

## Execução completa (ordem)
`00_setup_unity_catalog` → `01_gerar_dados_brutos` → `02_bronze_ingestao` → `03_perfilamento_bronze` (opcional) → `04_silver_empresas` → `04_silver_cotacoes` → `05_gold`.

## Reexecutar por cima (condicionalmente idempotente)
Rodar `02` → `04_silver_empresas` → `04_silver_cotacoes` → `05_gold` (não é preciso regerar o `01`). Conferir os números de referência em `QUALIDADE_DE_DADOS.md` e os invariantes de qualidade; a Bronze só ignora arquivos cujo caminho já consta em `_source_file`.

## Reiniciar do zero (DESTRUTIVO: pedir confirmação)
```sql
DROP SCHEMA IF EXISTS workspace.gold   CASCADE;
DROP SCHEMA IF EXISTS workspace.silver CASCADE;
DROP SCHEMA IF EXISTS workspace.bronze CASCADE;  -- apaga também o volume landing e os CSVs
```
Depois rodar do `00` ao `05`.

## Problemas comuns
| Sintoma | Causa | Solução |
|---|---|---|
| `NameError: df is not defined` | Sessão caiu | *Run all above* |
| Linhas empilhadas / contagem estranha após erro | Transformações encadeadas pela metade | Recriar o DataFrame do zero |
| `Path not found` no volume | `00` não rodou ou catálogo com outro nome | Rodar `00`; conferir o nome |
| Bronze não carregou arquivo novo | Nome igual a arquivo já carregado | Usar nome novo |
| `cache()` falha | Serverless não suporta APIs de cache | Gravar resultado intermediário em tabela |

## Novos dados
Arquivo novo na pasta `raw` com **nome novo** → rodar `02` → recriar silver e gold. A carga é completa (não incremental).
