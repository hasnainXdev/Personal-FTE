# Watcher Interface Contract

**Version**: 1.0.0
**Created**: 2026-02-20
**Status**: Draft

---

## Overview

Watchers are independent input channel monitors that detect and log triggers from external sources. Each watcher operates in isolation with no cross-watcher interference.

**Minimum Requirement**: 2+ watchers for Silver Tier classification

---

## Watcher Interface

### Core Methods

```python
class Watcher:
    """
    Abstract base class for all watchers.
    All watchers MUST implement this interface.
    """
    
    def __init__(self, name: str, config: dict):
        """
        Initialize watcher with name and configuration.
        
        Args:
            name: Unique watcher identifier (e.g., "gmail", "filesystem")
            config: Watcher-specific configuration (credentials, paths, etc.)
        """
        pass
    
    async def poll(self) -> list[InputItem]:
        """
        Poll the input source for new items since last check.
        
        Returns:
            List of new InputItem objects (excluding already-processed)
        
        Side Effects:
            - Updates last_check_timestamp
            - Logs poll event to Dashboard.md
        """
        pass
    
    def mark_processed(self, item_id: str) -> None:
        """
        Mark an item as processed (for duplicate detection).
        
        Args:
            item_id: Unique item identifier
        
        Side Effects:
            - Persists item_id to processed_ids[]
        """
        pass
    
    def get_last_check(self) -> datetime:
        """
        Get timestamp of last successful poll.
        
        Returns:
            ISO8601 timestamp of last check
        """
        pass
    
    async def restart(self) -> None:
        """
        Restart watcher (recover from error state).
        
        Side Effects:
            - Resets error state
            - Re-establishes connections
        """
        pass
```

---

## InputItem Data Structure

```python
class InputItem:
    """
    Standardized input item format across all watchers.
    """
    
    id: str                    # Unique, persistent identifier
    source: str                # Watcher name (e.g., "gmail")
    timestamp: datetime        # When item was created/received
    content: dict              # Raw content (provider-specific)
    metadata: dict             # Additional context
    
    # Metadata Fields (all watchers)
    metadata: {
        "watcher_type": str,   # gmail | filesystem | whatsapp | linkedin
        "raw_timestamp": str,  # Original timestamp from source
        "priority": str,       # low | normal | high (if available)
        "tags": list[str],     # Optional categorization tags
    }
```

---

## Output Format

Watchers MUST route all outputs through Bronze Inbox Intake skill.

**Output Location**: `Inbox/{item_id}.md`

**Format**:
```markdown
---
Source: {watcher_name}
Source_ID: {item.id}
Received: {item.timestamp.isoformat()}
Processed: false
---

## Content

{item.content formatted as Markdown}

## Metadata

- Priority: {item.metadata.priority}
- Tags: {", ".join(item.metadata.tags)}
- Raw Data: {item.content JSON (optional)}
```

---

## Watcher Implementations

### Gmail Watcher

**Type**: `gmail`
**Polling**: IMAP or Gmail API
**Interval**: 60 seconds

**Configuration**:
```yaml
watcher_type: gmail
credentials:
  oauth_token: ${GMAIL_OAUTH_TOKEN}
  refresh_token: ${GMAIL_REFRESH_TOKEN}
settings:
  poll_interval: 60
  label_filter: "INBOX"
  max_results: 50
```

**Item ID Format**: `MSG_{message_id}`

**Content Extraction**:
```python
{
  "from": email.sender,
  "to": email.recipients,
  "subject": email.subject,
  "body": email.body_plain,
  "html_body": email.body_html,
  "attachments": [attachment.metadata],
  "received_at": email.date
}
```

---

### Filesystem Watcher

**Type**: `filesystem`
**Polling**: Directory scan
**Interval**: 60 seconds

**Configuration**:
```yaml
watcher_type: filesystem
settings:
  watch_directory: /path/to/inbox
  poll_interval: 60
  file_patterns: ["*.txt", "*.md", "*.json"]
  recursive: false
```

**Item ID Format**: `FILE_{sha256_hash}`

**Content Extraction**:
```python
{
  "filename": file.name,
  "path": file.absolute_path,
  "size_bytes": file.size,
  "modified_at": file.mtime,
  "content": file.read_text(),
  "extension": file.suffix
}
```

---

### LinkedIn Message Watcher

**Type**: `linkedin`
**Polling**: LinkedIn API
**Interval**: 300 seconds (5 min - rate limit friendly)

**Configuration**:
```yaml
watcher_type: linkedin
credentials:
  access_token: ${LINKEDIN_ACCESS_TOKEN}
settings:
  poll_interval: 300
  message_type: "received"  # received | sent | all
```

**Item ID Format**: `LI_MSG_{message_urn}`

