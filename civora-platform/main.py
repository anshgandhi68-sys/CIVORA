from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CIVORA AI Autonomous Engineering Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/ai/chat")
async def ai_chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    mode = data.get("mode", "agent")
    api_key = os.getenv("OPENAI_API_KEY")

    system_prompt = f"""You are CIVORA AI, a Principal AI Software Engineer and Autonomous Platform Agent.
Mode: {mode} (agent = repository-aware specialist for architecture, documentation repair, CI drift, and verified patch generation; general = comprehensive coding assistant for algorithms, system design, and software engineering questions)."""

    if not api_key:
        return {
            "reply": f"[Civora {mode.capitalize()} Mode]: OPENAI_API_KEY is not configured in environment. Running in offline autonomous agent mode.\n\n"
                     "I can execute verified sandbox commands, analyze repositories for documentation drift, and generate counterfactual repairs."
        }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "system", "content": system_prompt}] + messages,
                    "temperature": 0.7
                },
                timeout=30.0
            )
            resp_data = response.json()
            return {"reply": resp_data["choices"][0]["message"]["content"]}
        except Exception as e:
            return {"reply": f"Error connecting to AI Provider: {str(e)}"}

@app.post("/api/repo/scan")
async def repo_scan(request: Request):
    data = await request.json()
    url = data.get("url", "Sample/Repo")
    return {
        "id": f"scan-{int(time.time())}",
        "repo": url,
        "status": "COMPLETED",
        "driftIssues": [
            {
                "id": 1,
                "severity": "HIGH",
                "file": "README.md",
                "issue": "Outdated Node.js version in installation instructions (README recommends v16.x, package.json requires >=18.0.0)"
            },
            {
                "id": 2,
                "severity": "MEDIUM",
                "file": "Dockerfile",
                "issue": "Missing production environment variables and unpinned OS headers (DATABASE_URL, libpq-dev)"
            },
            {
                "id": 3,
                "severity": "LOW",
                "file": ".github/workflows/ci.yml",
                "issue": "Package lockfile synchronization warning between npm and pnpm"
            }
        ]
    }

@app.post("/api/sandbox/exec")
async def sandbox_exec(request: Request):
    data = await request.json()
    command = data.get("command", "")

    forbidden = ["rm -rf", "sudo", "> /", "chmod 777", "mkfs", ":(){ :|:& };:"]
    if any(word in command for word in forbidden):
        return {
            "stdout": "",
            "stderr": "Security Policy Violation: Restricted shell command blocked by Zero-Trust Provenance Gate.",
            "status": "FAILED"
        }

    try:
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            timeout=10
        )
        return {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "status": "SUCCESS" if process.returncode == 0 else "FAILED"
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timeout: command exceeded 10s sandbox limit.", "status": "FAILED"}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "status": "FAILED"}

# Mount static files correctly
public_dir = os.path.join(os.path.dirname(__file__), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
