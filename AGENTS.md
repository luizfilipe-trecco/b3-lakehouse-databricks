# AGENTS.md — B3 Lakehouse (guia para agentes de IA)

Projeto de engenharia de dados em **arquitetura medalhão** (Bronze → Silver → Gold) no **Databricks** (Unity Catalog, Delta Lake, PySpark, Spark SQL). Os dados são **fictícios** (empresas da B3 geradas por script, com sujeira planejada).

> Leia este arquivo primeiro. Para detalhes, siga os links em `docs/` e use as skills em `skills/`.

## Mapa rápido

| Preciso de... | Vá para |
|---|---|
| Entender a arquitetura | `docs/ARQUITETURA.md` |
| Saber colunas e tipos de cada tabela | `docs/DICIONARIO_DE_DADOS.md` |
| Saber quais problemas de qualidade existem e como são tratados | `docs/QUALIDADE_DE_DADOS.md` |
| Entender por que algo foi feito assim | `docs/DECISOES_TECNICAS.md` |
| Executar ou reexecutar o pipeline | `docs/RUNBOOK.md` |
| Ver o que está planejado | `docs/ROADMAP.md` |
| Índice de toda a documentação | `docs/INDEX.md` |

## Estrutura do repositório

```
notebooks/
  00_setup_unity_catalog.py     # schemas bronze/silver/gold e volume landing
  01_gerar_dados_brutos.py      # gerador de CSVs sujos (sementes fixas)
  02_bronze_ingestao.py         # CSV -> tabelas Delta (tudo string + metadados)
  03_perfilamento_bronze.py     # queries de diagnóstico (somente leitura)
  04_silver_empresas.ipynb      # limpeza/tipagem do cadastro
  04_silver_cotacoes.ipynb      # limpeza, quarentena e integridade com empresas
  05_gold.ipynb                 # dimensão, fato, KPI, ranking e resumo
docs/                           # documentação para humanos e agentes
skills/                         # skills (padrão Agent Skills: pasta + SKILL.md)
```

## Convenções do projeto

- Catálogo: `workspace`. Schemas: `bronze`, `silver`, `gold`. Volume: `workspace.bronze.landing` (CSVs em `/Volumes/workspace/bronze/landing/raw`).
- **Bronze**: campos de origem lidos como `string`, com `_source_file` e `_ingestion_ts` técnicos. Não corrigir dados brutos na Bronze; mudanças estruturais e operações destrutivas exigem revisão e autorização.
- **Silver**: limpar, tipar, deduplicar, validar. Preferir `try_cast` para entradas sujeitas a falhas de conversão; `cast` pode ser adequado para valores já validados. Verifique o código antes de alterar.
- **Gold**: `CREATE OR REPLACE TABLE ... AS SELECT`, com granularidade documentada em comentário.
- Nomes em `snake_case`; comentários e documentação em português.
- Validar invariantes (unicidade, integridade, regras) e, quando aplicável, comparar contagens com os valores de referência do cenário original (ver `docs/QUALIDADE_DE_DADOS.md`).
- Os notebooks são **reexecutáveis sob condições**: Bronze ignora caminhos de arquivo já carregados; Silver usa `overwrite`; Gold usa `CREATE OR REPLACE`. Reprocessar um arquivo modificado no mesmo caminho exige estratégia específica.

## Números de referência (validar no workspace)

**Referência do cenário de demonstração, não resultado de execução verificada nesta auditoria.** As contagens podem mudar com novos arquivos, snapshots ou alterações de regras; confirme no Databricks antes de afirmar resultados.


Bronze: `empresas_raw` 476 · `cotacoes_raw` 30.294. Silver: `empresas` 450 · `cotacoes` 29.322 · `cotacoes_quarentena` 378. Gold: `dim_empresa` 450 · `fato_cotacao_diaria` 29.322 · `kpi_retorno_mensal` 1.350 · `ranking_setor_valor_mercado` 450 · `resumo_por_setor` 11.

## Regras para agentes

1. **Não executar operações destrutivas** (`DROP SCHEMA`, `DROP TABLE`, apagar arquivos do volume) sem confirmação explícita do usuário.
2. **Não alterar a bronze** nem os CSVs do volume para "consertar" um problema: corrija na silver.
3. **Não fazer commit direto na `main`.** Criar branch (`feature/...`) e abrir pull request.
4. **Nunca incluir tokens, senhas ou e-mails pessoais** em código, notebooks ou documentação.
5. Ao mudar uma regra de tratamento, **atualizar** `docs/QUALIDADE_DE_DADOS.md` e os números esperados.
6. Se uma célula falhar, recriar o DataFrame do zero (*Run all above*): as transformações encadeadas deixam passos pela metade na sessão.
7. Os dados são fictícios; não apresentar resultados como se fossem dados reais de mercado.
8. Não afirmar que Auto Loader, MERGE incremental, SCD2 histórico ou Kafka estão implementados.
9. Não assumir que o agente tem permissão para executar no workspace; solicitar confirmação para qualquer ação com efeitos persistentes.
10. Os arquivos `skills/` são fonte versionada; a descoberta automática depende da configuração da ferramenta. Consulte `docs/AGENTES_E_TESTES.md`.

## Skills disponíveis (`skills/`)

| Skill | Use quando |
|---|---|
| `b3-lakehouse-navigation` | Precisar se orientar no projeto |
| `add-new-source` | Adicionar uma nova fonte de dados |
| `silver-cleaning` | Escrever ou revisar tratamentos da silver |
| `gold-modeling` | Criar ou alterar tabelas da gold |
| `data-quality-checks` | Validar uma etapa ou investigar um número errado |
| `run-and-reset-pipeline` | Executar, reexecutar ou reiniciar o pipeline |
