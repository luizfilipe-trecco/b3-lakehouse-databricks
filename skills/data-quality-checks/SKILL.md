---
name: data-quality-checks
description: Técnicas e números esperados para validar etapas do pipeline B3 Lakehouse e investigar contagens erradas (reconciliação de nulos, teste por contraexemplo, integridade entre tabelas, regras de negócio). Use após alterar um tratamento, ao conferir uma tabela ou quando um número não bater.
---

# Validação de qualidade

## Técnicas
1. **Número de referência** para o cenário original (confirmar no workspace) para cada etapa (tabelas em `docs/QUALIDADE_DE_DADOS.md`).
2. **Reconciliação:** `nulos antes + problemas conhecidos = nulos depois` (ex.: datas 33 + 13 = 46).
3. **Contraexemplo:** contar quem viola a regra e esperar 0.
4. **Integridade entre tabelas:** `left_anti` e comparação de chaves.
5. **Regra de negócio:** `data_listagem >= data_fundacao`.

## Consultas úteis
```python
df.filter(~F.col("razao_social").endswith("S.A.")).count()                 # 0
cotacoes.join(empresas, "id_empresa", "left_anti").count()                  # 0
chk = cotacoes.join(empresas.select("id_empresa", F.col("ticker").alias("t_cad")), "id_empresa")
chk.filter(F.col("ticker") != F.col("t_cad")).count()                       # 0
```

## Quando um número não bater
1. Não avance. Identifique em qual etapa o valor mudou.
2. Compare com a bronze (que tem o texto original).
3. Procure erro silencioso: valor 100x maior, ticker em minúsculas, JOIN que devolve menos linhas.
4. Corrija na silver, **reexecute do início** e atualize `docs/QUALIDADE_DE_DADOS.md` se a regra mudou.
