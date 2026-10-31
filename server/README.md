# Setting Up and Deploying the CIVORA AI Chat Backend

This directory provides a lightweight Express Node.js backend for the CIVORA AI Chat widget.

## 1. Local Setup
1. Navigate to the `server` folder:
   ```bash
   cd server
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Add your OpenAI API key or TrueFoundry configuration (optional — if omitted, the built-in CIVORA Knowledge Base responds automatically).

4. Run your server:
   ```bash
   npm start
   ```
   Your endpoint will be available at `http://localhost:3000/api/chat`.

## 2. Deploying to the Cloud (Render / Railway / Fly.io)
You can deploy this server to any cloud host:
- **Render** (render.com):
  1. Create a Web Service connected to this repository (root directory: `server`).
  2. Build command: `npm install`
  3. Start command: `npm start`
  4. Environment Variables: `OPENAI_API_KEY` (optional)
- **Railway** (railway.app):
  1. Deploy from GitHub repository selecting `server` subfolder.

> [!NOTE]
> When deployed to Vercel with the root site, `/api/chat` is also automatically provided as a native Vercel Serverless Function via `api/chat.js`!
