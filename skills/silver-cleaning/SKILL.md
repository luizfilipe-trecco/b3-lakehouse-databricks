---
name: silver-cleaning
description: Padrões e armadilhas para escrever ou revisar tratamentos da camada Silver em PySpark neste projeto (limpeza de texto, nulos disfarçados, tipagem com try_cast, datas em vários formatos, valores em formato brasileiro, deduplicação e quarentena). Use ao criar, alterar ou depurar notebooks da silver.
---

# Silver: padrões de limpeza

## Ordem das etapas (importa)
1. Ler a bronze e descartar colunas irrelevantes.
2. `trim` e converter nulos disfarçados (`""`, `N/A`, `N/D`, `NULL`) em `NULL`.
3. Padronizar caixa (`upper` para ticker, situação e UF; `initcap` para nomes).
4. Preferir **`try_cast`** quando houver possibilidade de valor inválido; `cast` pode ser apropriado em dados já validados.
5. Converter datas, números e valores.
6. Deduplicar **depois** de limpar e converter.
7. Separar o que é inválido (quarentena) e validar.
8. Gravar com `mode("overwrite").saveAsTable(...)`.

## Padrões
```python
def limpa_texto(c):
    t = F.trim(F.col(c))
    return F.when(F.upper(t).isin(["", "N/A", "N/D", "NULL"]), None).otherwise(t)

def converte_data(col):  # tenta cada formato; "só ano" vira NULL
    fmts = ["dd/MM/yyyy", "yyyy-MM-dd", "dd-MM-yyyy", "yyyyMMdd", "dd.MM.yyyy"]
    return F.coalesce(*[F.expr(f"try_to_date({col}, '{f}')") for f in fmts])

w = Window.partitionBy("<chave>").orderBy(F.col("_ingestion_ts").desc())
df = df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")
```

## Armadilhas
- `valor_mercado` tem dois formatos (`R$ 1.234,56` e `1234.56`). Aplicar a limpeza BR **somente** quando começa com `R$`; senão o decimal do formato simples é destruído (valor 100x maior, sem erro).
- Preços de cotações: a vírgula é sempre decimal; trocar por ponto é seguro em todas as linhas.
- Ticker deve ser `upper` em empresas **e** cotações (senão o ticker diverge entre tabelas).
- Antes de converter, registre as contagens de referência (nulos, "só ano", negativos) para reconciliar depois.
- Se uma célula falhar, recrie o DataFrame (*Run all above*).
