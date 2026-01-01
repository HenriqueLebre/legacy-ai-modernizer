"""
Legacy ERP Inventory Module - Stock management with global state (bad practice).
"""

estoque = {}
reservas = {}
mov_history = []


def add_product(cod, nome, qtd, preco):
    global estoque
    estoque[cod] = {"nome": nome, "qtd": qtd, "preco": preco, "min": 10, "max": 1000}
    mov_history.append({"tipo": "ENTRADA", "cod": cod, "qtd": qtd, "data": "2024-01-01"})
    return True


def remove_product(cod):
    global estoque
    if cod in estoque:
        del estoque[cod]
        return True
    return False


def update_qty(cod, qtd, tipo="entrada"):
    global estoque
    if cod not in estoque:
        return False
    if tipo == "entrada":
        estoque[cod]["qtd"] += qtd
        mov_tipo = "ENTRADA"
    elif tipo == "saida":
        if estoque[cod]["qtd"] < qtd:
            return False
        estoque[cod]["qtd"] -= qtd
        mov_tipo = "SAIDA"
    else:
        return False
    mov_history.append({"tipo": mov_tipo, "cod": cod, "qtd": qtd, "data": "2024-01-01"})
    return True


def get_qty(cod):
    return estoque[cod]["qtd"] if cod in estoque else 0


def get_product(cod):
    return estoque.get(cod)


def check_stock(cod, qtd_necessaria):
    if cod not in estoque:
        return False
    disponivel = estoque[cod]["qtd"]
    if cod in reservas:
        for r in reservas[cod]:
            disponivel -= r["qtd"]
    return disponivel >= qtd_necessaria


def reserve_stock(cod, qtd, pedido_id):
    global reservas
    if not check_stock(cod, qtd):
        return False
    if cod not in reservas:
        reservas[cod] = []
    reservas[cod].append({"pedido": pedido_id, "qtd": qtd, "data": "2024-01-01"})
    return True


def release_reserve(cod, pedido_id):
    global reservas
    if cod not in reservas:
        return False
    for i, r in enumerate(reservas[cod]):
        if r["pedido"] == pedido_id:
            reservas[cod].pop(i)
            return True
    return False


def confirm_reserve(cod, pedido_id):
    global reservas
    if cod not in reservas:
        return False
    for i, r in enumerate(reservas[cod]):
        if r["pedido"] == pedido_id:
            qtd = r["qtd"]
            reservas[cod].pop(i)
            return update_qty(cod, qtd, "saida")
    return False


def list_low_stock():
    return [{"cod": c, "nome": p["nome"], "qtd": p["qtd"], "min": p["min"]}
            for c, p in estoque.items() if p["qtd"] < p["min"]]


def list_overstock():
    return [{"cod": c, "nome": p["nome"], "qtd": p["qtd"], "max": p["max"]}
            for c, p in estoque.items() if p["qtd"] > p["max"]]


def calc_total_value():
    return sum(p["qtd"] * p["preco"] for p in estoque.values())


def get_movements(cod=None, tipo=None):
    result = []
    for mov in mov_history:
        if cod and mov["cod"] != cod:
            continue
        if tipo and mov["tipo"] != tipo:
            continue
        result.append(mov)
    return result


def clear_all():
    global estoque, reservas, mov_history
    estoque, reservas, mov_history = {}, {}, []
