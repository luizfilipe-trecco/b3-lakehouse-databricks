# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Gerador de dados brutos (FICTICIOS) da B3
# MAGIC Gera 3 tipos de arquivo **propositalmente sujos** no Volume `landing`:
# MAGIC - `empresas_raw_d1.csv` (cadastro, separador `;`) - snapshot do dia 1
# MAGIC - `empresas_raw_d2.csv` - snapshot do dia 2, com mudancas (para treinar SCD depois)
# MAGIC - `cotacoes_raw_YYYYMM.csv` (separador `,`) - cotacoes diarias, 1 arquivo por mes
# MAGIC
# MAGIC Todos os dados sao inventados. Tickers e nomes nao representam empresas reais.

# COMMAND ----------

import os, random, string
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

OUT_DIR = os.environ.get("OUT_DIR", "/Volumes/workspace/bronze/landing/raw")
GABARITO_DIR = os.environ.get("GABARITO_DIR", "/Volumes/workspace/bronze/landing/gabarito")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(GABARITO_DIR, exist_ok=True)

SEED = 42
rng = random.Random(SEED)
nrng = np.random.default_rng(SEED)
N_EMPRESAS = 450

# COMMAND ----------
# MAGIC %md
# MAGIC ## 1. Base LIMPA (a "verdade") - ainda sem sujeira

# COMMAND ----------

SETORES = {
    "Financeiro": ["Bancos", "Seguros", "Servicos Financeiros"],
    "Energia Eletrica": ["Geracao", "Transmissao", "Distribuicao"],
    "Petroleo e Gas": ["Exploracao", "Refino", "Distribuicao de Gas"],
    "Materiais Basicos": ["Mineracao", "Siderurgia", "Papel e Celulose"],
    "Consumo Ciclico": ["Varejo", "Vestuario", "Viagens e Lazer"],
    "Consumo Nao Ciclico": ["Alimentos", "Bebidas", "Agropecuaria"],
    "Saude": ["Hospitais", "Medicamentos", "Diagnosticos"],
    "Tecnologia da Informacao": ["Software", "Hardware", "Servicos de TI"],
    "Utilidade Publica": ["Saneamento", "Agua", "Gas"],
    "Bens Industriais": ["Maquinas", "Transporte", "Construcao"],
    "Comunicacoes": ["Telecom", "Midia"],
}
PRE1 = ["Aurora", "Horizonte", "Brasil", "Atlantica", "Cruzeiro", "Planalto", "Vale", "Serra", "Litoral", "Nova",
        "Sol", "Rio", "Imperial", "Central", "Pioneira", "Guarani", "Tupi", "Amazonia", "Pampa", "Minas"]
PRE2 = ["Norte", "Sul", "Leste", "Oeste", "Prime", "Global", "Unida", "Forte", "Real", "Alfa",
        "Delta", "Omega", "Brasileira", "Nacional", "Integrada"]
CIDADES = [("SP", "Sao Paulo"), ("RJ", "Rio de Janeiro"), ("MG", "Belo Horizonte"), ("RS", "Porto Alegre"),
           ("PR", "Curitiba"), ("BA", "Salvador"), ("SC", "Florianopolis"), ("PE", "Recife"),
           ("DF", "Brasilia"), ("CE", "Fortaleza")]
SEGMENTOS = ["Novo Mercado", "Nivel 1", "Nivel 2", "Basico", "Bovespa Mais"]


