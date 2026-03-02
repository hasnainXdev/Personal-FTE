# Feature Specification: Silver Tier Orchestration

**Feature Branch**: `002-silver-tier-orchestration`
**Created**: 2026-02-20
**Status**: Draft
**Input**: Upgrade AI Employee from reactive task processor (Bronze) to Functional Assistant with orchestration, external actions, and controlled autonomy

## Clarifications

### Session 2026-02-21

- Q: How do agent skills authenticate to MCP server? What prevents unauthorized MCP calls? → A: Token-based auth with shared secret in .env file (HMAC header on each request)
- Q: Where exactly are OAuth tokens, SMTP passwords stored? Environment variables only? → A: Environment variables with .env file (gitignored)
- Q: What constitutes unique ID for Watcher items across different sources? → A: Source-prefixed composite ID (e.g., gmail_MSG_123, file_SHA256_abc)
- Q: What happens when human approval is never provided? Should there be escalation/reminder? → A: Optional reminder notification after configurable timeout (default 24h)
- Q: What are the specific performance budgets for watcher response, MCP calls, plan generation? → A: Specific budgets: watcher <1s, MCP <5s, plan <3s; graceful degradation on timeout

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Multi-Channel Input Processing (Priority: P1)

As a business professional, I want the AI to monitor multiple input channels (email, messaging, files) simultaneously so that I don't miss important tasks from any source.

**Why this priority**: Foundation capability that enables all other Silver Tier features. Without multi-channel intake, orchestration cannot occur.

**Independent Test**: Configure two watchers (e.g., Gmail and Filesystem), trigger inputs on both channels, verify both are logged in Dashboard.md and processed through Bronze intake without interference.

**Acceptance Scenarios**:

1. **Given** Gmail watcher is configured, **When** a new email arrives, **Then** the email is logged in Dashboard.md and routed to Bronze Inbox processing
2. **Given** two watchers are running simultaneously, **When** both receive inputs within the same minute, **Then** both inputs are logged and processed without data loss or duplication
3. **Given** a watcher is restarted, **When** it resumes, **Then** it does not reprocess already-handled inputs (duplicate detection works)

---

### User Story 2 - Structured Plan Generation (Priority: P1)

As a user, I want the AI to generate a structured execution plan before performing complex multi-step tasks so that I can review and understand what actions will be taken.

**Why this priority**: Core safety mechanism that enables human oversight and prevents uncontrolled autonomous behavior. Required before any external action.

**Independent Test**: Trigger a task requiring multiple steps, verify Plan.md is created with objective, steps, expected outcome, and risk level before any execution begins.

**Acceptance Scenarios**:

1. **Given** a multi-step task is identified, **When** the AI begins processing, **Then** a Plan.md file is created in the vault before any action is taken
2. **Given** a Plan.md is created, **When** I review it, **Then** it contains objective, numbered steps, expected outcome, and risk level (Low/Medium/High)
3. **Given** a plan requires external action, **When** the plan is generated, **Then** Approval_Required is marked as "Yes"

---

### User Story 3 - Human Approval Workflow (Priority: P1)

As a user, I want to review and approve sensitive actions (emails, posts, document edits) before they execute so that I maintain control over external communications and business-critical operations.

**Why this priority**: Primary governance mechanism that prevents irreversible autonomous errors. Required for all external actions.

**Independent Test**: Trigger an action requiring approval (e.g., LinkedIn post), verify Proposed_Action.md is created, wait for manual approval marking, then verify execution only proceeds after "Approved: Yes" is set.

**Acceptance Scenarios**:

1. **Given** an external action is planned (e.g., LinkedIn post), **When** the AI prepares execution, **Then** a Proposed_Action.md file is created with summary, plan reference, and risk level
2. **Given** a Proposed_Action.md exists, **When** I set "Approved: No", **Then** the action is not executed and the rejection is logged
3. **Given** a Proposed_Action.md exists, **When** I set "Approved: Yes", **Then** the action executes and the approval decision is logged in Dashboard.md

---

### User Story 4 - LinkedIn Content Automation (Priority: P2)

As a business professional, I want the AI to generate LinkedIn post drafts and publish them after my approval so that I can maintain consistent business presence without manual content creation.

**Why this priority**: First external action capability demonstrating full orchestration chain (planning → approval → MCP execution → logging).

