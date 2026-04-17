# Copilot Instructions

## Project Overview

## Commands

## Key Conventions


# Memory Bank Protocol
You are an AI assistant integrated into a project with a persistent memory system. 

## 1. Initialization (Read Phase)
At the start of any new task or session, you MUST silently read the following files via your workspace context to understand the current state:
- `.github/memory/project-context.md`
- `.github/memory/active-task.md`

## 2. Execution (Action Phase)
When asked how to perform a routine task, check `.github/memory/workflows.md` first before generating a generic solution. If proposing an architectural change, review `.github/memory/decision-log.md` to avoid contradicting established patterns.

## 3. Persistence (Write Phase)
When we complete a significant milestone, solve a complex bug, or make an architectural decision, I will ask you to "update the memory." You must then propose file edits to the relevant files in the `.github/memory/` directory to reflect the new state.

## 4. Maintenance (Dream Phase)
When the user says "dream", "/dream", or "consolidate memory", use the **dream** skill to consolidate, prune, and optimize the memory bank. The skill reads all memory files, follows the rules in `.github/memory/dream-protocol.md`, and presents the updated file contents for review.
