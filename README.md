# Agentic Boilerplate for Copilot

Boilerplate for GitHub Copilot — agents, skills, your own MCP servers, and a persistent memory system — ready to drop into any repository.

Let me know what you think about this, if this is helpful to you or how you would improved this. What default MCP, skills or agents would add?

## Quick Start

Copy the `.github/` directory into your repository and customise the files to match your project.
Then install the local plugin so Copilot picks up your agents, skills, and MCPs:

```bash
copilot plugin install "$PWD/.github"
```

Also add the anthropic document skills:

```bash
copilot plugin marketplace add anthropics/skills
copilot plugin install document-skills@anthropic-agent-skills
```

---

## Repository Layout

```text
.github/
├── .heartbeats.json                  # Declarative heartbeat schedule and prompts
├── copilot-instructions.md          # Standard global instructions loaded into every Copilot session
├── plugin.json                      # Local plugin manifest — registers agents, skills & MCPs
├── .mcp.json                        # MCP server registry (stdio servers run via `uv`)
├── hooks/                           # Copilot hook definitions (session lifecycle automation)
│   └── sync_heartbeats.json         # Session-start hook that syncs heartbeat jobs
├── scripts/                         # Helper scripts invoked by hooks
│   ├── sync_heartbeats.py           # Linux cron sync
│   ├── sync_heartbeats_mac.py       # macOS launchd sync
│   └── sync_heartbeats_win.py       # Windows Task Scheduler sync
│
├── agents/                          # Custom Copilot agent definitions
│   ├── orchestrator.agent.md        # Lead-Architect — coordinates all other agents
│   ├── researcher.agent.md          # Web & scientific literature search
│   ├── codebase.agent.md            # Read-only codebase exploration
│   ├── coder.agent.md               # Feature implementation
│   ├── refactor.agent.md            # Structural changes & migrations
│   ├── code_critic.agent.md         # Code review (read-only)
│   ├── tester.agent.md              # Test writing & QA
│   ├── test_critic.agent.md         # Test review (read-only)
│   ├── docs_writer.agent.md         # Documentation generation
│   └── experiment_manager.agent.md  # Experiment lifecycle management
│
├── mcps/                            # Model Context Protocol servers
│   └── deep_research_mcp.py         # Web + ArXiv search MCP (FastMCP / uv)
│
├── skills/                          # Reusable instruction bundles (skills)
│   ├── add-skill/                   # Skill: scaffold a new skill
│   │   └── SKILL.md
│   ├── add-mcp/                     # Skill: scaffold a new MCP server
│   │   └── SKILL.md
│   ├── dream/                       # Skill: memory consolidation (/dream)
│   │   └── SKILL.md
│   └── temp-skill-test/             # (empty, used for testing)
│
└── memory/                          # Persistent memory bank for cross-session context
    ├── project-context.md           # Project purpose, tech stack & architecture
    ├── active-task.md               # Current task and immediate next steps
    ├── workflows.md                 # Step-by-step SOPs for repetitive tasks
    ├── decision-log.md              # Chronological log of technical decisions
    ├── archive.md                   # Compressed summaries of completed work
    └── dream-protocol.md            # `/dream` consolidation & pruning rules
```

---

## Components

### 1. Copilot Instructions — `copilot-instructions.md`

The standard global instruction file loaded at the start of every Copilot session. It contains:

