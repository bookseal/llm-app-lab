# Frontend (React + Vite)

A minimal React app (plain JavaScript) that fetches a message from the Flask
backend and displays it.

## Install

```bash
cd frontend
npm install
```

## Run

```bash
npm run dev
```

The dev server runs on **http://localhost:5173**.

Requests to `/api/*` are proxied to the Flask backend at
`http://localhost:5001` (see `vite.config.js`), so make sure the backend is
running too.
