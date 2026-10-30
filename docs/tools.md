# Contratos de las 7 tools

> Cada tool es un acuerdo de **entrada → salida**. Si todos respetan el contrato,
> el interior de una tool puede cambiarse sin romper al resto del equipo.

| Tool | Entrada | Salida | Regla que activa |
| :--- | :--- | :--- | :--- |
| consultar_pedido | pedido_id: str | dict con pedido | siempre |
| validar_politica | pedido_id, motivo | {elegible, razon} | elegibilidad |
| calcular_reembolso | pedido_id, tipo | {monto, moneda} | reembolso |
| generar_etiqueta | pedido_id | {codigo, url} | logística |
| actualizar_crm | pedido_id, estado | {ok} | trazabilidad |
| notificar_cliente | cliente_id, mensaje | {ok} | comunicación |
| buscar_casos_similares | texto | list[dict] | RAG |

## 🛑 Error común que evita este documento

**Síntoma:** al programar, una tool necesita un dato que ninguna otra tool entrega.
**Causa raíz:** los contratos no se definieron antes de escribir código.
**Solución:** revisar que **cada salida alimente alguna entrada** de otra tool,
con la tabla a la vista.
