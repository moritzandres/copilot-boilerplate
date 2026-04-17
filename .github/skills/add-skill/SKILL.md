---
name: add-skill
description: Scaffold a new Copilot skill for this repository. Use this skill whenever the user wants to create, add, or scaffold a new skill, capability, or custom instruction set for the project. Trigger on phrases like "add a skill", "create a skill", "new skill", "scaffold skill", or "add a capability".
---

# Add Skill

Scaffold a new Copilot CLI skill inside this repository's local plugin at `.github/`.

## When to use

Use this skill when the user wants to add a new skill to this project. A skill is a reusable instruction bundle that teaches Copilot how to perform a specific task for this repository.

## Process

### 1. Gather requirements

Ask for:
1. **Skill name** — a short kebab-case identifier such as `run-experiment`
2. **Purpose** — a one-sentence summary of what the skill should do
3. **Trigger contexts** — the phrases or tasks that should cause Copilot to use it

### 2. Create the skill directory and `SKILL.md`

Create:

```text
.github/skills/<skill-name>/SKILL.md
```

Use this template:

```markdown
---
name: <skill-name>
description: <Say what the skill does and when to trigger it. Include concrete phrases and contexts so it triggers reliably.>
---

# <Skill Title>

## Overview

<What the skill does and why it exists.>

## Instructions

<Step-by-step instructions in imperative form.>
```

If the skill needs bundled resources, add them next to `SKILL.md`:

```text
.github/skills/<skill-name>/
├── SKILL.md
├── reference/
├── scripts/
└── assets/
```

### 3. Register the skill in `.github/plugin.json`

Add the new path to the `skills` array:

```json
{
  "skills": [
    "skills/add-skill",
    "skills/add-mcp",
    "skills/<new-skill-name>"
  ]
}
```

### 4. Reinstall the local plugin

From the repository root, run:

```bash
copilot plugin install "$PWD/.github"
```

### 5. Verify

Tell the user to start a new Copilot session and verify the skill with `/skills list`, or by asking for the task the skill should handle and confirming the skill triggers.

## Guidelines

- Keep `SKILL.md` under 500 lines. Move large content into `reference/`.
- Make trigger descriptions slightly pushy so the skill activates reliably.
- Use imperative instructions.
- Keep the skill specific to repository workflows and conventions.
