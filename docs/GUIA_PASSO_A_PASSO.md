# Guia passo a passo: projeto B3 Lakehouse no Databricks

Tempo estimado: 2 a 3 horas para a base (partes 1 a 8) e mais algumas horas para silver, gold e SCD.
Vá com calma e **entenda cada passo antes de seguir**: é isso que o entrevistador vai testar.

> Os nomes de botões do Databricks e do GitHub mudam de vez em quando. Se algo não estiver exatamente
> onde descrevi, procure pelo nome em inglês na busca (`CTRL + P`) ou me mande um print.

---

## PARTE 0: O que você vai construir

```
Gerador Python ──► Volume (arquivos CSV brutos)
                       │ notebook 02
                       ▼
                  BRONZE  → tabelas Delta, tudo string + metadados
                       │ (você faz) notebook 04
                       ▼
                  SILVER  → tipado, limpo, deduplicado
                       │ (você faz) notebook 05
                       ▼
                  GOLD    → dim_empresa (SCD), fato_cotacao, KPIs
```

**Dados (fictícios):** ~450 empresas e ~30 mil cotações diárias, com sujeira proposital.

**Cobertura da lista da engenheira sênior da XP:**

| Tema da lista | Onde você pratica |
|---|---|
| Tipagem de dados e JOIN | Armadilha do `id_empresa` (`'000123'` vs `123`) |
| Arquitetura medalhão | Bronze → Silver → Gold |
| Unity Catalog | catalog → schema → tabela |
| Volumes | Pasta `landing` e diferença para tabelas |
| Clusters | Conceito (Free Edition só tem serverless) |
| GitHub | Repo, branches, commits, Git folder no Databricks |
| ADF | Parte 13 (desenho, pois não dá para executar de graça) |
| Linhagem | Aba Lineage do Catalog Explorer |
| SCD 1 e 2 | Snapshot D2 com mudanças planejadas |

---

## PARTE 1: Pré-requisitos

1. Conta no **GitHub** (github.com).
2. **Git** instalado no computador (git-scm.com). Teste no terminal: `git --version`.
3. Seu workspace **Databricks Free Edition** (você já tem).
4. Configure seu nome no Git (uma vez só):
   ```bash
   git config --global user.name "Seu Nome"
   git config --global user.email "seu-email-do-github@exemplo.com"
   ```

---

## PARTE 2: Reconhecer o terreno no Databricks

No menu lateral, abra e olhe cada item (2 minutos cada):

- **Workspace**: onde ficam notebooks e pastas.
- **Catalog**: Unity Catalog. Você deve ver um catálogo chamado `workspace`. **Anote o nome do seu.**
  Se for diferente, troque `workspace` por ele em todos os notebooks.
- **Compute**: na Free Edition só existe **serverless**.
- **SQL Editor**: para rodar SQL fora de notebook.

**Conceito para saber explicar: Unity Catalog**
É a camada de **governança** do Databricks: organiza e controla acesso a dados e arquivos numa hierarquia:

```
catalog  →  schema  →  tabela / view / volume / função
workspace.bronze.empresas_raw
```
Também guarda metadados e a **linhagem** (quem alimenta quem).

---

## PARTE 3: Criar o repositório no GitHub

1. GitHub → botão **New repository**.
2. Nome: `b3-lakehouse-databricks`. Marque **Public** (para mostrar ao entrevistador) e **Add a README file**.
3. **Create repository**.
4. Clone no seu computador:
   ```bash
   git clone https://github.com/SEU_USUARIO/b3-lakehouse-databricks.git
   cd b3-lakehouse-databricks
   ```
5. Descompacte o zip que te mandei e copie para dentro da pasta clonada: `notebooks/`, `docs/`, `.gitignore` e `README.md` (substitua o README).
6. Primeiro commit:
   ```bash
   git add .
   git commit -m "chore: estrutura inicial do projeto"
   git push origin main
   ```
