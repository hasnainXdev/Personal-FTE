# Implementation Plan: Silver Tier Orchestration

**Branch**: `002-silver-tier-orchestration` | **Date**: 2026-02-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification for upgrading AI Employee from Bronze (reactive processor) to Silver (Functional Assistant with orchestration)

## Summary

Upgrade AI Employee to Silver Tier by adding multi-watcher orchestration, structured planning (Plan.md), human-in-the-loop approval workflow, MCP server for external actions, LinkedIn automation, scheduling layer, and skill chaining. All changes preserve Bronze Tier functionality as immutable foundation. Technical approach: 7-phase incremental rollout with validation gates between each phase.

## Technical Context

**Language/Version**: Python 3.11 (UV Python environment)
**Primary Dependencies**: Python standard library, cron (Linux/WSL) / Task Scheduler (Windows)
**Storage**: Filesystem-based vault (Markdown files in Obsidian-compatible structure)
**Testing**: Manual scenario testing, restart tests, duplicate trigger tests, failure simulation
**Target Platform**: WSL Ubuntu (Linux) with Windows interop
**Project Type**: Single project (CLI-based agent skills)
**Performance Goals**: Sub-second watcher trigger response, <5s plan generation for standard workflows
**Constraints**: Local execution only (no cloud), restart-safe, idempotent operations, <100MB memory footprint
**Scale/Scope**: Single user, 2-5 watchers, 10-50 tasks/day, 1-5 scheduled tasks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Constitution Principle | Compliance Status | Notes |
|------------------------|-------------------|-------|
| I. Bronze Tier Foundation | ✅ PASS | No Bronze modifications planned; all Silver additions are extensions |
| II. Silver Tier Purpose | ✅ PASS | Multi-channel, scheduling, external actions, planning, approval all addressed |
| III. Bronze-Silver Relationship | ✅ PASS | Uses Bronze vault structure, routes through Bronze skills, no rewrites |
| IV. Core Capabilities | ✅ PASS | 2+ watchers, Plan.md, MCP, approval, scheduling, Agent Skills all in scope |
| V. Orchestration Layer | ✅ PASS | Skill chaining with explicit dependencies, sequential execution |
| VI. External Action Governance | ✅ PASS | All external actions via MCP, logged, approval-gated |
| VII. Human-in-the-Loop | ✅ PASS | Proposed_Action.md workflow for emails, posts, high-risk plans |
| VIII. Planning Layer | ✅ PASS | Plan.md template with required fields, vault storage, deviation logging |
| IX. Scheduling Layer | ✅ PASS | Local cron/Task Scheduler, documented, restart-safe |
| X. Multi-Watcher Governance | ✅ PASS | Independent watchers, no cross-interference, logging, restart-safe |
| XI. LinkedIn Automation | ✅ PASS | Draft → approval → MCP → URL storage workflow |
| XII. MCP Server Requirements | ✅ PASS | Centralized external access, no direct API calls from skills |
| XIII. Agent Skill Expansion | ✅ PASS | Skills declare type, dependencies, side effects, approval requirements |
| XIV. Logging & Traceability | ✅ PASS | Dashboard.md extended with plan, approval, MCP, schedule logs |
| XV. Stability Guarantee | ✅ PASS | Validation gates after each phase; Bronze regression = STOP |
| XVI. Non-Scope (Gold Reserved) | ✅ PASS | No self-improvement, strategic goals, or autonomous optimization |
| XVII. Guiding Principle | ✅ PASS | Coordination with control; autonomy subordinate to approval |

**Constitution Check Result**: ✅ ALL PASS - No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/002-silver-tier-orchestration/
├── plan.md              # This file
├── research.md          # Phase 0 output (watcher patterns, MCP design, scheduling)
├── data-model.md        # Phase 1 output (entities, state transitions)
├── quickstart.md        # Phase 1 output (setup guide)
├── contracts/           # Phase 1 output (MCP interface, watcher contract)
│   ├── mcp-interface.md
│   └── watcher-contract.md
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
AI_Employee_Vault/
├── Skills/
│   ├── Bronze/                  # UNCHANGED - immutable foundation
│   │   ├── inbox-intake.md
│   │   ├── task-classifier.md
│   │   ├── task-state-mover.md
│   │   └── task-summarizer.md
│   └── Silver/                  # NEW - orchestration layer
│       ├── watcher-gmail.md
│       ├── watcher-filesystem.md
│       ├── plan-generator.md
│       ├── approval-request.md
│       ├── linkedin-generator.md
│       ├── scheduler.md
│       └── orchestrator.md
├── Dashboard.md                 # EXTENDED - new log types
├── Inbox/                       # Bronze - unchanged
├── Needs_Action/                # Bronze - unchanged
├── Done/                        # Bronze - unchanged
├── Plans/                       # NEW - Plan.md storage
├── Proposed_Actions/            # NEW - approval workflow
├── Scheduled_Tasks/             # NEW - scheduled task configs
└── Logs_Extended/               # NEW - detailed MCP/approval logs

mcp_server/                      # NEW - external action boundary
├── server.py
├── actions/
│   ├── email.py
│   ├── linkedin.py
│   └── webhook.py
└── tests/

scripts/                         # NEW - watchers, scheduler
├── watchers/
│   ├── gmail_watcher.py
│   └── filesystem_watcher.py
└── scheduler/
    └── cron_runner.py
