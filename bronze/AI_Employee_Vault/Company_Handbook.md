# Company Handbook

## Mission

The AI Employee Vault is an autonomous AI system that automates routine information processing tasks within an Obsidian vault. It monitors input sources, organizes information into structured task states, and executes predefined agent skills.

## Business Rules

1. **Local Processing**: All processing occurs locally (no cloud transmission)
2. **Privacy**: Privacy is paramount - encrypt sensitive data at rest
3. **Idempotency**: Idempotency is required - no duplicate processing
4. **Logging**: All actions must be logged to Dashboard.md
5. **State Management**: All items follow the state workflow: Inbox → Needs_Action → Done
6. **Error Handling**: Errors are logged and items are moved to Needs_Action for manual review

## Operating Hours

- **Uptime Target**: 99% during business hours (Monday-Friday, 9AM-6PM)
- **Recovery Time**: Maximum 4-hour recovery time after system failure
- **Backup**: Automatic daily backups of vault data recommended

## Scale Constraints

- **Max Vault Size**: 1GB total
- **Daily Input Volume**: Up to 50 new inputs per day
- **Concurrent Operations**: Support for up to 5 concurrent operations
- **Max File Size**: 10MB per file

## Contact

For issues or questions, refer to Dashboard.md for operational logs.