7. Atualize a página do GitHub e confira se os arquivos apareceram.

**Conceito: commit** é uma "foto" do projeto com uma mensagem. Prefixos comuns: `feat:` (funcionalidade), `fix:` (correção), `docs:`, `chore:`.

---

## PARTE 4: Conectar o GitHub ao Databricks (Git folder)

### 4.1 Criar um token de acesso no GitHub
1. GitHub → sua foto → **Settings** → (rolar até o fim) **Developer settings**.
2. **Personal access tokens** → **Fine-grained tokens** → **Generate new token**.
3. Nome: `databricks`. Expiração: 90 dias.
4. **Repository access**: *Only select repositories* → escolha o repo do projeto.
5. **Permissions → Repository permissions → Contents: Read and write**.
6. **Generate token** e **copie o token agora** (ele só aparece uma vez).

> Trate o token como senha. Nunca o coloque em notebook ou commit.

### 4.2 Registrar o token no Databricks
1. Clique no seu avatar (canto superior direito) → **Settings**.
2. **Linked accounts** (ou *Git integration*) → provedor **GitHub** → método **Personal access token**.
3. Cole o token, informe seu usuário/e-mail do GitHub e **Save**.

### 4.3 Criar o Git folder
1. **Workspace** → botão **Create** → **Git folder**.
2. Cole a URL do repo (`https://github.com/SEU_USUARIO/b3-lakehouse-databricks.git`).
3. **Create Git folder**. Os notebooks aparecem em `notebooks/`.

> **Alternativa se o Git folder der problema:** Workspace → menu `⋮` de uma pasta → **Import** → selecione os arquivos `.py` dos notebooks. Funciona, mas perde a integração com Git.

**Conceito: Git folder** é uma pasta do Databricks sincronizada com um repositório: você faz commit, push e pull, e troca de branch pela interface.

---

## PARTE 5: Rodar o setup do Unity Catalog (notebook 00)

1. Abra `notebooks/00_setup_unity_catalog.py`.
2. No canto superior direito, em **Connect**, escolha **Serverless**.
3. **Run all**.
4. Confira em **Catalog → workspace**: devem existir os schemas `bronze`, `silver`, `gold`. Em `bronze`, aba **Volumes**, deve existir `landing`.

**Conceito: Volume vs Tabela (pergunta de entrevista quase certa)**

| | Volume | Tabela |
|---|---|---|
| Guarda | **Arquivos** de qualquer tipo (CSV, JSON, imagem, PDF) | **Dados estruturados** em linhas e colunas (Delta) |
| Acesso | Caminho `/Volumes/catalogo/schema/volume/...` | `SELECT ... FROM catalogo.schema.tabela` |
| Schema | Nenhum, é só arquivo | Schema definido, com tipos |
| Uso típico | Área de pouso (*landing*), arquivos brutos | Dados prontos para consulta |

---

## PARTE 6: Gerar os dados brutos (notebook 01)

1. Abra `01_gerar_dados_brutos.py`, conecte ao **Serverless** e **Run all**. Leva cerca de 1 minuto.
2. Confira o resultado: **Catalog → workspace → bronze → landing → raw**. Devem existir:
   - `empresas_raw_d1.csv` e `empresas_raw_d2.csv` (separador `;`)
   - `cotacoes_raw_202607.csv`, `202608`, `202609` (separador `,`)
3. Existe também a pasta `gabarito` com a lista de mudanças esperadas do D1 para o D2. **Não use como entrada**, é só para conferir seu SCD depois.
4. Baixe um CSV e abra no Excel ou bloco de notas. Olhe a sujeira com seus próprios olhos.

Ler o notebook com calma também vale: ele mostra como a sujeira foi criada, e isso ajuda a saber tratá-la.

---

## PARTE 7: Ingestão para a camada Bronze (notebook 02)

