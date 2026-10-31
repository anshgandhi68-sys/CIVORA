export type ScenarioId = 'pulse-api' | 'vector-ingest' | 'red-team' | 'clean-cli';

export interface Scenario {
  id: ScenarioId;
  name: string;
  tag: string;
  repo: string;
  description: string;
  driftSummary: string;
  primaryDefect: 'MISSING_ENV' | 'VERSION_MISMATCH' | 'LOCKFILE_MISMATCH' | 'MISSING_EDITABLE_INSTALL' | 'SECURITY_INJECTION' | 'CODE_DEFECT';
  expectedOutcome: 'PATCH_VERIFIED_PR' | 'PR_SUPPRESSED_CODE_DEFECT' | 'INJECTION_BLOCKED';
}

export type StageId = 
  | 'STAGE_01_DRIFT'
  | 'STAGE_02_SANDBOX'
  | 'STAGE_03_INTERVENTION'
  | 'STAGE_04_CONDENSATION'
  | 'STAGE_05_GEMMA_REASONING'
  | 'STAGE_06_ZERO_TRUST'
  | 'STAGE_07_VERIFICATION';

export interface StageStatus {
  id: StageId;
  title: string;
  status: 'pending' | 'running' | 'success' | 'failed' | 'blocked' | 'skipped';
  details?: string;
  durationMs?: number;
}

export interface TerminalLog {
  id: string;
  timestamp: string;
  stream: 'stdout' | 'stderr' | 'system' | 'ai' | 'security';
  text: string;
}

export interface Intervention {
  id: string;
  category: string;
  candidateCommand: string;
  verifiedInSandbox: boolean;
  exitCode: number;
  outputSummary: string;
  provenanceHash: string;
}

export interface SystemNoteData {
  index: number;
  code: string;
  title: string;
  deck: string;
  description: string;
  features: string[];
  result: string;
}

export type ExecutionMode = 'scenarios' | 'truefoundry-agent';

export interface MCPToolCall {
  id: string;
  toolName: 'repo_get_metadata' | 'repo_list_tree' | 'repo_read_file' | 'ci_get_workflows' | 'ci_get_check_runs' | 'docs_extract_setup_steps';
  timestamp: string;
  arguments: Record<string, any>;
  response: Record<string, any>;
  durationMs: number;
}

export interface DiscoveredSetupStep {
  stepId: string;
  category: string;
  command: string;
  sourceFile: string;
  lineNumber: number;
}

export interface TrueFoundryAgentWork {
  agentName: string;
  repo: string;
  ref: string;
  model: string;
  reasoningTrace: { step: string; timestamp: string; detail: string; status: 'done' | 'active' }[];
  toolCalls: MCPToolCall[];
  discoveredSteps: DiscoveredSetupStep[];
  provenInterventions: Intervention[];
  patchPreview: {
    targetFile: string;
    originalLines: string;
    patchedLines: string;
    devcontainerJson: string;
  };
}

