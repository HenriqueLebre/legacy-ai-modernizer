"""Tests for pricing module - ensures modernization doesn't break behavior."""
import pytest
from erp.pricing import (calc_price, get_bulk_discount, format_price, calc_installments,
                         apply_coupon, calc_shipping, validate_price, PriceCalculator)


class TestCalcPrice:
    def test_basic_no_discount(self):
        assert calc_price(100, 1) == 118.0

    def test_with_manual_discount(self):
        assert calc_price(100, 1, d=10) == 106.2

    def test_with_quantity_discount(self):
        assert calc_price(10, 50) == 531.0

    def test_premium_customer(self):
        assert calc_price(100, 1, t="premium") == 112.0

    def test_wholesale_customer(self):
        assert calc_price(100, 1, t="wholesale") == 108.0


class TestBulkDiscount:
    def test_no_discount(self):
        assert get_bulk_discount(10) == 0

    def test_5_percent(self):
        assert get_bulk_discount(20) == 0.05

    def test_10_percent(self):
        assert get_bulk_discount(50) == 0.10

    def test_15_percent(self):
        assert get_bulk_discount(100) == 0.15


class TestFormatPrice:
    def test_basic(self):
        assert format_price(100) == "R$ 100"

    def test_decimal(self):
        assert format_price(99.99) == "R$ 99.99"


class TestCalcInstallments:
    def test_zero_installments(self):
        assert calc_installments(100, 0) == 100

    def test_3_no_interest(self):
        assert calc_installments(300, 3) == 100.0

    def test_6_with_interest(self):
        assert calc_installments(100, 6) == 17.5


class TestApplyCoupon:
    def test_valid_save10(self):
        assert apply_coupon(100, "SAVE10") == 90.0

    def test_invalid(self):
        assert apply_coupon(100, "INVALID") == 100.0


class TestCalcShipping:
    def test_local_light(self):
        assert calc_shipping(0.5, "local") == 10.0

    def test_national_heavy(self):
        assert calc_shipping(10, "national") == 75.0


class TestValidatePrice:
    def test_valid(self):
        assert validate_price(100) is True

    def test_none(self):
        assert validate_price(None) is False

    def test_negative(self):
        assert validate_price(-10) is False


class TestPriceCalculator:
    def test_basic(self):
        assert PriceCalculator(100).get_final() == 118.0

    def test_with_discount(self):
        calc = PriceCalculator(100)
        calc.set_discount(10)
        assert calc.get_final() == 106.2