def gerar_base(n):
    tickers, nomes, rows = set(), set(), []
    for i in range(1, n + 1):
        setor = rng.choice(list(SETORES))
        sub = rng.choice(SETORES[setor])
        while True:
            nome = f"{rng.choice(PRE1)} {rng.choice(PRE2)} {sub} S.A."
            if nome not in nomes:
                nomes.add(nome)
                break
        while True:
            t = "".join(rng.choices(string.ascii_uppercase, k=4))
            if t not in tickers:
                tickers.add(t)
                break
        ticker = t + rng.choice(["3", "3", "4", "11"])
        fundacao = datetime(1900, 1, 1) + timedelta(days=rng.randint(0, 365 * 118))
        ano_list = rng.randint(max(fundacao.year + 1, 1995), 2024)
        uf, cidade = rng.choice(CIDADES)
        rows.append({
            "id_empresa": i,
            "razao_social": nome,
            "nome_pregao": nome.split(" S.A.")[0],
            "ticker": ticker,
            "cnpj": "".join(rng.choices("0123456789", k=14)),
            "setor": setor,
            "subsetor": sub,
            "segmento_listagem": rng.choices(SEGMENTOS, weights=[55, 12, 8, 20, 5])[0],
            "data_fundacao": fundacao,
            "data_listagem": datetime(ano_list, rng.randint(1, 12), rng.randint(1, 28)),
            "valor_mercado": round(float(nrng.lognormal(22, 1.6)), 2),
            "num_funcionarios": int(nrng.lognormal(7, 1.3)),
            "uf": uf,
            "cidade": cidade,
            "site": f"www.{ticker.lower()}.com.br",
            "email_ri": f"ri@{ticker.lower()}.com.br",
            "telefone": f"{rng.randint(11, 99)}9{rng.randint(1000, 9999)}{rng.randint(1000, 9999)}",
            "situacao": rng.choices(["ATIVA", "CANCELADA"], weights=[96, 4])[0],
        })
    return pd.DataFrame(rows)


base = gerar_base(N_EMPRESAS)
print(base.shape)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 2. Funcoes que SUJAM os dados

# COMMAND ----------

FORMATOS_DATA = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y%m%d", "%d.%m.%Y"]


def sujar_data(d, r, p_null=0.04):
    x = r.random()
    if x < p_null:
        return None
    if x < p_null + 0.02:
        return "N/D"
    if x < p_null + 0.04:
        return str(d.year)  # so o ano
    return d.strftime(r.choice(FORMATOS_DATA))


def sujar_texto(s, r):
    estilo = r.choice(["orig", "orig", "upper", "lower", "pad"])
    if estilo == "upper":
        return s.upper()
    if estilo == "lower":
        return s.lower()
    if estilo == "pad":
        return f"  {s} "
    return s


def num_br(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def sujar_cnpj(c, r):
    x = r.random()
    if x < 0.55:
        return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}"
    if x < 0.90:
        return c
    if x < 0.95:
        return f" {c} "
    return c[1:]  # perdeu um digito (invalido)


