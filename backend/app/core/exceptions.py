"""Domain Exception Definitions for CIVORA Core."""

from typing import Any, Optional


class CivoraException(Exception):
    """Base domain exception for CIVORA."""

    def __init__(self, message: str, status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class RepositoryNotFoundError(CivoraException):
    def __init__(self, repo_id: str):
        super().__init__(f"Repository '{repo_id}' not found", status_code=404)


class RunNotFoundError(CivoraException):
    def __init__(self, run_id: str):
        super().__init__(f"Execution run '{run_id}' not found", status_code=404)


class UnauthorizedError(CivoraException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenError(CivoraException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class ProvenanceViolationError(CivoraException):
    def __init__(self, reason: str, details: Optional[Any] = None):
        super().__init__(
            f"Provenance verification gate rejected patch: {reason}",
            status_code=422,
            details=details,
        )


class SandboxExecutionError(CivoraException):
    def __init__(self, step_id: str, exit_code: int, stderr: str):
        super().__init__(
            f"Sandbox execution failed for step '{step_id}' with exit code {exit_code}",
            status_code=500,
            details={"step_id": step_id, "exit_code": exit_code, "stderr": stderr},
        )

