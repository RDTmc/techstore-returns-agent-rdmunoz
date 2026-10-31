"""Tests de las tools."""

import pytest

from agent.tools.consultar_pedido import consultar_pedido


def test_consultar_pedido_existente():
    r = consultar_pedido.invoke({"pedido_id": "PED-001"})
    assert "error" not in r
    assert r["pedido_id"] == "PED-001"
    assert r["monto"] > 0


def test_consultar_pedido_inexistente():
    r = consultar_pedido.invoke({"pedido_id": "PED-999"})
    assert "error" in r