def sujar_empresas(df, seed):
    r = random.Random(seed)
    out = []
    for row in df.to_dict("records"):
        x = r.random()
        vm = row["valor_mercado"]
        if x < 0.05:
            vm_s = None
        elif x < 0.08:
            vm_s = "N/A"
        elif x < 0.45:
            vm_s = "R$ " + num_br(vm)
        else:
            vm_s = str(vm)
        x = r.random()
        nf = row["num_funcionarios"]
        if x < 0.06:
            nf_s = None
        elif x < 0.09:
            nf_s = "n/d"
        elif x < 0.30:
            nf_s = f"{nf:,}".replace(",", ".")
        elif x < 0.31:
            nf_s = str(-nf)  # outlier invalido
        else:
            nf_s = str(nf)
        seg = row["segmento_listagem"]
        seg_s = r.choice([seg, seg.upper(), seg.lower(), seg]) if r.random() > 0.08 else None
        tel = row["telefone"]
        tel_s = r.choice([f"({tel[:2]}) {tel[2:7]}-{tel[7:]}", tel, f"+55 {tel[:2]} {tel[2:7]}-{tel[7:]}", None])
        mail = row["email_ri"] if r.random() > 0.15 else None
        if mail and r.random() < 0.2:
            mail = mail.upper()
        sit = row["situacao"]
        out.append({
            "id_empresa": row["id_empresa"],
            "razao_social": sujar_texto(row["razao_social"], r),
            "nome_pregao": sujar_texto(row["nome_pregao"], r),
            "ticker": sujar_texto(row["ticker"], r),
            "cnpj": sujar_cnpj(row["cnpj"], r),
            "setor": sujar_texto(row["setor"], r),
            "subsetor": sujar_texto(row["subsetor"], r),
            "segmento_listagem": seg_s,
            "data_fundacao": sujar_data(row["data_fundacao"], r),
            "data_listagem": sujar_data(row["data_listagem"], r),
            "valor_mercado": vm_s,
            "num_funcionarios": nf_s,
            "uf": row["uf"] if r.random() > 0.03 else row["uf"].lower(),
            "cidade": sujar_texto(row["cidade"], r),
            "site": row["site"] if r.random() > 0.2 else None,
            "email_ri": mail,
            "telefone": tel_s,
            "situacao": r.choice([sit, sit.lower(), sit.capitalize(), f" {sit}"]),
            # colunas IRRELEVANTES (ruido)
            "cor_marca": "#%06x" % r.randint(0, 0xFFFFFF),
            "codigo_legado": str(r.randint(100000, 999999)),
            "flag_teste": r.choice(["0", "0", "0", "1", None]),
            "obs_interna": r.choice([None, None, None, "revisar cadastro", "ver com juridico"]),
            "hash_antigo": "%08x" % r.randint(0, 0xFFFFFFFF),
            "versao_layout": "v2.1",
        })
    d = pd.DataFrame(out)
    # DUPLICATAS: 3% exatas + 3% "quase" (mesmo id, texto diferente)
    n = len(d)
    exatas = d.sample(int(n * 0.03), random_state=seed)
    quase = d.sample(int(n * 0.03), random_state=seed + 1).copy()
    quase["razao_social"] = quase["razao_social"].str.upper().apply(lambda s: f" {s}")
    d = pd.concat([d, exatas, quase], ignore_index=True)
    return d.sample(frac=1, random_state=seed).reset_index(drop=True)

# COMMAND ----------
# MAGIC %md
# MAGIC ## 3. Cadastro de empresas - snapshot D1 e D2 (D2 tem mudancas p/ treinar SCD)

# COMMAND ----------

emp_d1 = sujar_empresas(base, seed=1)
emp_d1.to_csv(f"{OUT_DIR}/empresas_raw_d1.csv", sep=";", index=False, encoding="utf-8")

base2 = base.copy()
ids = base2["id_empresa"].tolist()
rng.shuffle(ids)
n = len(ids)
mud_setor = ids[: int(n * 0.10)]
mud_nome = ids[int(n * 0.10): int(n * 0.15)]
cancel = ids[int(n * 0.15): int(n * 0.17)]

novo_setor = {}
for i in mud_setor:
    atual = base2.loc[base2.id_empresa == i, "setor"].iloc[0]
    s = rng.choice([x for x in SETORES if x != atual])
    novo_setor[i] = (s, rng.choice(SETORES[s]))
    base2.loc[base2.id_empresa == i, ["setor", "subsetor"]] = novo_setor[i]
for i in mud_nome:
    base2.loc[base2.id_empresa == i, "razao_social"] = base2.loc[base2.id_empresa == i, "razao_social"].str.replace(
        " S.A.", " Participacoes S.A.", regex=False)
base2.loc[base2.id_empresa.isin(cancel), "situacao"] = "CANCELADA"

emp_d2 = sujar_empresas(base2, seed=2)
emp_d2.to_csv(f"{OUT_DIR}/empresas_raw_d2.csv", sep=";", index=False, encoding="utf-8")

