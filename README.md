# B3 Lakehouse: pipeline de dados em arquitetura medalhão no Databricks

Projeto de engenharia de dados que transforma dados brutos e "sujos" de empresas listadas na bolsa em tabelas confiáveis e prontas para análise, usando **arquitetura medalhão (Bronze → Silver → Gold)** no **Databricks** com **Unity Catalog**.

> **Os dados são fictícios.** Tickers, nomes, CNPJs e cotações foram gerados por um script em Python (com apoio de IA), e não representam empresas reais. Os problemas de qualidade foram plantados de propósito e catalogados, o que permitiu validar cada tratamento contra um número esperado.

**Stack:** Python · PySpark · Spark SQL · Delta Lake · Unity Catalog (catálogos, schemas, volumes, linhagem) · Git/GitHub (branches e pull requests)

---

## Arquitetura

```mermaid
flowchart LR
    G["Gerador Python<br/>(CSVs sujos)"] --> V[("Volume<br/>landing/raw")]
    V --> B["BRONZE<br/>tudo string + metadados<br/>ingestão idempotente"]
    B --> S["SILVER<br/>tipado, limpo, deduplicado<br/>+ quarentena"]
    S --> O["GOLD<br/>dimensão, fato e KPIs"]
```

| Camada | Schema | Papel | Tabelas |
|---|---|---|---|
| Landing | `bronze.landing` (volume) | Recebe os arquivos exatamente como chegam | CSVs de cadastro e de cotações |
| **Bronze** | `workspace.bronze` | Guarda o dado bruto, com rastreabilidade | `empresas_raw`, `cotacoes_raw` |
| **Silver** | `workspace.silver` | Limpa, tipa, valida e deduplica | `empresas`, `cotacoes`, `cotacoes_quarentena` |
| **Gold** | `workspace.gold` | Modela para responder perguntas de negócio | `dim_empresa`, `fato_cotacao_diaria`, `kpi_retorno_mensal`, `ranking_setor_valor_mercado`, `resumo_por_setor` |

---

## Estrutura do repositório

```
notebooks/
├── 00_setup_unity_catalog     # schemas bronze/silver/gold e volume landing
├── 01_gerar_dados_brutos      # gerador de dados fictícios e sujos
├── 02_bronze_ingestao         # CSV → tabelas Delta (bronze)
├── 03_perfilamento_bronze     # diagnóstico da qualidade antes de tratar
├── 04_silver_empresas         # limpeza e tipagem do cadastro
├── 04_silver_cotacoes         # limpeza, quarentena e integridade com empresas
└── 05_gold                    # dimensão, fato, KPIs e ranking
```

---

## Os dados e os problemas planejados

| Problema plantado | Onde | Como foi tratado |
|---|---|---|
| Duplicatas exatas e "quase" duplicatas (caixa e espaços diferentes) | empresas e cotações | Deduplicação por chave natural, **depois** da limpeza |
| Nulos disfarçados (`N/A`, `N/D`, `n/d`, vazio) | empresas | Convertidos em `NULL` |
| Datas em 5 formatos (e só o ano) | empresas | Função que tenta cada formato; "só ano" vira `NULL` |
| Datas em 3 formatos | cotações | Mesma abordagem |
| Valores em formato brasileiro (`R$ 1.234,56`) misturados com `1234.56` | `valor_mercado` | Regra separada por formato, para não perder o decimal |
| Vírgula decimal em preços | cotações | Troca por ponto e conversão segura |
| Preços nulos, zero ou negativos | cotações | Tabela de **quarentena** com o motivo |
| CNPJ com e sem pontuação, e com 13 dígitos | empresas | Só dígitos + coluna `cnpj_valido` |
| Caixa e espaços inconsistentes (`ATIVA`, `ativa`, ` Ativa`) | empresas e cotações | `trim`, `upper` e `initcap` |
| Colunas irrelevantes | ambas | Descartadas na silver |
| **Chave com tipos diferentes** (`'000123'` nas cotações, `123` no cadastro) | `id_empresa` | Conversão para `INT` nos dois lados |

---

## O que cada camada faz

