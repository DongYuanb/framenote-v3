# FrameNote Frontend

React + Vite single-page app that wires up the FrameNote backend APIs. It covers:

- Uploading local videos and triggering processing
- Creating online download tasks
- Checking task status and inspecting aggregated outputs
- Editing / exporting notes (Markdown & PDF)
- Conversational AI helper panel
- After-sales WeChat group entry form

## Quick start

```bash
cd zed-landing-vibe-main
npm install           # requires Node.js >= 18
npm run dev           # start dev server
npm run build         # build production assets
```

The dev server proxies `/api` and `/storage` to `http://localhost:8001`; adjust in `vite.config.ts` if your backend runs elsewhere.

## Key files

- `src/App.tsx` – high-level layout plus feature sections
- `src/lib/api.ts` – helpers for API base coordination
- `src/index.css` – global styles

## Practical tips

- On load the app reads `/api/config` and auto-fills the API base; you can override it in the toolbar (persisted via `localStorage`).
- Export buttons open backend endpoints directly (Markdown / JSON / PDF).
- Chat requests hit `/api/chat/send` with the given task and user identifiers.

## Build output

`npm run build` emits static assets under `dist/`. Mount that directory in FastAPI (`main.py` already checks for `zed-landing-vibe/dist`) to serve the SPA in production.