**Content Extraction**:
```python
{
  "from": message.sender_name,
  "from_urn": message.sender_urn,
  "body": message.text,
  "conversation_id": message.conversation_id,
  "created_at": message.created_timestamp
}
```

---

### WhatsApp Watcher

**Type**: `whatsapp`
**Polling**: WhatsApp Business API / Twilio webhook
**Interval**: 60 seconds

**Configuration**:
```yaml
watcher_type: whatsapp
credentials:
  api_key: ${WHATSAPP_API_KEY}
  phone_number: ${WHATSAPP_PHONE}
settings:
  poll_interval: 60
```

**Item ID Format**: `WA_MSG_{message_sid}`

**Content Extraction**:
```python
{
  "from": message.from_number,
  "body": message.body,
  "media_url": message.media_url,
  "media_type": message.content_type,
  "received_at": message.date_created
}
```

---

## Duplicate Detection

### Algorithm

```python
def is_duplicate(self, item_id: str) -> bool:
    """Check if item was already processed."""
    processed = load_processed_ids()
    return item_id in processed

def mark_processed(self, item_id: str) -> None:
    """Mark item as processed, persist to storage."""
    processed = load_processed_ids()
    processed.append(item_id)
    
    # Prune old IDs (keep last 1000)
    if len(processed) > 1000:
        processed = processed[-1000:]
    
    save_processed_ids(processed)
```

### Storage Format

**File**: `Logs_Extended/watcher-{name}_processed.md`

```markdown
# Processed IDs: Gmail Watcher

Last Pruned: 2026-02-20T00:00:00Z
Count: 247

- MSG_1708412345_abc123
- MSG_1708412346_def456
- MSG_1708412347_ghi789
```

---

## Logging Requirements

### Dashboard.md Entry

Each poll event MUST log to Dashboard.md:

```markdown
### Watcher Triggers

| Timestamp | Watcher | Items Found | Status | Duration |
|-----------|---------|-------------|--------|----------|
| 2026-02-20T10:00:00Z | Gmail | 3 | Processed | 1.2s |
| 2026-02-20T10:00:00Z | Filesystem | 0 | Processed | 0.3s |
| 2026-02-20T10:01:00Z | LinkedIn | 1 | Processed | 2.1s |
```

### Error Logging

Errors MUST log with context:

```markdown
### Watcher Errors

| Timestamp | Watcher | Error | Recovery Action |
|-----------|---------|-------|-----------------|
| 2026-02-20T10:05:00Z | Gmail | OAuth token expired | Refreshed token, retry succeeded |
```

---

## Restart Safety

### State Persistence

Watchers MUST persist state to survive restarts:

1. **last_check_timestamp**: Stored in `Logs_Extended/watcher-{name}_state.md`
2. **processed_ids**: Stored in `Logs_Extended/watcher-{name}_processed.md`
3. **error_state**: Stored in same state file

### Recovery Flow

```python
async def start(self):
    """Initialize watcher with restart safety."""
    state = load_state()
    
    if state.status == "error":
        logger.warning(f"Watcher {self.name} in error state, attempting recovery")
        await self.restart()
    
    # Check for missed executions
    missed = datetime.now() - state.last_check
    if missed > timedelta(minutes=5):
        logger.info(f"Watcher {self.name} missed {missed}, executing catch-up poll")
        await self.poll(missed_schedule=True)
```

---

## Testing

### Unit Tests

```python
async def test_gmail_watcher_poll():
    watcher = GmailWatcher("gmail", test_config)
    items = await watcher.poll()
    
    assert len(items) >= 0
    assert all(isinstance(item, InputItem) for item in items)
    assert all(item.source == "gmail" for item in items)

async def test_duplicate_detection():
    watcher = GmailWatcher("gmail", test_config)
    
    # First poll - should find items
    items1 = await watcher.poll()
    for item in items1:
        watcher.mark_processed(item.id)
    
    # Second poll - should not return same items
    items2 = await watcher.poll()
    assert not any(item.id in [i.id for i in items1] for item in items2)
```

### Integration Tests

```python
async def test_watcher_to_inbox_flow():
    """Test complete flow: watcher → Inbox file creation."""
    watcher = GmailWatcher("gmail", test_config)
    
    # Poll
    items = await watcher.poll()
    
    # Route to Inbox
    for item in items:
        output_path = f"Inbox/{item.id}.md"
        write_inbox_file(item, output_path)
        
        # Verify file created
        assert os.path.exists(output_path)
        watcher.mark_processed(item.id)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-20 | Initial contract: interface, InputItem, 4 watcher types |

---

## Next Steps

1. ✅ Watcher contract complete
2. Implement Gmail watcher (scripts/watchers/gmail_watcher.py)
3. Implement Filesystem watcher (scripts/watchers/filesystem_watcher.py)
4. Add duplicate detection persistence
5. Test restart safety
