"""
Legacy ERP Tax Module - Brazilian fiscal system (ICMS, PIS, COFINS, IPI).
"""

icms_rates = {"SP": 18, "RJ": 20, "MG": 18, "RS": 17, "PR": 18, "SC": 17, "BA": 18, "PE": 18}
pis_rate = 1.65
cofins_rate = 7.6


def calc_icms(valor, uf_origem, uf_destino):
    if uf_origem == uf_destino:
        r = icms_rates.get(uf_origem, 18)
        return valor * r / 100
    else:
        if uf_destino in ["SP", "RJ", "MG", "PR", "RS", "SC"]:
            r = 12
        else:
            r = 7
        return valor * r / 100


def calc_pis_cofins(valor, tipo="cumulativo"):
    if tipo == "cumulativo":
        pis = valor * 0.65 / 100
        cofins = valor * 3.0 / 100
    elif tipo == "nao_cumulativo":
        pis = valor * pis_rate / 100
        cofins = valor * cofins_rate / 100
    else:
        pis = valor * 0.65 / 100
        cofins = valor * 3.0 / 100
    return pis, cofins


def calc_ipi(valor, ncm):
    ncm_rates = {"8471": 15, "8443": 10, "9403": 5, "6403": 10, "2203": 40, "2402": 300}
    ncm_prefix = str(ncm)[:4]
    rate = ncm_rates.get(ncm_prefix, 0)
    return valor * rate / 100


def calc_iss(valor, cod_servico, municipio="SAO PAULO"):
    if municipio == "SAO PAULO":
        if cod_servico.startswith("1"):
            r = 5.0
        elif cod_servico.startswith("17"):
            r = 2.0
        else:
            r = 5.0
    else:
        r = 5.0
    return valor * r / 100


def calc_total_impostos(valor, uf_o, uf_d, ncm=None, tipo_pis="cumulativo"):
    result = {}
    result["icms"] = calc_icms(valor, uf_o, uf_d)
    pis, cofins = calc_pis_cofins(valor, tipo_pis)
    result["pis"] = pis
    result["cofins"] = cofins
    result["ipi"] = calc_ipi(valor, ncm) if ncm else 0
    result["total"] = result["icms"] + result["pis"] + result["cofins"] + result["ipi"]
    return result


def is_isento(ncm, uf):
    isentos_ncm = ["0401", "0402", "1001", "1005"]
    ncm_prefix = str(ncm)[:4]
    if ncm_prefix in isentos_ncm:
        return True
    if uf == "AM" and ncm_prefix.startswith("84"):
        return True
    return False


def calc_difal(valor, uf_origem, uf_destino, consumidor_final=True):
    if not consumidor_final or uf_origem == uf_destino:
        return 0
    aliq_interna = icms_rates.get(uf_destino, 18)
    aliq_inter = 12 if uf_destino in ["SP", "RJ", "MG", "PR", "RS", "SC"] else 7
    diff = aliq_interna - aliq_inter
    return valor * diff / 100 if diff > 0 else 0
