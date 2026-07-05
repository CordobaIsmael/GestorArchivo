# Agente Financiero Inteligente

## Visión

Crear un Agente Financiero Inteligente cuyo canal principal sea WhatsApp
y que permita registrar ingresos, gastos, préstamos y cuotas mediante
lenguaje natural, audios y comprobantes, con dashboard web y memoria
financiera.

## Objetivos

-   Registro por WhatsApp.
-   IA conversacional.
-   Confirmación antes de guardar.
-   Dashboard web.
-   Multiusuario.
-   Auditoría.
-   Memoria financiera.

## Arquitectura

``` text
WhatsApp
   │
Evolução API
   │
 n8n
   │
FastAPI
   │
Motor Financiero
   │
PostgreSQL + pgvector
   │
Dashboard Next.js
```

## Stack

-   Next.js
-   React
-   Tailwind
-   shadcn/ui
-   FastAPI
-   PostgreSQL
-   SQLAlchemy
-   Alembic
-   n8n
-   Evolução API
-   GPT-5.5
-   Whisper
-   Mistral OCR
-   MinIO
-   Docker

## Roadmap

1.  Infraestructura.
2.  Registro de movimientos.
3.  Dashboard.
4.  Cuotas.
5.  Préstamos.
6.  OCR.
7.  Memoria financiera.
8.  Asistente financiero.

## Objetivo final

Construir un CFO personal capaz de registrar, analizar, aprender y
recomendar decisiones financieras mediante conversación natural.