```

**Structure Decision**: Single project with clear Bronze/Silver separation. Silver adds new directories and skills without modifying Bronze structure. MCP server isolated in separate directory for clear boundary.

## Complexity Tracking

No Constitution violations. Complexity justified by tiered rollout with validation gates.

| Complexity Item | Why Needed | Simpler Alternative Rejected Because |
|-----------------|------------|--------------------------------------|
| 7-phase rollout | Bronze stability guarantee | Big-bang deployment risks Bronze regression |
| MCP server layer | Security, audit, testing | Direct API calls would violate constitution Principle XII |
| Approval workflow | Irreversible action safety | Auto-execution would violate Principle VII |
| Skill chaining | Complex workflow automation | Manual skill invocation defeats orchestration purpose |
| Multiple watchers | Multi-channel intake | Single channel insufficient for Silver classification |

---

## Phase 0: Research & Design Decisions

### Research Tasks

1. **Watcher Interface Patterns**
   - Research: Polling vs. push-based watcher architectures
   - Research: Duplicate detection strategies across restarts
   - Research: Error handling and retry patterns for watchers

2. **MCP Server Design**
   - Research: Minimal MCP server implementation in Python
   - Research: Structured response formats (JSON schema)
   - Research: Timeout and failure handling patterns

3. **Scheduling Patterns**
   - Research: Cron syntax and scheduling libraries for Python
   - Research: Windows Task Scheduler integration from WSL
   - Research: Restart-safe scheduling (missed execution handling)

4. **Plan Generation Patterns**
   - Research: Structured plan templates for task execution
   - Research: Risk assessment heuristics for approval triggers

### Design Decisions (to be finalized in research.md)

| Decision | Options | Preliminary Choice |
|----------|---------|-------------------|
| Watcher polling interval | 30s / 60s / 5min | 60s (balance responsiveness vs. API limits) |
| MCP transport | HTTP / stdio / sockets | HTTP localhost (simplest for WSL) |
| Scheduling library | APScheduler / cron / custom | cron (native, no dependencies) |
| Plan storage format | Markdown / JSON | Markdown (vault-compatible) |
| Approval polling | File watch / manual trigger | File watch (Proposed_Action.md modification time) |

---

## Phase 1: Design Artifacts

### Data Model (data-model.md)

**Entities**:

1. **Watcher**
   - Fields: name, source_type, last_check_timestamp, processed_ids[], status
   - Relationships: logs to Dashboard.md, outputs to Inbox/
   
2. **Plan**
   - Fields: title, objective, risk_level, approval_required, steps[], expected_outcome, rollback_strategy, created_timestamp, status
   - Relationships: referenced by Proposed_Action.md, executed by Orchestrator

3. **Proposed_Action**
   - Fields: summary, plan_reference, risk_level, approved (Yes/No), created_timestamp, reviewed_timestamp
   - Relationships: references Plan.md, triggers MCP action if approved

4. **Scheduled_Task**
   - Fields: name, cron_expression, last_run, next_run, enabled, task_config
   - Relationships: logs to Dashboard.md

5. **MCP_Action_Log**
   - Fields: timestamp, action_type, request_payload, response_payload, status, error_context
   - Relationships: referenced by Dashboard.md

**State Transitions**:

```
Proposed_Action: Pending → (Approved: Yes) → Executing → Completed
                                   → (Approved: No)  → Rejected

Plan: Draft → Active → Completed
              → Rolled_Back (if rollback triggered)

Scheduled_Task: Enabled → Triggered → Executing → Completed → Enabled (cycle)
```

### API Contracts (contracts/)

**MCP Interface** (contracts/mcp-interface.md):

```yaml
POST /execute
  request:
    action: string (send_email | post_linkedin | fetch_url)
    parameters: object
    timeout_ms: number
  response:
    success: boolean
    result: object
    error: string (if !success)

GET /health
  response:
    status: "healthy" | "degraded" | "unhealthy"
    uptime_seconds: number
```

**Watcher Contract** (contracts/watcher-contract.md):

```yaml
Watcher Interface:
  - poll() → list[InputItem]
  - mark_processed(id: string)
  - get_last_check() → timestamp
  - restart() → void

InputItem:
  - id: string (unique, persistent)
  - source: string (watcher name)
  - timestamp: ISO8601
  - content: object
  - metadata: object
```

### Quickstart Guide (quickstart.md)

**Setup Steps**:

1. Clone repository, ensure UV Python environment active
2. Configure watcher credentials (Gmail OAuth, etc.)
3. Set up MCP server: `cd mcp_server && python server.py`
4. Configure cron jobs: `crontab -e` (see Scheduled_Tasks/ examples)
5. Test Phase 1: Run two watchers, verify Dashboard.md logging
6. Proceed through phases 2-7 with validation gates

**Testing Checklist**:

- [ ] Both watchers trigger and log independently
- [ ] Plan.md generated for multi-step task
- [ ] Approval workflow halts execution until approved
- [ ] MCP server executes test action successfully
- [ ] Scheduled task triggers at configured time
- [ ] Full chain executes: watcher → intake → classifier → plan → approval → MCP → state → log
- [ ] Bronze Inbox processing still functional

---

## Agent Context Update

**Action Required**: Run `.specify/scripts/bash/update-agent-context.sh qwen` to add Silver Tier technologies:

- MCP server pattern (HTTP localhost)
- APScheduler / cron scheduling
- Watcher polling architecture
- Plan.md generation pattern
- Approval workflow pattern

---

## Constitution Re-Check (Post-Design)

All principles remain satisfied after design completion:

- ✅ No Bronze modifications
- ✅ MCP server provides external action boundary
- ✅ Approval workflow prevents unsafe auto-execution
- ✅ Local scheduling only (no cloud)
- ✅ Skill contracts explicit with dependencies
- ✅ Comprehensive logging in Dashboard.md

**Ready for Phase 2**: `/sp.tasks` to break into implementation tasks.