**Independent Test**: Request LinkedIn post generation, verify draft is saved, approve it, verify post is published via MCP, verify LinkedIn URL is stored in vault.

**Acceptance Scenarios**:

1. **Given** a LinkedIn post is requested, **When** content is generated, **Then** a Draft_LinkedIn_Post.md is saved in the vault
2. **Given** a draft is approved, **When** the post is executed, **Then** it goes through MCP server (not direct API call)
3. **Given** a post is published, **When** execution completes, **Then** the LinkedIn post URL is stored in the vault and logged

---

### User Story 5 - Scheduled Autonomous Workflows (Priority: P2)

As a user, I want the AI to execute routine tasks on a schedule (daily summaries, periodic scanning) so that I don't have to manually trigger repetitive operations.

**Why this priority**: Enables proactive assistance without constant user initiation. Demonstrates controlled autonomy within safe boundaries.

**Independent Test**: Configure a scheduled task (e.g., daily inbox scan at 9 AM), verify it triggers automatically at the scheduled time and logs execution in Dashboard.md.

**Acceptance Scenarios**:

1. **Given** a scheduled task is configured, **When** the scheduled time arrives, **Then** the task triggers automatically without user intervention
2. **Given** a scheduled task completes, **When** execution finishes, **Then** the trigger and result are logged in Dashboard.md
3. **Given** the system is restarted, **When** it resumes, **Then** scheduled tasks continue to operate (restart-safe)

---

### User Story 6 - External Action Execution via MCP (Priority: P2)

As a user, I want all external actions (emails, webhooks, API calls) to be routed through a centralized MCP server so that actions are logged, safe, and auditable.

**Why this priority**: Security and audit boundary that prevents uncontrolled external access and enables testing/mock capabilities.

**Independent Test**: Trigger an external action (e.g., send email), verify it routes through MCP server, verify action is logged with full context, verify no direct API calls bypass MCP.

**Acceptance Scenarios**:

1. **Given** an external action is requested, **When** execution occurs, **Then** it routes through MCP server (no direct API calls from agent skills)
2. **Given** an MCP call is made, **When** it completes, **Then** the call and response are logged with full context
3. **Given** an MCP call fails, **When** the failure occurs, **Then** the state is not corrupted and the error is logged

---

### User Story 7 - Skill Chaining and Orchestration (Priority: P3)

As a power user, I want the AI to chain multiple skills together in a defined sequence (watcher → classifier → planner → executor → logger) so that complex workflows execute automatically.

**Why this priority**: Demonstrates full orchestration capability. Lower priority because it depends on all other capabilities being functional first.

**Independent Test**: Trigger a workflow requiring skill chaining, verify each skill executes in declared order, verify dependencies are respected, verify no implicit chaining occurs.

**Acceptance Scenarios**:

1. **Given** a watcher triggers, **When** the workflow executes, **Then** skills chain in order: Inbox Intake → Classifier → Plan Generator → Approval Request → MCP Execution → State Transition → Log Entry
2. **Given** a skill declares a dependency, **When** the chain executes, **Then** the dependency is satisfied before the skill runs
3. **Given** a skill declares side effects, **When** it executes, **Then** side effects are logged and match the declaration

---

### Edge Cases

