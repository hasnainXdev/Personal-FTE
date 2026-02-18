# Data Model: AI Employee Vault

**Branch**: `001-ai-employee-vault` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)

## Core Entities

### 1. VaultItem

**Purpose**: Represents a single piece of information tracked in the vault

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (SHA256 hash of content) |
| `title` | string | Yes | Human-readable title extracted from content |
| `source` | enum | Yes | `gmail` \| `filesystem` |
| `source_path` | string | Yes | Original file path or email message-id |
| `current_state` | enum | Yes | `inbox` \| `needs_action` \| `done` |
| `content` | markdown | Yes | Full markdown content |
| `created_at` | datetime | Yes | ISO8601 timestamp |
| `updated_at` | datetime | Yes | ISO8601 timestamp |
| `processed_at` | datetime | No | When item was last processed |
| `assigned_skill` | string | No | Name of agent skill to apply |
| `metadata` | JSON | No | Additional structured data |

**Validation Rules**:
- `id` MUST be unique across all vault items
- `source_path` MUST be absolute path or valid email message-id
- `current_state` MUST be one of: `inbox`, `needs_action`, `done`
- `content` MUST be valid markdown
- `created_at` <= `updated_at` <= `processed_at` (if present)

**State Transitions**:
```
┌─────────┐    requires_action    ┌──────────────┐    processing_complete    ┌──────┐
│  Inbox  │ ────────────────────> │ Needs_Action │ ────────────────────────> │ Done │
└─────────┘                       └──────────────┘                           └──────┘
    │                                                                        ^
    │ no_action_needed                                                       │
    └────────────────────────────────────────────────────────────────────────┘
```

**Transition Rules**:
- `inbox` → `needs_action`: When AI determines action is required
- `inbox` → `done`: When no action needed (informational only)
- `needs_action` → `done`: When skill execution completes successfully
- `done` → (no outgoing transitions; terminal state)

---

### 2. AgentSkill

**Purpose**: Defines a capability that the AI employee can execute

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique skill identifier |
| `purpose` | string | Yes | What this skill does |
| `input_format` | schema | Yes | Expected input structure (JSON Schema or markdown template) |
| `output_format` | schema | Yes | Produced output structure |
| `invocation_method` | string | Yes | How to call this skill (CLI command, function name) |
| `expected_behavior` | string | Yes | Normal operation description |
| `failure_handling` | string | Yes | Error recovery steps |
| `enabled` | boolean | Yes | Whether skill is active |
| `execution_count` | integer | No | Number of times skill has been executed |
| `last_executed` | datetime | No | Last execution timestamp |

**Validation Rules**:
- `name` MUST be unique across all skills
- `input_format` and `output_format` MUST be valid JSON Schema or markdown template
- `invocation_method` MUST reference an existing function or CLI command
- At least one skill MUST be enabled

**Example** (from spec requirements):
```markdown
## Skill: ProcessEmail
- **Purpose**: Extract actionable items from Gmail messages
- **Input Format**: 
  ```json
  {
    "from": "sender @example.com",
    "subject": "Email subject",
    "body": "Email body content",
    "received_at": "2026-02-16T10:30:00Z"
  }
  ```
- **Output Format**: Markdown file in Inbox/
- **Invocation Method**: `python -m ai_employee.skills.process_email`
- **Expected Behavior**: Creates vault item with extracted content
- **Failure Handling Notes**: Log error to Dashboard.md, move to Needs_Action for manual review
```

---

### 3. WatcherConfig

**Purpose**: Configuration for input source monitoring

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `watcher_type` | enum | Yes | `gmail` \| `filesystem` |
| `enabled` | boolean | Yes | Whether watcher is active |
| `poll_interval_seconds` | integer | No | Default: 30 (max 30 per SC-003) |
| `source_config` | JSON | Yes | Type-specific configuration |

**Gmail Config Schema**:
```json
{
  "imap_server": "imap.gmail.com",
  "imap_port": 993,
  "email_address": "user @gmail.com",
  "app_password_env": "GMAIL_APP_PASSWORD",
  "folder": "INBOX",
  "mark_as_read": true
}
```

**Filesystem Config Schema**:
```json
{
  "watch_path": "/path/to/input/directory",
  "file_pattern": "*.md",
  "recursive": false,
  "ignore_patterns": [".*", "*.tmp", "*.swp"]
}
```

