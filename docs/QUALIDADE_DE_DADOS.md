# Qualidade de dados: problemas, tratamentos e validações

Os problemas foram **planejados** no gerador (`01_gerar_dados_brutos.py`). As contagens abaixo são referências previstas/anotadas nos notebooks, **não resultados medidos nesta auditoria**. Execute as consultas para confirmar; dados e versões diferentes podem produzir outros números.

## Problemas e tratamentos

| Problema | Tabela | Tratamento | Validação esperada |
|---|---|---|---|
| Duplicatas exatas e "quase" iguais | empresas | `trim`/caixa e `row_number` por `id_empresa` (mais recente por `_ingestion_ts`) | 476 → 450; 0 ids repetidos |
| Duplicatas | cotações | `row_number` por (`id_empresa`, `data_pregao`) **depois** de converter | 30.294 → 29.700 (450 × 66 dias) |
| Nulos disfarçados (`N/A`, `N/D`, vazio) | empresas | `limpa_texto` → `NULL` | nulos: fundação 33, listagem 24, valor 40, funcionários 40, e-mail 65, site 106, telefone 129 |
| Datas em 5 formatos (+ "só ano") | empresas | `coalesce` de `try_to_date` | 33+13=46 nulos (fundação); 24+8=32 (listagem) |
| Datas em 3 formatos | cotações | idem | 0 nulos; 2026-07-01 a 2026-09-30 |
| `R$ 1.234,56` e `1234.56` | `valor_mercado` | Regra separada por formato (`F.when(startswith("R$"))`) | 40 nulos; mínimo ≥ 1 milhão |
| Funcionários negativos | empresas | viram `NULL` | 4 negativos (40+4=44 nulos) |
| CNPJ com 13 dígitos | empresas | só dígitos + `cnpj_valido` | 26 inválidos |
| Vírgula decimal em preços | cotações | `replace(',', '.')` + `try_cast double` | fechamento: 308 nulos e 79 negativos antes e depois |
| Preço nulo, zero ou negativo | cotações | **quarentena** com `motivo_rejeicao` | válidas 29.322 + quarentena 378 = 29.700 |
| `id_empresa` string `'000123'` vs int `123` | ambas | `try_cast("int")` | JOIN: o resultado na Bronze depende de coerção implícita de tipos pelo Spark; valide explicitamente. Na Silver, a chave `id_empresa` é tipada para `int`. |
| Ticker em minúsculas (cotações) | cotações | `F.upper` | 450 tickers distintos; 0 divergentes do cadastro |

## Técnicas de validação (usar sempre)

1. **Número esperado**: cada etapa tem uma contagem conhecida.
2. **Reconciliação**: nulos antes + problemas conhecidos = nulos depois.
3. **Contraexemplo**: contar o que viola a regra (ex.: razão social que não termina em `S.A.`); deve ser 0.
4. **Integridade entre tabelas**: `left_anti` cotações sem empresa (0); tickers divergentes (0).
5. **Regra de negócio**: `data_listagem` não pode ser anterior a `data_fundacao` (0).

## Armadilhas conhecidas

- Tirar os pontos de todos os `valor_mercado` multiplica por 100 os valores do formato simples, **sem erro**. Separar os formatos.
- `cast` derruba a execução no modo ANSI; usar `try_cast`.
- Deduplicar antes de limpar/converter deixa escapar quase-duplicatas.
- Uma validação isolada por tabela não pega divergências **entre** tabelas (caso real: 662 tickers).
