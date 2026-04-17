---
name: dream
description: Consolidate, prune, and optimize the persistent memory bank. Use this skill whenever the user says "dream", "/dream", "consolidate memory", "clean up memory", or "prune memory". Triggers the memory maintenance cycle that archives completed tasks, merges redundant decisions, extracts new workflows, and updates project context.
---

# Dream — Memory Consolidation

Consolidate, prune, and optimize the `.github/memory/` directory so the context window stays efficient across sessions.

## When to use

Use this skill when the user triggers a memory maintenance cycle — typically by saying `/dream`, "dream", "consolidate memory", or "clean up memory".

## Process

### 1. Read all memory files

Read every file in `.github/memory/`:
- `project-context.md`
- `active-task.md`
- `workflows.md`
- `decision-log.md`
- `archive.md`

Also read `dream-protocol.md` for the authoritative consolidation rules.

### 2. Prune active tasks

Review `active-task.md`. Identify any tasks marked as complete. Move the essence of each completed task to `archive.md` as a brief 1–2 sentence summary, then remove it from `active-task.md`.

### 3. Consolidate decisions

Review `decision-log.md`. If multiple entries relate to the same component, merge them into a single, cohesive rule or principle. Remove redundant or obsolete decisions.

### 4. Extract workflows

Scan recent work across the memory files. If a new repetitive pattern has emerged, document it as a standard operating procedure in `workflows.md`.

### 5. Update project context

If recent decisions fundamentally change the project architecture, update `project-context.md` to reflect this.

### 6. Present changes

Generate the updated file contents and present them to the user for review before applying.

## Guidelines

- Keep archive entries concise — 1–2 sentences per completed task.
- Never delete information without moving its essence to the archive first.
- Preserve the chronological order in the decision log after merging.
- Do not alter `dream-protocol.md` itself during a dream cycle.