- **Project Overview / Commands / Key Conventions** — placeholders you fill in for your project.
- **Memory Bank Protocol** — tells Copilot how to read, use, and update the persistent memory files (see [§7 Memory](#7-memory-bank--memory)).

### 2. Plugin Manifest — `plugin.json`

| Field | Purpose |
| --- | --- |
| `agents` | Points to the `agents/` directory so all `.agent.md` files are discovered |
| `skills` | Lists registered skills by path (`skills/add-skill`, `skills/add-mcp`, `skills/dream`) |
| `mcpServers` | Points to `.mcp.json` for MCP server definitions |

### 3. Agents — `agents/`

The agents form a **multi-agent workflow** orchestrated by the Lead-Architect:

| Agent | File | Role |
| --- | --- | --- |
| **Lead-Architect** | `orchestrator.agent.md` | Coordinates all agents |
| **Researcher** | `researcher.agent.md` | Searches the web and ArXiv for scientific context |
| **Codebase Agent** | `codebase.agent.md` | Explores the local codebase for existing implementations |
| **Coder** | `coder.agent.md` | Implements new features |
| **Refactor-Specialist** | `refactor.agent.md` | Restructures code, updates imports, handles migrations |
| **Code Critic** | `code_critic.agent.md` | Reviews code for correctness, readability & security |
| **Tester** | `tester.agent.md` | Writes pytest tests targeting 100% coverage |
| **Test Critic** | `test_critic.agent.md` | Reviews test suites for gaps and robustness |
| **Docs Writer** | `docs_writer.agent.md` | Generates and updates READMEs, API docs & changelogs |

### 4. MCP Servers — `mcps/` and `.mcp.json`

MCP (Model Context Protocol) servers give Copilot access to external tools at runtime.

#### `deep_research_mcp.py`

A local stdio MCP server built with **FastMCP** and run via `uv`. It exposes two tools:

| Tool | Description |
| --- | --- |
| `search_web` | DuckDuckGo web search for documentation, articles & general info |
| `search_scientific_papers` | ArXiv search for academic papers and preprints |

Dependencies are declared inline (PEP 723) so they stay isolated from the main project:

```bash
arxiv>=3.0.0, duckduckgo-search>=8.0.0, mcp[cli]>=1.0.0
```

#### `.mcp.json`

Registers servers so Copilot can discover them:

```json
{
  "mcpServers": {
    "deep-research": {
      "command": "uv",
      "args": ["run", "mcps/deep_research_mcp.py"]
    }
  }
}
```

### 5. Skills — `skills/`

Skills are reusable instruction bundles that teach Copilot how to perform specific tasks. Each skill lives in its own directory with a `SKILL.md` file.

| Skill | Directory | Trigger phrases |
| --- | --- | --- |
| **add-skill** | `skills/add-skill/` | _"add a skill"_, _"create a skill"_, _"scaffold skill"_ |
| **add-mcp** | `skills/add-mcp/` | _"add an MCP"_, _"create an MCP"_, _"new MCP server"_ |
| **dream** | `skills/dream/` | _"dream"_, _"/dream"_, _"consolidate memory"_, _"prune memory"_ |

#### `add-skill`

Walks through scaffolding a new skill: gathering requirements, creating `skills/<name>/SKILL.md`, registering it in `plugin.json`, and reinstalling the plugin.

#### `add-mcp`

Walks through scaffolding a new MCP server: gathering requirements, creating a FastMCP Python script in `mcps/`, registering it in `.mcp.json`, and verifying the server responds.

#### `dream`

Triggers the memory maintenance cycle: reads all memory files, archives completed tasks, merges redundant decisions, extracts new workflows, updates project context, and presents the changes for review.

### 6. Hooks and Heartbeats — `hooks/`, `scripts/`, and `.heartbeats.json`

Hooks let Copilot run automation at session lifecycle boundaries. In this boilerplate, the currently implemented hook runs at **session start** and ensures the configured heartbeat jobs are synchronized with the local operating system scheduler.

#### `hooks/sync_heartbeats.json`

This file registers a `sessionStart` hook with platform-specific commands:

- `bash` runs `python .github/scripts/sync_heartbeats.py`
- `powershell` runs `python .github/scripts/sync_heartbeats_win.py`

The effect is that whenever a real Copilot chat session starts in the repository, Copilot re-reads the heartbeat configuration and reapplies it to the local scheduler. That keeps the scheduled automation aligned with the checked-in config instead of relying on a one-time manual setup.

#### `.heartbeats.json`

This file is the declarative source of truth for heartbeat jobs:

| Field | Purpose |
| --- | --- |
| `name` | Stable identifier used for the scheduled job name and log file name |
| `schedule` | Five-field cron-style schedule string |
| `prompt` | Copilot prompt to execute when the heartbeat fires |

Current example:

- `weekly-sleep` runs every Sunday at `03:00`
- It executes the `dream` skill prompt to consolidate memory automatically

#### Platform-specific scheduler sync

The hook does not execute the heartbeat immediately. Instead, it translates `.heartbeats.json` into native scheduled jobs:

| Platform | Script | Scheduler |
| --- | --- | --- |
| Linux | `scripts/sync_heartbeats.py` | `cron` |
| macOS | `scripts/sync_heartbeats_mac.py` | `launchd` |
| Windows | `scripts/sync_heartbeats_win.py` | Task Scheduler |

On Windows, the sync script validates each heartbeat, creates a per-workspace task prefix, writes a short PowerShell wrapper script, and registers a Task Scheduler entry that launches Copilot in autopilot mode from the repository root. The task name format is `CopilotHB_<workspace-hash>_<heartbeat-name>`, which avoids collisions across repositories.

This design gives you two important properties:

1. Heartbeat definitions stay version-controlled in the repository.
2. Session start acts as a repair point, re-registering jobs if they were deleted or changed locally.

### 7. Memory Bank — `memory/`

A persistent, file-based memory system that gives Copilot cross-session context. Governed by the **Memory Bank Protocol** defined in `copilot-instructions.md`.

| File | Purpose | Volatility |
| --- | --- | --- |
| `project-context.md` | Project description, tech stack, architecture | Static — rarely changes |
| `active-task.md` | Current task and immediate next steps | Highly dynamic |
| `workflows.md` | Step-by-step SOPs for repetitive tasks | Grows over time |
| `decision-log.md` | Why specific technical decisions were made | Append-only |
| `archive.md` | Compressed summaries of completed tasks | Append-only |
| `dream-protocol.md` | Rules for the `/dream` consolidation command | Static |

**Protocol phases:**

1. **Read** — Copilot reads `project-context.md` and `active-task.md` at session start.
2. **Execute** — Copilot consults `workflows.md` and `decision-log.md` during work.
3. **Write** — On request (_"update the memory"_), Copilot proposes edits to the relevant memory files.
4. **Dream** — The **dream** skill triggers consolidation: completed tasks move to the archive, redundant decisions are merged, and new workflows are extracted. Activate it by saying _"dream"_, _"/dream"_, or _"consolidate memory"_.

---

## Customisation Guide

| What you want to do | Where to look |
| --- | --- |
| Add project-specific instructions | `copilot-instructions.md` — fill in the placeholder sections |
| Add a new agent | Create `agents/<name>.agent.md` (auto-discovered via `plugin.json`) |
| Add a new skill | Use the **add-skill** skill, or manually create `skills/<name>/SKILL.md` and register in `plugin.json` |
| Add a new MCP server | Use the **add-mcp** skill, or manually create `mcps/<name>_mcp.py` and register in `.mcp.json` |
| Add or change a startup hook | Edit `hooks/*.json` and point it at a script in `scripts/` |
| Add or change a heartbeat job | Edit `.heartbeats.json`; the next session start will resync it |
| Record a technical decision | Add an entry to `memory/decision-log.md` |
| Document a repeatable workflow | Add steps to `memory/workflows.md` |

---

## Requirements

- [GitHub Copilot CLI](https://docs.github.com/en/copilot) with plugin support
- [uv](https://docs.astral.sh/uv/) (for running MCP servers)
- Python ≥ 3.12 (for the MCP scripts)
