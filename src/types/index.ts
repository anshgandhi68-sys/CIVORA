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