### Bronze: guardar sem interpretar
- Tudo entra como **string**, e uma leitura nunca falha por causa de dado sujo.
- Metadados de rastreio: `_source_file` e `_ingestion_ts`.
- Ingestão **idempotente por arquivo**: rodar duas vezes não duplica (476 e 30.294 linhas nas duas execuções).
- Nenhuma correção: se a regra de negócio mudar, reprocessa-se silver e gold sem depender da fonte.

### Silver: limpar e confiar
- **Perfilamento antes de tratar:** as queries do notebook 03 mostraram o que estava errado, e cada tratamento foi conferido contra esses números.
- **Tipagem segura:** `try_cast` em vez de `cast`, que devolve `NULL` em vez de derrubar a execução.
- **Reconciliação:** a contagem de nulos antes e depois da conversão precisa fechar (por exemplo, datas: 33 nulos + 13 "só ano" = 46 nulos depois).
- **Quarentena:** cotações com preço inválido vão para `silver.cotacoes_quarentena` com o motivo, em vez de serem apagadas.
- **Integridade entre tabelas:** cada cotação precisa ter uma empresa e o mesmo ticker do cadastro.

### Gold: modelar para o negócio
- `dim_empresa`: uma linha por empresa, com chave substituta (`sk_empresa`) e colunas de histórico (`data_inicio`, `data_fim`, `flag_atual`).
- `fato_cotacao_diaria`: uma linha por empresa e dia, com retorno diário (`LAG`).
- `kpi_retorno_mensal`: retorno e volume por empresa e mês.
- `ranking_setor_valor_mercado`: `RANK()` por setor.
- `resumo_por_setor`: agregações por setor.

---

## Validações de qualidade (resultados)

| Verificação | Resultado |
|---|---|
| Empresas: bronze → silver | 476 → **450** (26 duplicatas removidas) |
| Cotações: bronze → silver | 30.294 → **29.700** (594 duplicatas removidas) |
| Cotações válidas + quarentena | 29.322 + 378 = **29.700** |
| Empresas × dias de pregão | 450 × 66 = 29.700 |
| JOIN cotações × empresas **na bronze** (texto) | **0 linhas** |
| JOIN cotações × empresas **na silver** (INT) | **todas as linhas** (29.322) |
| Cotações sem empresa correspondente | **0** |
| Tickers divergentes entre cotação e cadastro | **0** |
| Linhas na gold | `dim_empresa` 450 · `fato_cotacao_diaria` 29.322 · `kpi_retorno_mensal` 1.350 · `ranking` 450 · `resumo_por_setor` 11 |

**Um caso real de validação:** os tipos e contagens da silver de cotações passavam, mas a checagem de integridade **entre tabelas** revelou 662 tickers divergentes (cotações em minúsculas, cadastro em maiúsculas). Só olhar cada tabela isoladamente não teria pegado o erro.

---

## Decisões técnicas

| Decisão | Motivo |
|---|---|
| Bronze toda em string | Não perder nem quebrar a leitura com dado sujo; a interpretação é da silver |
| `try_cast` no lugar de `cast` | O modo ANSI do serverless derruba a execução no primeiro valor inválido |
| Regra separada para `valor_mercado` BR e simples | No formato BR o ponto é milhar; no simples é decimal. Limpar igual multiplicaria valores por 100 sem erro visível |
| `valor_mercado` mantido em reais na silver | A silver preserva o dado; a escala de apresentação fica para a gold |
| Quarentena em vez de descarte | Preço inválido não serve para o retorno, mas o motivo do erro fica auditável |
| 4 valores negativos de `num_funcionarios` viraram `NULL` | Corrigir o sinal seria adivinhar; `NULL` não inventa informação |
| "Só ano" nas datas vira `NULL` | Inventar dia e mês criaria uma data que não existe |
| CNPJ inválido marcado, não apagado | Preserva a informação para investigar a origem |
| Deduplicar depois da limpeza e da conversão | As "quase duplicatas" só ficam idênticas depois do `trim` e da padronização; a mesma cotação com data em outro formato escaparia |
| Chave substituta na dimensão | Prepara o SCD tipo 2, em que a mesma empresa terá várias versões |
| `NULLS LAST` no ranking | Empresas sem valor de mercado continuam no cadastro, no fim da lista |
| Sem particionar as tabelas | Com ~30 mil linhas, particionar geraria arquivos minúsculos (*small files*) |
| `bigint` em quantidade de títulos | O valor pode ultrapassar 2 bilhões |

