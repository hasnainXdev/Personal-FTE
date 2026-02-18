# Implementation Plan: AI Employee Vault — Bronze Tier

**Branch**: `001-ai-employee-vault` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)

## Summary

Build a minimum viable autonomous AI Employee system that operates locally within an Obsidian vault, capable of monitoring input sources (Gmail or filesystem), organizing information into structured task states (Inbox → Needs_Action → Done), and executing defined agent skills. The system runs entirely locally via Qwen CLI and UV-managed Python environment, with all actions logged to Dashboard.md for observability.

---

## Technical Context

**Language/Version**: Python 3.11+ (verified: UV 0.9.13 available)

**Primary Dependencies**:
- `watchdog` (>=4.0.0) - Cross-platform filesystem monitoring
- `pydantic` (>=2.0.0) - Data validation and settings management
- `rich` (>=13.0.0) - CLI output formatting
- `typer` (>=0.9.0) - CLI interface
- `markdown` (>=3.5.0) - Markdown parsing/generation

**Storage**: Filesystem-based (Obsidian vault structure)
- No database required for Bronze tier
- Markdown files in state folders: `Inbox/`, `Needs_Action/`, `Done/`
- Configuration in `.ai_employee/config.json`
- Idempotency registry in `.ai_employee/processed.json`

**Testing**: pytest with pytest-asyncio
- Unit tests: Individual service functions
- Integration tests: Vault operations, watcher integration
- Contract tests: Agent skill input/output validation

**Target Platform**: Linux (WSL2 compatible)
- User environment verified: WSL2 on Windows
- Filesystem monitoring via inotify backend
- POSIX file locking with `fcntl`

**Project Type**: Single Python project (CLI-first)
- No frontend/backend split
- Exposed via CLI commands: `ai-employee start|status|process`
- Qwen CLI integration for AI-powered operations

**Performance Goals**:
- Input detection latency: <30 seconds (per SC-003)
- File operations: <1 second per operation
- Concurrent operations: Support up to 5 (per spec)
- Memory usage: <200MB during normal operation

**Constraints**:
- All processing must occur locally (no cloud APIs except Gmail IMAP)
- No external data transmission (privacy requirement)
- Must work within Qwen CLI execution model
- UV-managed Python environment for reproducibility
- Max 1GB vault size, 50 daily inputs (per spec)

**Scale/Scope**:
- Max vault size: 1GB
- Daily input volume: 50 inputs
- Concurrent operations: 5
- File count: Up to 10,000 markdown files
- Single-user personal automation (Bronze tier)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Justification |
|-----------|--------|---------------|
| **Standalone Library** | ✅ PASS | `ai_employee` is self-contained Python package with clear boundaries |
| **CLI Interface** | ✅ PASS | Exposes `ai-employee start|status|process` commands with text I/O |
| **Test-First (TDD)** | ✅ PASS | All implementation will follow Red-Green-Refactor cycle |
| **Integration Testing** | ✅ PASS | Contract tests for skills, integration tests for vault operations |
| **Observability** | ✅ PASS | Dashboard.md logs all actions; structured logging via rich |
| **Simplicity (YAGNI)** | ✅ PASS | Bronze tier is minimal: filesystem + basic skills only |

**Gate Result**: ✅ PASS - All principles satisfied. Proceed to Phase 0.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-employee-vault/
├── plan.md              # This file
├── research.md          # Phase 0 output - Technical decisions resolved
├── data-model.md        # Phase 1 output - Entity definitions
├── quickstart.md        # Phase 1 output - Setup guide
├── contracts/           # Phase 1 output - Service contracts
│   └── service-contracts.md
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
ai_employee/
├── pyproject.toml       # UV project definition
├── src/
│   └── ai_employee/
│       ├── __init__.py
│       ├── main.py          # CLI entry point (typer)
│       ├── models/
│       │   ├── __init__.py
│       │   ├── vault.py     # VaultItem, VaultState, Source
│       │   └── skill.py     # AgentSkill, SkillResult
│       ├── services/
│       │   ├── __init__.py
│       │   ├── vault.py     # VaultService (read/write/move)
│       │   ├── watcher.py   # GmailWatcher, FilesystemWatcher
│       │   ├── executor.py  # SkillExecutor
│       │   ├── logger.py    # DashboardLogger
│       │   └── registry.py  # IdempotencyRegistry
│       └── skills/
│           ├── __init__.py
│           ├── process_email.py
│           └── process_file.py
└── tests/
    ├── __init__.py
    ├── contract/
    │   ├── __init__.py
    │   └── test_skill_contracts.py
    ├── integration/
    │   ├── __init__.py
    │   ├── test_vault_operations.py
    │   └── test_watcher_integration.py
    └── unit/
        ├── __init__.py
        ├── test_models.py
        ├── test_vault_service.py
        └── test_executor.py
```

**Structure Decision**: Single Python project with clear separation:
- `models/` - Pydantic data models
- `services/` - Business logic (vault, watcher, executor, logger, registry)
- `skills/` - Agent skill implementations
- `tests/` - Three-tier testing (contract, integration, unit)

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles satisfied with minimal complexity.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Phase 2 Planning Stop Point

**Command ends after Phase 2 planning.** The following artifacts have been generated:

### Generated Artifacts

| File | Purpose | Status |
|------|---------|--------|
| `research.md` | Technical decisions and clarifications | ✅ Complete |
| `data-model.md` | Entity definitions and validation rules | ✅ Complete |
| `contracts/service-contracts.md` | Internal service API contracts | ✅ Complete |
| `quickstart.md` | Setup and usage guide | ✅ Complete |
| `plan.md` | This implementation plan | ✅ Complete |

### Next Steps (Phase 2: Tasks)

To proceed with implementation, run `/sp.tasks` to generate:
- Testable implementation tasks
- Acceptance criteria per task
- Test cases for each requirement

### Success Criteria Mapping

| Success Criteria | Implementation Path |
|-----------------|---------------------|
| SC-001: Vault structure exists | `VaultService.create_vault_structure()` |
| SC-002: Qwen CLI reads/writes markdown | `VaultService.read_item()`, `write_item()` |
| SC-003: Watcher triggers within 30s | `FilesystemWatcher` with 30s poll interval |
| SC-004: Working Agent Skill | `ProcessFile` skill implementation |
| SC-005: File transitions correct | `VaultService.move_item()` with state machine |
| SC-006: Dashboard logs all actions | `DashboardLogger.log_entry()` |
| SC-007: No manual intervention | Automated watcher + executor loop |
| SC-008: Runs entirely locally | Filesystem + local Python, no cloud deps |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gmail API changes | Medium | Use IMAP (stable protocol); app password authentication |
| File locking conflicts | Low | Advisory locking with timeout + retry |
| Vault corruption | High | Atomic file operations; transaction log |
| Duplicate processing | Medium | Idempotency registry with content hashing |

---

## References

- **Spec**: `/specs/001-ai-employee-vault/spec.md`
- **Research**: `/specs/001-ai-employee-vault/research.md`
- **Data Model**: `/specs/001-ai-employee-vault/data-model.md`
- **Contracts**: `/specs/001-ai-employee-vault/contracts/service-contracts.md`
- **Quickstart**: `/specs/001-ai-employee-vault/quickstart.md`
- **Constitution**: `/.specify/memory/constitution.md`
