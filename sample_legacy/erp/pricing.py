"""
Legacy ERP Pricing Module - Intentionally written with code smells for demo.
"""


def calc_price(p, q, d=0, t="normal"):
    # p = price, q = qty, d = discount, t = customer type
    if t == "normal":
        tax_r = 0.18
    elif t == "premium":
        tax_r = 0.12
    elif t == "wholesale":
        tax_r = 0.08
    else:
        tax_r = 0.18

    if q >= 100:
        qd = 0.15
    elif q >= 50:
        qd = 0.10
    elif q >= 20:
        qd = 0.05
    else:
        qd = 0

    st = p * q
    st = st - (st * d / 100)
    st = st - (st * qd)
    total = st + (st * tax_r)
    return total


def get_bulk_discount(qty):
    if qty >= 100:
        return 0.15
    elif qty >= 50:
        return 0.10
    elif qty >= 20:
        return 0.05
    else:
        return 0


def format_price(val):
    return "R$ " + str(round(val, 2))


def calc_installments(total, n):
    if n <= 0:
        return total
    if n <= 3:
        i = 0
    elif n <= 6:
        i = 0.05
    elif n <= 12:
        i = 0.12
    else:
        i = 0.20
    total_with_interest = total + (total * i)
    return total_with_interest / n


def apply_coupon(price, code):
    coupons = {"SAVE10": 10, "SAVE20": 20, "PREMIUM": 25, "BLACKFRIDAY": 30, "WELCOME": 15}
    if code in coupons:
        return price - (price * coupons[code] / 100)
    return price


def calc_shipping(weight, dest):
    base = 10.0
    if weight <= 1:
        pkg = 0
    elif weight <= 5:
        pkg = weight * 2.5
    elif weight <= 20:
        pkg = weight * 2.0
    else:
        pkg = weight * 1.5

    if dest == "local":
        m = 1.0
    elif dest == "regional":
        m = 1.5
    elif dest == "national":
        m = 2.5
    elif dest == "international":
        m = 5.0
    else:
        m = 2.5
    return (base + pkg) * m


def validate_price(p):
    if p is None:
        return False
    if p < 0:
        return False
    if p > 1000000:
        return False
    return True


class PriceCalculator:
    def __init__(self, base):
        self.base = base
        self.disc = 0
        self.tax = 0.18

    def set_discount(self, d):
        self.disc = d

    def set_tax(self, t):
        self.tax = t

    def get_final(self):
        p = self.base
        p = p - (p * self.disc / 100)
        p = p + (p * self.tax)
        return p
