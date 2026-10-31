import React, { useState } from 'react';
import { TrueFoundryAgentWork, MCPToolCall } from '../../types';

interface AgentWorkInspectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  workData: TrueFoundryAgentWork;
}

export const AgentWorkInspectorModal: React.FC<AgentWorkInspectorModalProps> = ({
  isOpen,
  onClose,
  workData,
}) => {
  const [activeTab, setActiveTab] = useState<'reasoning' | 'mcp' | 'steps' | 'interventions' | 'pr'>('reasoning');
  const [selectedToolCall, setSelectedToolCall] = useState<MCPToolCall | null>(
    workData.toolCalls.length > 0 ? workData.toolCalls[0] : null
  );
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(workData, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-md">
      <div
        className="bg-[#040917] border border-white/15 rounded-2xl w-full max-w-5xl h-[85vh] flex flex-col shadow-[0_0_50px_rgba(0,113,255,0.15)] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="h-16 border-b border-white/10 px-6 flex items-center justify-between bg-[#01030F]/80">
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-[#10B981] animate-pulse" />
            <span className="font-mono text-xs font-semibold text-white tracking-wider">
              SHOWING OUR WORK // TRUEFOUNDRY CIVORA ENGINEER AGENT
            </span>
            <span className="font-mono text-[10px] text-[#38BDF8] bg-[#38BDF8]/10 border border-[#38BDF8]/30 px-2 py-0.5 rounded">
              {workData.repo}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleCopyJson}
              className="px-3 py-1.5 rounded text-[11px] font-mono text-white/80 hover:text-white border border-white/10 hover:border-white/20 bg-white/5 transition-all"
            >
              {copied ? '✓ COPIED JSON' : 'EXPORT TELEMETRY'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-colors"
              aria-label="Close modal"
            >
              <svg viewBox="0 0 16 16" className="w-5 h-5 fill-none stroke-currentColor stroke-[1.7]">
                <path d="M3 3l10 10M13 3L3 13" />
              </svg>
            </button>
          </div>
        </div>

        {/* Modal Tabs Navigation */}
        <div className="border-b border-white/10 px-6 flex items-center gap-1 bg-white/[0.01]">
          <button
            type="button"
            onClick={() => setActiveTab('reasoning')}
            className={`py-3 px-4 font-mono text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'reasoning'
                ? 'border-[#0071FF] text-white text-shadow-[0_0_10px_rgba(0,113,255,0.5)]'
                : 'border-transparent text-white/50 hover:text-white/80'
            }`}
          >
            01 / AGENT REASONING TRACE
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('mcp')}
            className={`py-3 px-4 font-mono text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'mcp'
                ? 'border-[#0071FF] text-white text-shadow-[0_0_10px_rgba(0,113,255,0.5)]'
                : 'border-transparent text-white/50 hover:text-white/80'
            }`}
          >
            02 / MCP WIRE TELEMETRY ({workData.toolCalls.length})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('steps')}
            className={`py-3 px-4 font-mono text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'steps'
                ? 'border-[#0071FF] text-white text-shadow-[0_0_10px_rgba(0,113,255,0.5)]'
                : 'border-transparent text-white/50 hover:text-white/80'
            }`}
          >
            03 / EXTRACTED SETUP STEPS
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('interventions')}
            className={`py-3 px-4 font-mono text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'interventions'
                ? 'border-[#0071FF] text-white text-shadow-[0_0_10px_rgba(0,113,255,0.5)]'
                : 'border-transparent text-white/50 hover:text-white/80'
            }`}
          >
            04 / PROVEN INTERVENTIONS
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('pr')}
            className={`py-3 px-4 font-mono text-xs font-semibold border-b-2 transition-all ${
              activeTab === 'pr'
                ? 'border-[#0071FF] text-white text-shadow-[0_0_10px_rgba(0,113,255,0.5)]'
                : 'border-transparent text-white/50 hover:text-white/80'
            }`}
          >
            05 / SYNTHESIZED PR DIFF
          </button>
        </div>

        {/* Modal Tab Content */}
        <div className="flex-1 p-6 overflow-y-auto font-mono text-xs">
          {/* TAB 1: REASONING TRACE */}
          {activeTab === 'reasoning' && (
            <div className="flex flex-col gap-4 max-w-4xl">
              <div className="p-4 bg-white/5 border border-white/10 rounded-xl mb-2 flex items-center justify-between">
                <div>
                  <div className="text-white font-semibold text-sm">{workData.agentName}</div>
                  <div className="text-white/60 text-[11px] mt-0.5">Model Engine: {workData.model}</div>
                </div>
                <div className="text-right">
                  <div className="text-[#10B981] font-semibold text-xs">AUTONOMOUS REASONING ACTIVE</div>
                  <div className="text-white/40 text-[10px]">Zero-Trust Provenance Bound</div>
                </div>
              </div>

              <div className="space-y-3">
                {workData.reasoningTrace.map((r, i) => (
                  <div key={i} className="p-4 rounded-xl border border-white/10 bg-[#01030F] flex items-start gap-4">
                    <div className="w-6 h-6 rounded-full bg-[#0071FF]/20 text-[#38BDF8] border border-[#0071FF]/40 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                      {i + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-white font-semibold text-sm">{r.step}</span>
                        <span className="text-white/40 text-[10px]">{r.timestamp}</span>
                      </div>
                      <p className="text-white/70 leading-relaxed font-sans text-xs">{r.detail}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: MCP WIRE TELEMETRY */}
          {activeTab === 'mcp' && (
            <div className="grid grid-cols-12 gap-6 h-full">
              {/* Tool list */}
              <div className="col-span-5 border-r border-white/10 pr-6 space-y-2.5 overflow-y-auto">
                <span className="text-[11px] text-white/40 uppercase tracking-wider block mb-2 font-semibold">
                  RECORDED MCP TOOL INVOCATIONS
                </span>
                {workData.toolCalls.map((tc) => (
                  <button
                    key={tc.id}
                    type="button"
                    onClick={() => setSelectedToolCall(tc)}
                    className={`w-full p-3 rounded-lg border text-left transition-all ${
                      selectedToolCall?.id === tc.id
                        ? 'border-[#0071FF] bg-[#0071FF]/10 text-white shadow-[0_0_15px_rgba(0,113,255,0.2)]'
                        : 'border-white/10 bg-white/[0.02] text-white/70 hover:border-white/20 hover:text-white'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-xs text-[#38BDF8]">{tc.toolName}</span>
                      <span className="text-[10px] text-white/40">{tc.durationMs}ms</span>
                    </div>
                    <div className="text-[10px] text-white/50 truncate">
                      {tc.timestamp} // Streamable HTTP POST /mcp
                    </div>
                  </button>
                ))}
              </div>

              {/* Tool Payload Inspector */}
              <div className="col-span-7 flex flex-col gap-4 overflow-y-auto">
                {selectedToolCall ? (
                  <>
                    <div className="p-3 bg-white/5 border border-white/10 rounded-lg flex items-center justify-between">
                      <div>
                        <span className="text-white/50 text-[10px]">TOOL NAME:</span>
                        <div className="text-white font-bold text-sm">{selectedToolCall.toolName}</div>
                      </div>
                      <div className="text-right">
                        <span className="text-white/50 text-[10px]">EXECUTION TIME:</span>
                        <div className="text-[#10B981] font-semibold">{selectedToolCall.durationMs}ms</div>
                      </div>
                    </div>

                    <div>
                      <span className="text-[10px] text-white/50 uppercase block mb-1">JSON-RPC 2.0 ARGUMENTS</span>
                      <pre className="p-3 bg-black/60 border border-white/10 rounded-lg text-white/80 overflow-x-auto text-[11px]">
                        {JSON.stringify(selectedToolCall.arguments, null, 2)}
                      </pre>
                    </div>

                    <div>
                      <span className="text-[10px] text-white/50 uppercase block mb-1">MCP SERVER RESPONSE PAYLOAD</span>
                      <pre className="p-3 bg-black/60 border border-white/10 rounded-lg text-[#38BDF8] overflow-x-auto text-[11px] max-h-72">
                        {JSON.stringify(selectedToolCall.response, null, 2)}
                      </pre>
                    </div>
                  </>
                ) : (
                  <div className="h-64 flex items-center justify-center text-white/40">
                    Select a tool call to inspect payload.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: EXTRACTED SETUP STEPS */}
          {activeTab === 'steps' && (
            <div className="flex flex-col gap-4 max-w-4xl">
              <div className="p-4 bg-white/5 border border-white/10 rounded-xl mb-2 flex items-center justify-between">
                <div>
                  <div className="text-white font-semibold text-sm">Deterministic Documentation Parser</div>
                  <div className="text-white/60 text-[11px] mt-0.5">Identified onboarding instructions with exact line numbers</div>
                </div>
                <span className="font-mono text-xs bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 px-2.5 py-1 rounded">
                  {workData.discoveredSteps.length} EXTRACTED STEPS
                </span>
              </div>

              <div className="space-y-2.5">
                {workData.discoveredSteps.map((step) => (
                  <div key={step.stepId} className="p-3.5 rounded-lg border border-white/10 bg-[#01030F] flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="text-[10px] uppercase font-bold text-[#38BDF8] bg-[#38BDF8]/10 px-2 py-0.5 rounded">
                          {step.category}
                        </span>
                        <span className="text-[11px] text-white/50">
                          {step.sourceFile}:{step.lineNumber}
                        </span>
                      </div>
                      <div className="text-white font-medium text-xs bg-black/40 px-2.5 py-1.5 rounded mt-1 border border-white/5">
                        $ {step.command}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: PROVEN INTERVENTIONS */}
          {activeTab === 'interventions' && (
            <div className="flex flex-col gap-4 max-w-4xl">
              <div className="p-4 bg-white/5 border border-white/10 rounded-xl mb-2 flex items-center justify-between">
                <div>
                  <div className="text-white font-semibold text-sm">Counterfactual Sandbox Interventions</div>
                  <div className="text-white/60 text-[11px] mt-0.5">Physical exit-code 0 verification in isolated environment</div>
                </div>
                <span className="font-mono text-xs bg-[#0071FF]/10 text-[#38BDF8] border border-[#0071FF]/30 px-2.5 py-1 rounded">
                  STAGE 03 PROVENANCE REGISTRY
                </span>
              </div>

              <div className="space-y-3">
                {workData.provenInterventions.map((item) => (
                  <div key={item.id} className="p-4 bg-[#01030F] border border-white/10 rounded-xl">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[#10B981] font-bold text-xs uppercase">{item.category}</span>
                      <span className="text-[10px] text-white/40">{item.provenanceHash}</span>
                    </div>
                    <div className="p-2.5 bg-black/60 border border-white/10 rounded-lg text-white font-medium text-xs mb-2">
                      $ {item.candidateCommand}
                    </div>
                    <div className="text-[11px] text-white/70">
                      Sandbox Outcome: <span className="text-[#10B981] font-semibold">Exit Code {item.exitCode}</span> // {item.outputSummary}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: SYNTHESIZED PR DIFF */}
          {activeTab === 'pr' && (
            <div className="flex flex-col gap-6 max-w-4xl">
              {/* README Patch */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-bold text-sm">Target Patch: {workData.patchPreview.targetFile}</span>
                  <span className="text-[10px] text-[#10B981] bg-[#10B981]/10 border border-[#10B981]/30 px-2 py-0.5 rounded">
                    PROVENANCE VERIFIED
                  </span>
                </div>
                <div className="border border-white/10 rounded-xl overflow-hidden bg-[#01030F]">
                  <div className="p-3 bg-red-950/20 border-b border-red-500/20 text-red-300">
                    <div className="text-[10px] text-red-400/80 mb-1">ORIGINAL DRIFTED LINES:</div>
                    <pre className="text-xs">{workData.patchPreview.originalLines}</pre>
                  </div>
                  <div className="p-3 bg-green-950/20 text-green-300">
                    <div className="text-[10px] text-green-400/80 mb-1">PROPOSED VERIFIED REPAIR:</div>
                    <pre className="text-xs">{workData.patchPreview.patchedLines}</pre>
                  </div>
                </div>
              </div>

              {/* Devcontainer Synthesizer */}
              <div>
                <span className="text-white font-bold text-sm block mb-2">Synthesized .devcontainer/devcontainer.json</span>
                <pre className="p-4 bg-black/60 border border-white/10 rounded-xl text-[#38BDF8] text-[11px] overflow-x-auto">
                  {workData.patchPreview.devcontainerJson}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
