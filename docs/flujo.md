# Flujo del agente — Diagrama (Paso 1.1)

> Referencia digital del diagrama dibujado a mano. Es la **misma lógica de la
> guía** pero con las reglas y tools explicitadas para que sea más explicativo.

## Cómo verlo

| Dónde | Cómo |
|---|---|
| **GitHub** | Después del push, al abrir este archivo se renderiza solo |
| **mermaid.live** | Copiar el código del bloque y pegarlo (exporta PNG/SVG) |
| **draw.io** | `Arrange → Insert → Mermaid` → pegar → `Insert` → queda como formas editables para darle diseño propio |

## Diagrama

```mermaid
flowchart TD
    classDef entrada fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef agente fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef pregunta fill:#fef9c3,stroke:#ca8a04,color:#713f12
    classDef decision fill:#ffedd5,stroke:#ea580c,color:#7c2d12
    classDef aprobar fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef escalar fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    classDef info fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef accion fill:#f1f5f9,stroke:#64748b,color:#0f172a

    A(["Cliente escribe: Quiero devolver el pedido PED-001"]):::entrada --> Z
    Z["Agente: ¿qué necesito saber?"]:::agente

    subgraph PREG["1 · Las 4 preguntas"]
        direction LR
        Q1{"¿Existe el pedido?"}:::pregunta
        Q2{"¿Está dentro de plazo?"}:::pregunta
        Q3{"¿Es un producto elegible?"}:::pregunta
        Q4{"¿Cuánto es el monto?"}:::pregunta
    end

    Z --> Q1
    Z --> Q2
    Z --> Q3
    Z --> Q4

    Q1 --> D{"2 · Decisión del agente:<br/>aplica las 6 reglas<br/>de arriba hacia abajo<br/>y se detiene en la primera"}:::decision
    Q2 --> D
    Q3 --> D
    Q4 --> D

    subgraph SALIDAS["3 · Las 3 salidas"]
        direction LR
        ESC["ESCALAR<br/>a un humano"]:::escalar
        INFO["PEDIR INFO<br/>al cliente"]:::info
        APR["APROBAR<br/>automáticamente"]:::aprobar
    end

    D -->|"Reglas 1, 2 y 3"| ESC
    D -->|"Regla 5"| INFO
    D -->|"Reglas 4 y 6"| APR

    ESC --> E1["Justificar motivo<br/>y registrar: actualizar_crm"]:::accion
    ESC --> E2["Avisar al cliente:<br/>notificar_cliente"]:::accion
    INFO --> I1["Preguntar qué falta<br/>y pausar el caso:<br/>notificar_cliente"]:::accion
    APR --> A1["Monto del reembolso:<br/>calcular_reembolso"]:::accion
    APR --> A2["Guía de devolución:<br/>generar_etiqueta"]:::accion
    APR --> A3["Trazabilidad:<br/>actualizar_crm"]:::accion
    APR --> A4["Confirmación al cliente:<br/>notificar_cliente"]:::accion
```

## Tabla de apoyo: regla → salida → tools

| Regla | Condición | Salida | Tools que se ejecutan |
|---|---|---|---|
| 1 | No elegible (plazo/producto) | ESCALAR | actualizar_crm, notificar_cliente |
| 2 | Monto > $100.000 | ESCALAR (aprobación) | actualizar_crm, notificar_cliente |
| 3 | ≥3 devoluciones en 90 días | ESCALAR (fraude) | actualizar_crm, notificar_cliente |
| 4 | Cliente recurrente y monto < $50.000 | APROBAR | calcular_reembolso, generar_etiqueta, actualizar_crm, notificar_cliente |
| 5 | Falta comprobante o descripción | PEDIR INFO | notificar_cliente |
| 6 | Caso estándar | APROBAR | calcular_reembolso, generar_etiqueta, actualizar_crm, notificar_cliente |

Siempre, como primer paso: **consultar_pedido**. Y para enriquecer la decisión:
**validar_politica** + **buscar_casos_similares** (RAG).