1. Abra `02_bronze_ingestao.py` e **Run all** (as células da "FASE SCD" ficam comentadas).
2. Resultado esperado:
   - `workspace.bronze.empresas_raw` com **476 linhas** (450 empresas + 26 duplicatas)
   - `workspace.bronze.cotacoes_raw` com **~30.294 linhas**
3. Em **Catalog**, abra a tabela e veja as abas **Columns**, **Sample Data** e **Details**.
4. **Teste a idempotência:** rode o notebook de novo. As contagens **não** devem mudar.

**Por que a bronze é assim? (saiba explicar cada ponto)**
- **Tudo string** (`inferSchema=False`): bronze não interpreta. Se um valor vier sujo, a leitura não quebra e nada se perde.
- **`_source_file` e `_ingestion_ts`**: rastreabilidade (de onde veio e quando).
- **Append + filtro de arquivos já carregados**: reprocessar não duplica.
- **Nenhuma correção**: a regra de negócio vai para a silver. Se ela mudar, você reprocessa sem depender da fonte.

---

## PARTE 8: Perfilamento (notebook 03)

Antes de limpar qualquer coisa, **descubra o que está errado**. Rode cada célula de `03_perfilamento_bronze.py` e anote.

Resultados esperados:

| Query | O que você deve encontrar |
|---|---|
| 1 e 2 | 476 linhas e 450 ids distintos, ou seja, 26 ids repetidos |
| 3 | Nulos disfarçados: `N/A`, `N/D`, `n/d` e vazios |
| 4 e 5 | `setor` e `situacao` com caixa e espaços diferentes |
| 5 | 5 formatos de data, mais "só ano" e `N/D` |
| 6 | CNPJ com 14 dígitos, mas também com 13 (inválido) |
| 7 | `valor_mercado` como `R$ 1.234,56` e como `1234.56` |
| 8 | Preços com vírgula, negativos e nulos |
| 9 | Duplicatas nas cotações |
| 10 | **JOIN retorna 0 linhas**: `'000123'` ≠ `'123'` |

**A query 10 é a mais importante.** É exatamente o assunto "JOIN entre colunas de tipos diferentes" da lista da engenheira. Descubra por que dá zero e como resolver.

---

## PARTE 9: Checklist de tratamento (para suas camadas Silver e Gold)

Faça em notebooks novos: `04_silver_empresas.py`, `04_silver_cotacoes.py`, `05_gold.py`.

### Silver: empresas
- [ ] Padronizar nomes das colunas em `snake_case` minúsculo (já estão)
- [ ] Descartar colunas irrelevantes: `cor_marca`, `codigo_legado`, `flag_teste`, `obs_interna`, `hash_antigo`, `versao_layout`
- [ ] Texto: `trim` em todas, padronizar caixa (`upper` para ticker/situação/UF, `initcap` para nomes/cidade)
- [ ] Nulos disfarçados (`N/A`, `N/D`, `n/d`, vazio) → `NULL` de verdade
- [ ] Datas em 5 formatos → `DATE` (e "só ano" → decidir: `NULL` ou 01/01?)
- [ ] `valor_mercado` → `DOUBLE` (tratar `R$` e vírgula)
- [ ] `num_funcionarios` → `INT` (tratar `1.200`, `n/d` e negativos)
- [ ] `cnpj` → só dígitos, com 14 caracteres; marcar inválidos
- [ ] `segmento_listagem` → padronizar valores (ex.: `NOVO MERCADO` = `Novo Mercado`)
- [ ] Deduplicar por `id_empresa` (duplicatas exatas **e** "quase" iguais) → `row_number()` ordenado por `_ingestion_ts`
- [ ] `id_empresa` → `INT`

