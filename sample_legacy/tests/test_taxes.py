"""Tests for taxes module."""
import pytest
from erp.taxes import (calc_icms, calc_pis_cofins, calc_ipi, calc_iss,
                       calc_total_impostos, is_isento, calc_difal)


class TestCalcICMS:
    def test_intrastate_sp(self):
        assert calc_icms(1000, "SP", "SP") == 180.0

    def test_interstate_sudeste(self):
        assert calc_icms(1000, "SP", "RJ") == 120.0

    def test_interstate_nordeste(self):
        assert calc_icms(1000, "SP", "BA") == 70.0


class TestCalcPisCofins:
    def test_cumulativo(self):
        pis, cofins = calc_pis_cofins(1000, "cumulativo")
        assert pis == 6.5
        assert cofins == 30.0

    def test_nao_cumulativo(self):
        pis, cofins = calc_pis_cofins(1000, "nao_cumulativo")
        assert pis == 16.5
        assert cofins == 76.0


class TestCalcIPI:
    def test_computadores(self):
        assert calc_ipi(1000, "84710000") == 150.0

    def test_isento(self):
        assert calc_ipi(1000, "99990000") == 0.0


class TestCalcISS:
    def test_informatica_sp(self):
        assert calc_iss(1000, "1.01", "SAO PAULO") == 50.0


class TestCalcTotalImpostos:
    def test_completo(self):
        result = calc_total_impostos(1000, "SP", "SP", ncm="84710000")
        assert result["icms"] == 180.0
        assert result["ipi"] == 150.0
        assert result["total"] == 366.5


class TestIsIsento:
    def test_leite(self):
        assert is_isento("04010000", "SP") is True

    def test_computador(self):
        assert is_isento("84710000", "SP") is False

    def test_zona_franca(self):
        assert is_isento("84710000", "AM") is True


class TestCalcDifal:
    def test_mesma_uf(self):
        assert calc_difal(1000, "SP", "SP") == 0.0

    def test_interestadual(self):
        assert calc_difal(1000, "SP", "BA") == 110.0
        