---

### 4. DashboardLog

**Purpose**: Operational log entry for Dashboard.md

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | datetime | Yes | ISO8601 timestamp |
| `trigger_event` | string | Yes | What initiated the action |
| `skill_executed` | string | No | Name of skill (if applicable) |
| `file_moved` | string | No | Transition (e.g., "Inbox→Needs_Action") |
| `outcome` | enum | Yes | `success` \| `failure` \| `skipped` |
| `error_message` | string | No | Error details (if failed) |
| `duration_ms` | integer | No | Execution time in milliseconds |

**Log Entry Format** (markdown table):
```markdown
| Timestamp | Trigger Event | Skill Executed | File Moved | Outcome |
|-----------|---------------|----------------|------------|---------|
| 2026-02-16 10:30:00 | Gmail: "Meeting Notes" | ProcessEmail | Inbox→Needs_Action | Success |
```

---

### 5. ProcessedItemRegistry

**Purpose**: Track processed items for idempotency (prevents duplicates)

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content_hash` | string | Yes | SHA256 hash of content |
| `vault_item_id` | string | Yes | Reference to VaultItem.id |
| `processed_at` | datetime | Yes | When item was processed |
| `source` | enum | Yes | `gmail` \| `filesystem` |

**Validation Rules**:
- `content_hash` MUST be unique (enforces idempotency per FR-009)
- Entries retained indefinitely for duplicate detection

---

## Relationships

```
┌──────────────┐       ┌──────────────┐
│ WatcherConfig│──────▶│  VaultItem   │
└──────────────┘  1:N  └──────────────┘
                            │
                            │ assigned_skill
                            ▼
                       ┌──────────────┐
                       │  AgentSkill  │
                       └──────────────┘
                            │
                            │ execution logs
                            ▼
                       ┌──────────────┐
                       │ DashboardLog │
                       └──────────────┘

┌──────────────┐       ┌──────────────┐
│  VaultItem   │──────▶│ProcessedItem │
│ (content)    │ hash  │   Registry   │
└──────────────┘  1:1  └──────────────┘
```

---

## File Structure Mapping

| Entity | Storage Location | Format |
|--------|-----------------|--------|
| VaultItem | `Inbox/`, `Needs_Action/`, `Done/` | Markdown file |
| AgentSkill | `Agent_Skills.md` | Markdown with frontmatter |
| WatcherConfig | `.ai_employee/config.json` | JSON |
| DashboardLog | `Dashboard.md` | Markdown table |
| ProcessedItemRegistry | `.ai_employee/processed.json` | JSON |

---

## Validation Rules Summary

### VaultItem Validation
- FR-001: Vault structure MUST exist before operations
- FR-002: Markdown files MUST be valid (parseable)
- FR-006: File transitions MUST be atomic (no intermediate state)

### AgentSkill Validation
- FR-013: All fields MUST be present in skill definition
- FR-007: Skills MUST execute with proper input/output handling

### Idempotency Validation
- FR-009: Content hash MUST be checked before processing
- Duplicate items MUST be skipped and logged

---

## Data Scale Constraints

| Constraint | Limit | Enforcement |
|------------|-------|-------------|
| Max vault size | 1GB | Warning at 800MB, error at 1GB |
| Daily inputs | 50 | Rate limiting, queue overflow handling |
| Concurrent operations | 5 | Semaphore-based concurrency control |
| Max file size | 10MB | Reject files exceeding limit |
| Log entries (Dashboard) | 1000 | Archive to monthly files |

---

## Error Taxonomy

| Error Code | Category | Recovery |
|------------|----------|----------|
| `VAULT_NOT_FOUND` | Configuration | Create vault structure |
| `FILE_LOCK_TIMEOUT` | Transient | Retry with backoff |
| `INVALID_MARKDOWN` | Validation | Move to Needs_Action for manual review |
| `SKILL_NOT_FOUND` | Configuration | Log error, skip processing |
| `DUPLICATE_INPUT` | Idempotency | Skip and log |
| `WATCHER_CONNECTION_LOST` | Transient | Reconnect with exponential backoff |
| `STORAGE_CAPACITY_EXCEEDED` | Resource | Alert user, pause processing |
