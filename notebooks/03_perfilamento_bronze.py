# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Perfilamento (data profiling) da bronze
# MAGIC Antes de limpar, **descubra** o que esta errado. Rode cada query e anote o que encontrou.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 1) Tamanho e duplicatas por chave
# MAGIC SELECT COUNT(*) AS linhas, COUNT(DISTINCT id_empresa) AS empresas_distintas
# MAGIC FROM workspace.bronze.empresas_raw;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 2) Quais ids estao repetidos?
# MAGIC SELECT id_empresa, COUNT(*) AS qtd
# MAGIC FROM workspace.bronze.empresas_raw
# MAGIC GROUP BY id_empresa HAVING COUNT(*) > 1
# MAGIC ORDER BY qtd DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 3) Nulos por coluna (conta tambem strings vazias e 'N/A', 'N/D', 'n/d')
# MAGIC SELECT
# MAGIC   SUM(CASE WHEN data_fundacao IS NULL OR upper(trim(data_fundacao)) IN ('', 'N/D', 'N/A') THEN 1 ELSE 0 END) AS fundacao_vazia,
# MAGIC   SUM(CASE WHEN valor_mercado IS NULL OR upper(trim(valor_mercado)) IN ('', 'N/D', 'N/A') THEN 1 ELSE 0 END) AS vm_vazio,
# MAGIC   SUM(CASE WHEN num_funcionarios IS NULL OR upper(trim(num_funcionarios)) IN ('', 'N/D', 'N/A') THEN 1 ELSE 0 END) AS func_vazio,
# MAGIC   SUM(CASE WHEN email_ri IS NULL THEN 1 ELSE 0 END) AS email_nulo
# MAGIC FROM workspace.bronze.empresas_raw;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 4) Valores distintos que "deveriam ser iguais" (maiuscula/minuscula/espacos)
# MAGIC SELECT setor, COUNT(*) AS qtd FROM workspace.bronze.empresas_raw GROUP BY setor ORDER BY setor;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT DISTINCT situacao, length(situacao) AS tamanho FROM workspace.bronze.empresas_raw;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 5) Formatos de data diferentes: classifique pelo "formato"
# MAGIC SELECT
# MAGIC   CASE
# MAGIC     WHEN data_fundacao RLIKE '^[0-9]{2}/[0-9]{2}/[0-9]{4}$' THEN 'dd/MM/yyyy'
# MAGIC     WHEN data_fundacao RLIKE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' THEN 'yyyy-MM-dd'
# MAGIC     WHEN data_fundacao RLIKE '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' THEN 'dd-MM-yyyy'
# MAGIC     WHEN data_fundacao RLIKE '^[0-9]{8}$'                   THEN 'yyyyMMdd'
# MAGIC     WHEN data_fundacao RLIKE '^[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}$' THEN 'dd.MM.yyyy'
# MAGIC     WHEN data_fundacao RLIKE '^[0-9]{4}$'                   THEN 'so ano'
# MAGIC     ELSE 'outro/nulo'
# MAGIC   END AS formato, COUNT(*) AS qtd
# MAGIC FROM workspace.bronze.empresas_raw GROUP BY 1 ORDER BY qtd DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 6) Formatos de CNPJ (esperado: 14 digitos sem pontuacao)
# MAGIC SELECT length(regexp_replace(cnpj, '[^0-9]', '')) AS qtd_digitos, COUNT(*) AS qtd
# MAGIC FROM workspace.bronze.empresas_raw GROUP BY 1 ORDER BY 1;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 7) Valor de mercado: quais formatos existem?
# MAGIC SELECT valor_mercado FROM workspace.bronze.empresas_raw
# MAGIC WHERE valor_mercado LIKE 'R$%' OR valor_mercado IN ('N/A') LIMIT 10;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 8) COTACOES: precos com virgula decimal, negativos e nulos
# MAGIC SELECT
# MAGIC   SUM(CASE WHEN preco_fechamento LIKE '%,%' THEN 1 ELSE 0 END) AS com_virgula,
# MAGIC   SUM(CASE WHEN preco_fechamento LIKE '-%' THEN 1 ELSE 0 END)  AS negativos,
# MAGIC   SUM(CASE WHEN preco_fechamento IS NULL THEN 1 ELSE 0 END)    AS nulos
# MAGIC FROM workspace.bronze.cotacoes_raw;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 9) Duplicatas em cotacoes: mesma empresa + mesmo dia (cuidado: a data tem formatos diferentes!)
# MAGIC SELECT id_empresa, data_pregao, COUNT(*) AS qtd
# MAGIC FROM workspace.bronze.cotacoes_raw
# MAGIC GROUP BY id_empresa, data_pregao HAVING COUNT(*) > 1 LIMIT 20;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- 10) A ARMADILHA DO JOIN: em cotacoes o id vem como '000123' e em empresas como '123'.
# MAGIC -- Rode e veja o resultado (esperado: 0 linhas!). Descubra o porque e conserte na silver com CAST para INT.
# MAGIC SELECT COUNT(*) AS linhas_no_join
# MAGIC FROM workspace.bronze.cotacoes_raw c
# MAGIC JOIN workspace.bronze.empresas_raw e ON c.id_empresa = e.id_empresa;
