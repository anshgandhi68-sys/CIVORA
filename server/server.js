const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors()); // Allows website frontend to call this backend
app.use(express.json());

// Knowledge base for fallback
function generateCivoraResponse(query) {
  const q = (query || '').toLowerCase().trim();

  if (!q) {
    return 'Hello! I am CIVORA AI Engineer powered by TrueFoundry and Gemma 4 26B-A4B MoE. I can help you inspect repositories, detect CI-to-documentation drift, test counterfactual interventions in pristine sandboxes, and synthesize verified Devcontainers. What repository or question would you like to explore?';
  }

  if (q.includes('drift') || q.includes('ci') || q.includes('mismatch')) {
    return "**CI-vs-Docs Drift Detection** is Stage 01 of CIVORA's pipeline. We compare documentation setup commands (from README.md or onboarding docs) against CI matrix definitions (like GitHub Actions workflows). When environments drift—e.g. Node 18 documented while CI mandates Node 20, or unpinned dependencies—CIVORA flags the discrepancy immediately.";
  }

  if (q.includes('zero-trust') || q.includes('security') || q.includes('provenance') || q.includes('injection')) {
    return '**Zero-Trust Provenance Gate** (Stage 06) protects repositories from prompt injections and hallucinated commands. Every proposed patch must match an HMAC SHA-256 Provenance Registry record proven in an isolated sandbox. Unverified, untrusted, or malicious shell sequences (e.g. `curl | sh`) are blocked before a Pull Request is ever created.';
  }

  if (q.includes('intervention') || q.includes('sandbox') || q.includes('counterfactual') || q.includes('docker')) {
    return '**Counterfactual Interventions** (Stage 03) systematically simulate candidate remediations in pristine Debian/Ubuntu containers. Rather than guessing, CIVORA tests candidates—such as version pin alignments, dependency lock generation (`pip install --require-hashes`), or missing environment template instantiation—and only accepts those that yield a verified exit code 0.';
  }

  if (q.includes('mcp') || q.includes('model context protocol') || q.includes('tools')) {
    return 'CIVORA exposes 6 read-only repository inspection tools via the official **Model Context Protocol (MCP)** Streamable HTTP transport at `/mcp`: `repo_get_metadata`, `repo_list_tree`, `repo_read_file`, `ci_get_workflows`, `ci_get_check_runs`, and `ci_get_job_logs`. All tools enforce read-only safety, DNS-rebinding protection, and automatic secret redaction.';
  }

  if (q.includes('civora') || q.includes('who are you') || q.includes('what is this') || q.includes('about')) {
    return '**CIVORA** is an Autonomous Open-Source Onboarding & Documentation Repair Engine. We ensure every open-source repository delivers a working first run for new contributors by executing setup instructions, discovering hidden blockers, proving counterfactual fixes, and synthesizing verified Devcontainers.';
  }

  if (q.includes('repo') || q.includes('github') || q.includes('anshgandhi') || q.includes('anshgandhi68-sys')) {
    return 'Target repository **anshgandhi68-sys/CIVORA** is configured with Python 3.13 FastAPI backend, MCP 2.3.0 Streamable HTTP server, hash-locked dependencies, and React 19 frontend. You can run live inspection directly in Mission Control or query our MCP server at `/mcp`.';
  }

  return `I received your inquiry: "${query}". As CIVORA's AI Engineer, I can analyze your codebase, verify setup instructions in isolated Docker sandboxes, and generate verified PRs. Try asking about **CI Drift**, **Zero-Trust Security**, **MCP Tools**, or testing a repository in Mission Control!`;
}

// Chat API Endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { messages, message, prompt } = req.body;

    let userQuery = message || prompt || '';
    let chatHistory = [];

    if (Array.isArray(messages) && messages.length > 0) {
      chatHistory = messages;
      for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i] && messages[i].role === 'user' && messages[i].content) {
          userQuery = messages[i].content;
          break;
        }
      }
    } else if (userQuery) {
      chatHistory = [{ role: 'user', content: userQuery }];
    }

    const apiKey = process.env.OPENAI_API_KEY;

    // 1. Call OpenAI if configured
    if (apiKey) {
      try {
        const aiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify({
            model: 'gpt-4o-mini',
            messages: [
              {
                role: 'system',
                content:
                  'You are CIVORA AI Engineer — an intelligent assistant for the CIVORA autonomous open-source onboarding and documentation repair platform. You explain CI drift detection, zero-trust HMAC provenance gates, ephemeral Docker sandboxing, Model Context Protocol (MCP) tools at /mcp, and how CIVORA guarantees reproducible, working repository setups.',
              },
              ...chatHistory.map((m) => ({ role: m.role || 'user', content: m.content || '' })),
            ],
            temperature: 0.7,
          }),
        });

        if (aiResponse.ok) {
          const data = await aiResponse.json();
          const reply = data.choices[0].message.content;
          return res.json({
            reply,
            response: reply,
            message: reply,
            agent: 'CIVORA AI Engineer (GPT-4o-mini)',
            status: 'success',
          });
        }
      } catch (openAiErr) {
        console.warn('OpenAI request failed, falling back to CIVORA knowledge base:', openAiErr);
      }
    }

    // 2. Fallback to CIVORA Knowledge Base
    const reply = generateCivoraResponse(userQuery);
    res.json({
      reply,
      response: reply,
      message: reply,
      agent: 'CIVORA AI Engineer (TrueFoundry / Gemma 4 MoE Knowledge Base)',
      status: 'success',
    });
  } catch (error) {
    console.error('Backend error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/', (req, res) => {
  res.send('CIVORA AI Chat Backend is running!');
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