### Silver: cotações
- [ ] `id_empresa` → `INT` (remover zeros à esquerda)
- [ ] `data_pregao` (3 formatos) → `DATE`
- [ ] Preços e volume: trocar vírgula por ponto e converter para `DOUBLE`
- [ ] Preços negativos ou zero → inválidos (mandar para uma tabela de quarentena)
- [ ] `preco_fechamento` nulo → decidir a regra (descartar? marcar?)
- [ ] `ticker` → trim e upper
- [ ] Deduplicar por (`id_empresa`, `data_pregao`) **depois** de converter a data
- [ ] Descartar colunas irrelevantes (`codigo_bdi`, `tipo_mercado`, `moeda`, `fator_cotacao`, `prazo_dias_termo`, `codigo_isin`)
- [ ] Validar: máximo ≥ mínimo, fechamento entre mínimo e máximo
- [ ] Gravar particionado ou com clustering por mês

### Gold (ideias)
- `dim_empresa` (com SCD, ver Parte 12)
- `fato_cotacao_diaria` (JOIN silver cotações × dimensão, **com tipos iguais**)
- `kpi_retorno_mensal_por_empresa`, `ranking_setor_valor_mercado`, `volume_medio_por_setor`

### Dicas de código (só os trechos mais chatos)

Datas com vários formatos (tenta cada um e pega o primeiro que funcionar):
```python
from pyspark.sql import functions as F

def parse_data(col):
    c = F.trim(F.col(col))
    return F.coalesce(
        F.expr(f"try_to_date(trim({col}), 'dd/MM/yyyy')"),
        F.expr(f"try_to_date(trim({col}), 'yyyy-MM-dd')"),
        F.expr(f"try_to_date(trim({col}), 'dd-MM-yyyy')"),
        F.expr(f"try_to_date(trim({col}), 'yyyyMMdd')"),
        F.expr(f"try_to_date(trim({col}), 'dd.MM.yyyy')"),
    )
```

Conversão segura de número (retorna `NULL` em vez de quebrar):
```python
F.expr("try_cast(regexp_replace(preco_fechamento, ',', '.') as double)")
```

Dedup mantendo o registro mais recente:
```python
from pyspark.sql import Window
w = Window.partitionBy("id_empresa").orderBy(F.col("_ingestion_ts").desc())
dedup = df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")
```

> **Cuidado ao deduplicar cotações:** se você deduplicar antes de converter as datas, `2026-07-17` e `17/07/2026` parecem registros diferentes.

---

## PARTE 10: Versionamento com branches (GitHub)

Boa prática que o entrevistador vai gostar: **não trabalhe direto na `main`**.

Fluxo para cada etapa (exemplo: silver):

1. **Criar branch** (no Databricks: Git folder → seletor de branch no topo → *Create branch* `feature/silver`).
   Ou no terminal: `git checkout -b feature/silver`.
2. Desenvolver e testar os notebooks.
3. **Commit e push** (no Databricks: botão do Git folder → *Commit & Push*).
4. No GitHub: **Compare & pull request** → descrever o que mudou → **Merge**.
5. Voltar para `main` e **Pull**.

Sugestão de histórico de commits:
```
chore: estrutura inicial do projeto
feat: setup do unity catalog e volume
feat: gerador de dados brutos
feat: ingestao bronze idempotente
feat: silver de empresas
feat: silver de cotacoes
feat: gold dim_empresa com scd2
docs: atualiza readme com arquitetura e linhagem
```

**Conceitos:** *branch* é uma linha paralela de desenvolvimento; *pull request* é o pedido de mesclar uma branch na principal, com revisão; *merge* é a junção.

---

## PARTE 11: Linhagem de dados (Data Lineage)

Quando você criar silver a partir de bronze (via Spark/SQL, dentro do Unity Catalog):

1. **Catalog** → abra uma tabela silver.
2. Aba **Lineage** → **See lineage graph**.
3. Você verá bronze → silver → gold, com as colunas.
4. Tire um print e coloque no README.

Saiba explicar: origem dos dados, transformações, destino e **rastreabilidade** (se um número na gold estiver errado, você segue o caminho de volta até o arquivo original, graças ao `_source_file`).

---

## PARTE 12: Fase SCD (Slowly Changing Dimensions)

