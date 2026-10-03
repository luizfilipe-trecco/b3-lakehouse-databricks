# Databricks notebook source
# MAGIC %md
# MAGIC # 00 - Setup do Unity Catalog
# MAGIC Cria os schemas das camadas (bronze/silver/gold) e o Volume onde os arquivos brutos "pousam".
# MAGIC
# MAGIC Hierarquia: **catalog.schema.objeto** (tabela, view, volume...)
# MAGIC
# MAGIC > Na Free Edition o catálogo padrão normalmente se chama `workspace`. Confira em *Catalog* no menu lateral.
# MAGIC > Se o seu tiver outro nome, troque `workspace` em todos os notebooks.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT current_catalog(), current_schema();

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.bronze COMMENT 'Dados brutos, exatamente como chegaram';
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.silver COMMENT 'Dados limpos, tipados e deduplicados';
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.gold   COMMENT 'Tabelas analiticas para o negocio';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Volume = pasta governada pelo Unity Catalog para ARQUIVOS (csv, json, parquet, imagens...)
# MAGIC CREATE VOLUME IF NOT EXISTS workspace.bronze.landing COMMENT 'Area de pouso dos arquivos brutos';

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW SCHEMAS IN workspace;
