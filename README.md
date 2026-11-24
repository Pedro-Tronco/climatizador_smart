# Climatizador Smart

Sistema de telemetria e monitoramento de ocorrências para climatizador integrado com Arduino, com painel web em tempo real, histórico de leituras e resumo de estados.

## Arquitetura

O projeto é orquestrado via Docker Compose (`docker-compose.yaml`) com três serviços:

- **`app` (Backend Python):**
  - Lê os dados seriais do Arduino (`pyserial` via `ARDUINO_PORT`).
  - Persiste ocorrências em banco SQLite em `./data` (`sqlmodel`).
  - Expõe a API REST com **FastAPI / Uvicorn** na porta `8000`.
  - Expõe o servidor WebSocket com **Tornado** na porta `7000`.
- **`frontend` (Painel Web):**
  - Interface estática (`index.html`, `styles.css`, `app.js`) servida por **Nginx** na porta `80`.
  - Três seções principais: **Tempo Real** (status ao vivo via WebSocket e modo tela cheia), **Histórico** (consulta de ocorrências) e **Resumo** (distribuição por estado: `OK`, `WARNING`, `DISABLED`, `INITIALIZING`).
- **`caddy` (Proxy Reverso):**
  - Imagem `caddy:2-alpine` exposta na porta `4000` (`Caddyfile`), roteando:
    - `/ws` → `app:7000`
    - `/api/*` → `app:8000`
    - `/*` → `frontend:80`

## Estrutura do Projeto

```text
climatizador_smart/
├── Caddyfile
├── Dockerfile
├── docker-compose.yaml
├── pyproject.toml
├── .env
├── data/                         # Banco SQLite persistido em volume
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── src/trabalho_g2/
    ├── __init__.py
    ├── database.py
    ├── registry.py
    ├── settings.py
    ├── arduino/
    │   ├── controller.py
    │   └── schemas.py
    └── telemetry/
        ├── controller.py
        ├── protocols.py
        ├── repositories.py
        ├── schemas.py
        ├── services.py
        └── websockets.py
```

## Configuração

Verifique o arquivo `.env` na raiz do projeto com as variáveis necessárias:

```env
ARDUINO_PORT=/dev/ttyUSB0
TZ=America/Sao_Paulo
```

> Ajuste `ARDUINO_PORT` conforme a porta serial onde o Arduino está conectado no host.

## Como Executar

Suba todos os serviços com Docker Compose:

```bash
docker compose up --build -d
```

Após iniciar, acesse o painel em:

- **Painel Web:** `http://localhost:4000`
- **API de Ocorrências:** `GET http://localhost:4000/api/occurrences` (aceita parâmetro opcional `timestamp`)
- **WebSocket:** `ws://localhost:4000/ws`

Para parar os containers:

```bash
docker compose down
```