**Dimensão** é uma tabela descritiva (empresa, cliente, produto) que muda devagar. **SCD** é como tratar essas mudanças:

| | SCD Tipo 1 | SCD Tipo 2 |
|---|---|---|
| O que faz | **Sobrescreve** o valor antigo | **Cria nova linha** e fecha a antiga |
| Histórico | Perde | Mantém |
| Usar quando | Correção de erro (ex.: nome digitado errado) | A mudança tem significado histórico (ex.: empresa mudou de setor) |

### Plano
1. Rode a célula comentada `ingest("empresas_raw_d2.csv", ...)` do notebook 02 (chega o "dia 2").
2. Limpe o D2 com **a mesma lógica** da silver do D1.
3. Construa `gold.dim_empresa`:
   - **Tipo 1** em `razao_social` (e-mail, telefone): sobrescreve.
   - **Tipo 2** em `setor`, `subsetor` e `situacao`: mantém histórico.
4. Colunas típicas do tipo 2: `sk_empresa` (chave substituta), `id_empresa`, `data_inicio`, `data_fim`, `flag_atual`.
5. Confira com `gabarito/gabarito_mudancas_d2.csv`: devem aparecer mudanças de setor/subsetor, de razão social e cancelamentos.

Esqueleto de `MERGE` para tipo 2 (adapte):
```sql
-- 1) fecha a versao atual das empresas que mudaram
MERGE INTO workspace.gold.dim_empresa AS d
USING workspace.silver.empresas_d2 AS s
ON d.id_empresa = s.id_empresa AND d.flag_atual = true
WHEN MATCHED AND (d.setor <> s.setor OR d.subsetor <> s.subsetor OR d.situacao <> s.situacao)
  THEN UPDATE SET d.flag_atual = false, d.data_fim = current_date();

-- 2) insere a nova versao (e as empresas novas)
INSERT INTO workspace.gold.dim_empresa
SELECT ... FROM workspace.silver.empresas_d2 s
LEFT JOIN workspace.gold.dim_empresa d ON d.id_empresa = s.id_empresa AND d.flag_atual = true
WHERE d.id_empresa IS NULL;
```
Tente escrever você mesmo. Se travar, me mande o que fez que eu corrijo com você.

---

## PARTE 13: Azure e ADF (opcional, honesto sobre os limites)

**Fato importante:** a Free Edition **não conecta ao Azure** e o ADF não consegue chamar notebooks dela. Para executar de verdade você precisaria de uma conta Azure (exige cartão, com créditos iniciais para teste) e de um workspace Azure Databricks.

**Recomendação:** não gaste dinheiro para a entrevista. Em vez disso, documente no README "como esse projeto seria no Azure":

| No seu projeto | No Azure |
|---|---|
| Volume `landing` | Container em **ADLS Gen2** (Storage Account com hierarchical namespace) |
| Notebook 01/fonte | Fonte externa (API, banco, SFTP) |
| Ingestão para landing | **ADF** com *Copy Activity* |
| Notebooks bronze/silver/gold | **Databricks Notebook Activity** dentro de um pipeline do ADF |
| Ordem de execução | Dependências entre activities (sucesso → próxima) |
| Agendamento | **Trigger** de agenda (ex.: diário às 02h) |
| Unity Catalog | Igual, com *external locations* apontando para o ADLS |

Conceitos de ADF para saber falar: **pipeline** (fluxo), **activity** (passo), **linked service** (conexão), **dataset** (dado), **trigger** (gatilho), **integration runtime** (quem executa).

Se quiser mais para frente, eu detalho um passo a passo de ADF para você praticar quando tiver acesso.

---

## PARTE 14: Como contar esse projeto na entrevista

