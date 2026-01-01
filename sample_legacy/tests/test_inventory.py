"""Tests for inventory module."""
import pytest
from erp.inventory import (add_product, remove_product, update_qty, get_qty, get_product,
                           check_stock, reserve_stock, release_reserve, confirm_reserve,
                           list_low_stock, calc_total_value, get_movements, clear_all)


@pytest.fixture(autouse=True)
def clean():
    clear_all()
    yield
    clear_all()


class TestAddProduct:
    def test_add(self):
        assert add_product("P001", "Product 1", 100, 10.0) is True
        assert get_qty("P001") == 100

    def test_creates_movement(self):
        add_product("P001", "Product 1", 50, 10.0)
        assert len(get_movements(cod="P001")) == 1


class TestRemoveProduct:
    def test_existing(self):
        add_product("P001", "Product 1", 100, 10.0)
        assert remove_product("P001") is True
        assert get_product("P001") is None

    def test_nonexistent(self):
        assert remove_product("INVALID") is False


class TestUpdateQty:
    def test_entrada(self):
        add_product("P001", "Product 1", 100, 10.0)
        update_qty("P001", 50, "entrada")
        assert get_qty("P001") == 150

    def test_saida(self):
        add_product("P001", "Product 1", 100, 10.0)
        update_qty("P001", 30, "saida")
        assert get_qty("P001") == 70

    def test_insuficiente(self):
        add_product("P001", "Product 1", 10, 10.0)
        assert update_qty("P001", 50, "saida") is False


class TestCheckStock:
    def test_sufficient(self):
        add_product("P001", "Product 1", 100, 10.0)
        assert check_stock("P001", 50) is True

    def test_insufficient(self):
        add_product("P001", "Product 1", 10, 10.0)
        assert check_stock("P001", 50) is False


class TestReservations:
    def test_reserve(self):
        add_product("P001", "Product 1", 100, 10.0)
        assert reserve_stock("P001", 30, "PED001") is True

    def test_reserve_affects_availability(self):
        add_product("P001", "Product 1", 100, 10.0)
        reserve_stock("P001", 80, "PED001")
        assert check_stock("P001", 30) is False

    def test_release(self):
        add_product("P001", "Product 1", 100, 10.0)
        reserve_stock("P001", 80, "PED001")
        release_reserve("P001", "PED001")
        assert check_stock("P001", 100) is True

    def test_confirm(self):
        add_product("P001", "Product 1", 100, 10.0)
        reserve_stock("P001", 30, "PED001")
        confirm_reserve("P001", "PED001")
        assert get_qty("P001") == 70


class TestReports:
    def test_low_stock(self):
        add_product("P001", "Product 1", 5, 10.0)
        assert len(list_low_stock()) == 1

    def test_total_value(self):
        add_product("P001", "Product 1", 10, 100.0)
        add_product("P002", "Product 2", 5, 200.0)
        assert calc_total_value() == 2000.0
