# Step-by-Step Developer Integration Tutorial

Follow this 5-minute walkthrough to generate your key, configure your local environment, and make your first authenticated CIVORA AI request.

---

### Step 1: Generate your CIVORA API Key
1. Navigate to the **CIVORA Mission Control / SaaS Command Center**.
2. Click **Developer Platform** in the sidebar.
3. Under the **API Keys** tab, click **CREATE NEW API KEY**.
4. Choose a descriptive name (e.g., `Local Python Tool`) and select **Live** or **Test**.
5. Click **CREATE KEY**.
6. **IMPORTANT:** Copy your secret key immediately (e.g. `civora_sk_live_...`).

---

### Step 2: Configure Environment Variables

```bash
export CIVORA_API_KEY="civora_sk_live_YOUR_KEY_HERE"
export CIVORA_BASE_URL="http://localhost:4000/v1"
```

---

### Step 3: Run the Python Quickstart

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["CIVORA_API_KEY"],
    base_url=os.environ.get("CIVORA_BASE_URL", "http://localhost:4000/v1")
)

response = client.chat.completions.create(
    model="civora-coder",
    messages=[
        {"role": "user", "content": "Write a FastAPI route that streams responses using Server-Sent Events."}
    ]
)

print(response.choices[0].message.content)
```

---

### Step 4: Run the JavaScript Quickstart

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.CIVORA_API_KEY,
  baseURL: process.env.CIVORA_BASE_URL || "http://localhost:4000/v1"
});

const completion = await client.chat.completions.create({
  model: "civora-repository-agent",
  messages: [{ role: "user", content: "Check my repository for documentation drift." }]
});

console.log(completion.choices[0].message.content);
```

---

### Step 5: Handling Rate Limits Gracefully

If you exceed your allowed Requests Per Minute (RPM), CIVORA returns HTTP `429 Too Many Requests`.

```python
import time
from openai import RateLimitError

try:
    resp = client.chat.completions.create(
        model="civora-coder",
        messages=[{"role": "user", "content": "Execute task"}]
    )
except RateLimitError as e:
    print(f"Rate limited by CIVORA API: {e}. Backing off for 5 seconds...")
    time.sleep(5)
```