- What happens when two watchers trigger simultaneously with conflicting actions? System processes both independently through Bronze intake; conflicts resolved at classification stage with logging.
- How does system handle MCP server being unavailable? External actions queue with timeout; user notified; state not corrupted; retry logic with backoff.
- What happens when human approval is never provided? Action remains pending indefinitely; optional reminder notification sent after configurable timeout (default 24h).
- How does system handle duplicate inputs across watchers? Duplicate detection persists across restarts; duplicates logged but not reprocessed.
- What happens when a scheduled task's execution window is missed (system was off)? Task executes on next system start with "missed schedule" logged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support two or more independent watcher scripts monitoring different input channels
- **FR-002**: Each watcher MUST log all trigger events in Dashboard.md with timestamp and source
- **FR-003**: All watcher inputs MUST route through Bronze skill pipeline before Silver processing
- **FR-004**: Watchers MUST be restart-safe (no duplicate processing after restart)
- **FR-005**: System MUST generate Plan.md for multi-step tasks, external actions, and non-trivial risk workflows
- **FR-006**: Plan.md MUST include Title, Objective, Risk_Level (Low/Medium/High), Approval_Required (Yes/No), Created timestamp, numbered Steps, Expected Outcome, and Rollback Strategy
- **FR-007**: Plans MUST be saved in vault before execution begins
- **FR-008**: System MUST operate at least one MCP server for all external actions
- **FR-009**: No agent skill MAY directly call external APIs (all external calls route through MCP)
- **FR-009a**: MCP server MUST validate all requests using token-based authentication with shared secret (HMAC header); requests without valid auth header MUST be rejected with 401 Unauthorized
- **FR-010**: All MCP calls and responses MUST be logged with structured format
- **FR-011**: System MUST require human approval for outbound emails, LinkedIn posts, high-risk plans, and multi-step irreversible actions
- **FR-012**: Approval workflow MUST use Proposed_Action.md with Summary, Plan reference, Risk level, and Approved (Yes/No) field
- **FR-013**: Execution MUST NOT proceed without "Approved: Yes" marking
- **FR-014**: All approval decisions MUST be logged in Dashboard.md
- **FR-015**: System MUST generate LinkedIn content drafts and save as Draft_LinkedIn_Post.md
- **FR-016**: LinkedIn posts MUST NOT auto-publish without human approval
- **FR-017**: Published LinkedIn post URLs MUST be stored in vault
- **FR-018**: System MUST support scheduled task execution via cron (Linux/WSL) or Task Scheduler (Windows)
- **FR-019**: Scheduling configuration MUST be documented
- **FR-020**: No cloud scheduler dependencies allowed (local execution only)
- **FR-021**: All agent skills MUST declare Skill_Type (Internal/External), Requires_Plan (Yes/No), Requires_Approval (Yes/No), and Side_Effects (description)
- **FR-022**: Skill chains MUST follow declared skill order with no implicit chaining
- **FR-023**: Dashboard.md MUST log plan creation events, approval status updates, MCP server calls, scheduled task triggers, success/failure states, and rollback actions
- **FR-024**: All logs MUST be append-only
- **FR-024a**: All credentials (OAuth tokens, SMTP passwords, MCP shared secret) MUST be stored in environment variables loaded from .env file (gitignored); no credentials in vault files
- **FR-025**: Silver MAY add vault directories (/Plans, /Proposed_Actions, /Scheduled_Tasks, /Logs_Extended) but MUST NOT modify core Bronze directories
- **FR-026**: Bronze capabilities (Inbox intake, Task classification, State movement, Basic logging) MUST remain fully functional and unmodified

### Key Entities

- **Watcher**: Independent input channel monitor that detects and logs triggers from external sources (email, messaging, files)
- **Watcher Input Item**: Unique ID format MUST be source-prefixed composite (e.g., `gmail_MSG_123`, `file_SHA256_abc`) to guarantee global uniqueness across watchers
- **Plan.md**: Structured execution document containing objective, steps, risk assessment, and approval requirements
- **Proposed_Action.md**: Approval request document containing action summary, plan reference, risk level, and approval status
- **MCP Server**: Centralized external action handler that abstracts APIs, enforces safety boundaries, and provides structured responses
- **Skill Chain**: Ordered sequence of agent skills executed in declared dependency order for complex workflows
- **Scheduled Task**: Time-based trigger that executes predefined workflows without user initiation

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Two or more watchers operate simultaneously without interference or data loss
- **SC-002**: 100% of multi-step and external action workflows have Plan.md generated before execution
- **SC-003**: 100% of approval-required actions wait for explicit "Approved: Yes" before execution
- **SC-004**: At least one MCP server successfully executes external actions (email, LinkedIn, webhook)
- **SC-005**: LinkedIn automation workflow completes end-to-end: draft generation → approval → post → URL storage
- **SC-006**: Scheduled tasks execute automatically at configured times and log triggers
- **SC-007**: Dashboard.md logs include all planning events, approval decisions, MCP calls, and scheduled task executions
- **SC-008**: Bronze Tier capabilities (Inbox processing, classification, state movement, logging) remain fully functional with zero regressions
- **SC-009**: System operates entirely locally (WSL Ubuntu, UV Python environment) with no cloud dependencies
- **SC-010**: System is restart-safe (watchers, schedulers, and duplicate detection resume correctly after restart)
- **SC-011**: Performance budgets met: watcher polling response <1s, MCP action execution <5s, Plan.md generation <3s; graceful degradation on timeout