### Pitch de 1 minuto
> "Montei um projeto de lakehouse no Databricks com arquitetura medalhão e Unity Catalog. Gerei dados fictícios de empresas da B3 com problemas planejados: duplicatas, nulos disfarçados, datas em vários formatos, tipos inconsistentes. Na bronze, ingeri tudo como string, com metadados e de forma idempotente. Na silver, tratei tipagem, datas, deduplicação e qualidade. Na gold, modelei uma dimensão com SCD tipo 2 e uma tabela fato. Versionei tudo no GitHub com branches e pull requests, e acompanhei a linhagem pelo Catalog."

### Perguntas que o projeto te prepara para responder
- **"Por que a bronze guarda tudo como string?"** Para não perder nem quebrar a leitura com dado sujo. A interpretação fica para a silver.
- **"O que acontece num JOIN com tipos diferentes?"** Pode retornar zero linhas (`'000123'` ≠ `'123'`), conversões implícitas inesperadas e problemas de performance. A solução é converter para o mesmo tipo antes.
- **"Volume ou tabela?"** Ver tabela da Parte 5.
- **"Serverless vs cluster tradicional?"** Serverless: o Databricks gerencia a infraestrutura, sobe rápido e é bom para trabalho interativo e cargas variáveis. Cluster tradicional: você escolhe o tamanho e as configurações (*all-purpose* para desenvolvimento interativo, *job cluster* para pipelines agendados, que sobe, roda e desliga, sendo mais barato).
- **"SCD 1 ou 2?"** Ver tabela da Parte 12.
- **"Como ingerir 1 bilhão de linhas por dia?"** Pontos para citar: ingestão **incremental** (nunca recarregar tudo), arquivos em formato colunar (Parquet/Delta), **particionar por data**, evitar *small files*, paralelismo na ingestão (ADF com cópia paralela, ou Auto Loader no Databricks), clustering/compactação (`OPTIMIZE`), e monitorar gargalos (skew, shuffle).

### Sobre IA (o chefe mencionou como diferencial)
Seja honesto e mostre critério: *"Usei IA para acelerar (gerar dados, revisar código, tirar dúvidas), mas testei e entendi cada etapa, e sei explicar as decisões."* O Databricks tem o **Assistant** embutido, e vale citar que você o conhece. IA acelera quem entende, e a entrevista vai medir se você entende.

### Para depois (itens da lista do chefe)
- **Airflow:** orquestrar os notebooks (bronze → silver → gold) em uma DAG.
- **Docker:** empacotar o gerador de dados.
- **Kafka:** simular cotações em tempo real (streaming).
- Certificação mais alcançável para júnior: **Databricks Data Engineer Associate**.

---

## PARTE 15: Problemas comuns

| Erro | Causa provável | Solução |
|---|---|---|
| `Path not found` ao salvar CSV | Volume não criado ou catálogo com outro nome | Rode o notebook 00; confira o nome em Catalog |
| `Catalog 'workspace' not found` | Seu catálogo tem outro nome | Troque `workspace` pelo nome certo nos notebooks |
| `_metadata` não encontrado | Rodando em compute sem Unity Catalog | Use **Serverless** |
| Git folder pede autenticação | Token não salvo ou sem permissão | Refaça a Parte 4 (permissão **Contents: Read and write**) |
| Linhas duplicadas após reexecutar a bronze | Tabela criada por versão antiga | `DROP TABLE` e rode de novo |
| Quota excedida / compute desligado | Limite diário da Free Edition | Aguarde até o dia seguinte |

---

## PARTE 16: Cronograma sugerido

| Dia | Atividade |
|---|---|
| 1 | Partes 1 a 5 (GitHub, Git folder, Unity Catalog) |
| 2 | Partes 6 a 8 (gerar dados, bronze, perfilamento) |
| 3 | Silver empresas e cotações (Parte 9) |
| 4 | Gold e linhagem (Partes 9 e 11) |
| 5 | SCD (Parte 12) e README final |
| 6 | Treinar o pitch e as perguntas (Parte 14) |

Quando terminar a bronze, ou se travar em qualquer passo, me mande o resultado (print ou erro) que eu te ajudo. Depois posso revisar sua silver e gold e simular a entrevista com você.
