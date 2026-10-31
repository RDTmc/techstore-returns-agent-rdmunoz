"""Tool: consulta un pedido por ID en SQLite."""

import sqlite3

from langchain_core.tools import tool

from config.settings import DB_PATH


@tool
def consultar_pedido(pedido_id: str) -> dict:
    """Consulta los datos de un pedido por su ID.

    Devuelve un dict con producto, monto, fecha_compra, estado y cliente_id.
    Si el pedido no existe, devuelve {'error': '...'}.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM pedidos WHERE pedido_id = ?", (pedido_id,)
    ).fetchone()
    conn.close()
    if not row:
        return {"error": f"Pedido {pedido_id} no encontrado"}
    return dict(row)


if __name__ == "__main__":
    print(consultar_pedido.invoke({"pedido_id": "PED-001"}))