# GABARITO das mudancas D1 -> D2 (nao e dado de entrada! serve para voce conferir seu SCD)
gab = pd.concat([
    pd.DataFrame({"id_empresa": mud_setor, "tipo_mudanca": "setor/subsetor"}),
    pd.DataFrame({"id_empresa": mud_nome, "tipo_mudanca": "razao_social"}),
    pd.DataFrame({"id_empresa": cancel, "tipo_mudanca": "situacao->CANCELADA"}),
])
gab.to_csv(f"{GABARITO_DIR}/gabarito_mudancas_d2.csv", index=False)
print("empresas d1:", emp_d1.shape, "| d2:", emp_d2.shape, "| mudancas esperadas:", len(gab))

# COMMAND ----------
# MAGIC %md
# MAGIC ## 4. Cotacoes diarias (1 arquivo por mes) - com a chave `id_empresa` como STRING com zeros
# MAGIC Proposital: no cadastro `id_empresa` e inteiro, aqui e texto `"000123"`. Treino de JOIN com tipos diferentes.

# COMMAND ----------

dias = pd.bdate_range("2026-07-01", "2026-09-30")
registros = []
for row in base.to_dict("records"):
    p0 = float(nrng.lognormal(3, 0.9))
    ret = nrng.normal(0.0003, 0.02, len(dias))
    fech = p0 * np.cumprod(1 + ret)
    ant = np.concatenate([[p0], fech[:-1]])
    for k, dia in enumerate(dias):
        a = ant[k] * (1 + nrng.normal(0, 0.005))
        f = fech[k]
        mx = max(a, f) * (1 + abs(nrng.normal(0, 0.006)))
        mn = min(a, f) * (1 - abs(nrng.normal(0, 0.006)))
        vol = float(nrng.lognormal(15, 1.2))
        registros.append((row["id_empresa"], row["ticker"], dia, a, mx, mn, f, vol,
                          int(nrng.lognormal(7, 1)), int(vol / f)))

rc = random.Random(7)


def num_sujo(v, p_comma=0.15, p_null=0.0, p_neg=0.0):
    x = rc.random()
    if x < p_null:
        return None
    if x < p_null + p_neg:
        return f"{-abs(v):.2f}"
    s = f"{v:.2f}"
    return s.replace(".", ",") if rc.random() < p_comma else s


def data_cot(d):
    x = rc.random()
    if x < 0.70:
        return d.strftime("%Y-%m-%d")
    if x < 0.95:
        return d.strftime("%d/%m/%Y")
    return d.strftime("%Y%m%d")


linhas = []
for (idemp, tk, dia, a, mx, mn, f, vol, neg, tit) in registros:
    linhas.append({
        "id_empresa": f"{idemp:06d}",  # string com zeros a esquerda
        "ticker": sujar_texto(tk, rc) if rc.random() < 0.12 else tk,
        "data_pregao": data_cot(dia),
        "preco_abertura": num_sujo(a),
        "preco_maximo": num_sujo(mx),
        "preco_minimo": num_sujo(mn),
        "preco_fechamento": num_sujo(f, p_null=0.01, p_neg=0.003),
        "volume_financeiro": num_sujo(vol, p_comma=0.10),
        "qtd_negocios": str(neg),
        "qtd_titulos": str(tit),
        # IRRELEVANTES
        "codigo_bdi": "02",
        "tipo_mercado": "010",
        "moeda": "R$",
        "fator_cotacao": "1",
        "prazo_dias_termo": None,
        "codigo_isin": f"BR{tk}ACNOR0",
        "_mes": dia.strftime("%Y%m"),
    })
cot = pd.DataFrame(linhas)
dup = cot.sample(frac=0.02, random_state=3)
cot = pd.concat([cot, dup], ignore_index=True).sample(frac=1, random_state=4)

for mes, g in cot.groupby("_mes"):
    g.drop(columns="_mes").to_csv(f"{OUT_DIR}/cotacoes_raw_{mes}.csv", index=False, encoding="utf-8")
    print("cotacoes", mes, g.shape)

# COMMAND ----------

print(sorted(os.listdir(OUT_DIR)))
