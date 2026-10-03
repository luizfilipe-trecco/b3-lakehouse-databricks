# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Camada BRONZE
# MAGIC Regras da bronze: **nao corrigir nada**. Tudo como STRING, com metadados de rastreio.
# MAGIC - `_source_file`: de qual arquivo veio a linha
# MAGIC - `_ingestion_ts`: quando foi ingerida
# MAGIC
# MAGIC A ingestao e **idempotente por arquivo**: rodar de novo nao duplica arquivos ja carregados.

# COMMAND ----------

from pyspark.sql import functions as F

CATALOG = "workspace"
RAW = f"/Volumes/{CATALOG}/bronze/landing/raw"


def ingest(pattern: str, sep: str, table: str):
    full = f"{CATALOG}.bronze.{table}"
    df = (
        spark.read.option("header", True)
        .option("sep", sep)
        .option("encoding", "UTF-8")
        .option("inferSchema", False)          # tudo string: bronze nao interpreta
        .csv(f"{RAW}/{pattern}")
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_ingestion_ts", F.current_timestamp())
    )
    if spark.catalog.tableExists(full):
        ja_carregados = [r[0] for r in spark.table(full).select("_source_file").distinct().collect()]
        df = df.filter(~F.col("_source_file").isin(ja_carregados))
    df.write.mode("append").saveAsTable(full)
    print(f"{full}: {spark.table(full).count()} linhas no total")

# COMMAND ----------

# Cadastro: por enquanto SO o snapshot do dia 1 (o d2 entra na fase de SCD)
ingest("empresas_raw_d1.csv", ";", "empresas_raw")

# COMMAND ----------

# Cotacoes: os 3 meses de uma vez
ingest("cotacoes_raw_*.csv", ",", "cotacoes_raw")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM workspace.bronze.empresas_raw LIMIT 10;

# COMMAND ----------

spark.table(f"{CATALOG}.bronze.empresas_raw").printSchema()

# COMMAND ----------
# MAGIC %md
# MAGIC ## FASE SCD (so depois de terminar silver/gold v1)
# MAGIC Descomente e rode para "chegar o dia 2". Note que o `_source_file` diferencia os snapshots.

# COMMAND ----------

# ingest("empresas_raw_d2.csv", ";", "empresas_raw")