---

## Governança e linhagem (Unity Catalog)

- Hierarquia `catálogo.schema.tabela`, com schemas separados por camada.
- Arquivos brutos em **Volume**, tabelas em **Delta**.
- A linhagem (bronze → silver → gold) é registrada automaticamente pelo Unity Catalog, já que as transformações rodam dentro dele.


### Evidências do pipeline

![Tabelas no Catalog](docs/img/catalog_tabelas.png)
  

---

## Como executar

Requer uma conta no **Databricks (Free Edition serve)** com compute serverless.

1. Crie um **Git folder** apontando para este repositório (Workspace → Create → Git folder).
2. Confirme o nome do seu catálogo em *Catalog*. Os notebooks usam `workspace`; se o seu for outro, troque o nome.
3. Execute na ordem:
   `00_setup_unity_catalog` → `01_gerar_dados_brutos` → `02_bronze_ingestao` → `03_perfilamento_bronze` → `04_silver_empresas` → `04_silver_cotacoes` → `05_gold`
4. A silver de cotações lê `silver.empresas` na validação de integridade, então a silver de empresas precisa rodar antes.

Se uma célula falhar, use *Run all above* antes de repetir: as transformações do DataFrame são encadeadas e uma execução com erro deixa passos pela metade na sessão.

---

## Limitações e próximos passos

**Limitações conhecidas**
- Os dados são fictícios, então os CNPJs não têm dígito verificador real: a validação checa apenas o tamanho.
- A carga é **completa** (`overwrite`), e não incremental.
- A idempotência da bronze é **por nome de arquivo**: um arquivo corrigido com o mesmo nome seria ignorado.
- A fato aponta para a versão atual da dimensão, sem ligar cada cotação à versão vigente na data dela.
- Os notebooks são executados manualmente, sem orquestração nem testes automatizados.
- Não há SCD implementado na carga. A dimensão já tem chave substituta e colunas de histórico, e foram gerados um segundo snapshot do cadastro e um arquivo de gabarito para essa evolução.

**Próximos passos**
- SCD tipo 2 em `setor` e `situacao` (e tipo 1 em razão social) com `MERGE`, usando o snapshot D2.
- Ingestão incremental com Auto Loader ou `COPY INTO`.
- Orquestração dos notebooks com Databricks Workflows (ou Airflow).
- Testes de qualidade automatizados, com falha do pipeline quando uma regra for violada.
- Particionamento ou *clustering* por data em volume maior.

---

## Como seria no Azure

O projeto roda na Free Edition, que não se conecta ao Azure. Este é o desenho de como ele seria em produção (**não executado**):

| Neste projeto | No Azure |
|---|---|
| Volume `landing` | Contêiner em **ADLS Gen2** (storage account com namespace hierárquico) |
| Gerador de dados | Fonte externa (API, banco, SFTP) |
| Ingestão para a landing | **Azure Data Factory**, com *Copy Activity* |
| Notebooks bronze, silver e gold | **Databricks Notebook Activity** dentro do pipeline do ADF |
| Ordem de execução | Dependências entre atividades (sucesso → próxima) |
| Agendamento | **Trigger** de agenda (por exemplo, diário às 02h) |
| Unity Catalog | Igual, com *external locations* apontando para o ADLS |
| Conexão ADF ↔ Databricks | *Linked service* com autenticação gerenciada |

Para um volume grande (por exemplo, 1 bilhão de linhas por dia): ingestão incremental, formato colunar (Parquet/Delta), partição por data, cópia paralela no ADF, compactação periódica (`OPTIMIZE`) e atenção a *small files* e *skew*.

---

## Autor

**Luiz Filipe Trecco**
GitHub: [luizfilipe-trecco](https://github.com/luizfilipe-trecco)
LinkedIn: [Luiz Filipe Trecco](https://www.linkedin.com/in/luiz-filipe-trecco/)
