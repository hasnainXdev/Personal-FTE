# 1. SKILL: Inbox Intake Processor

## Purpose
Convert raw input (email or file) into a structured markdown task file.

## Trigger
Watcher detects new item in /Inbox OR Gmail.

## Input
Raw text content from:
- Email body
- Uploaded markdown
- Plain text file

## Process
- Extract title
- Identify main intent
- Generate structured task file
- Add metadata header

## Output Format

---
Title: [Generated Title]
Status: Inbox
Created: [Timestamp]
Source: [Email/File]
---

## Description
[Structured clean version of input]

## Next Step
To be determined

## Behavior Rules
- Must not overwrite existing files.
- Must generate a unique filename.
- Must place file in /Inbox folder.

---