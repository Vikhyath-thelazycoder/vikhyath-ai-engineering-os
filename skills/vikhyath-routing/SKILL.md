---
name: vikhyath-routing
description: Task classification and capability routing for Vikhyath AI Engineering OS. Determines which external capabilities to activate based on task analysis.
---

# Vikhyath Routing Skill

## Purpose

Classify incoming tasks and route them to the appropriate external capabilities. This is the core orchestration logic of the Vikhyath AI Engineering OS.

## How to Use

When presented with a task, follow this process:

### Step 1: Classify the Task

Analyze the task description and identify which category it falls into:

| Category | Signals |
|---|---|
| Simple bugfix | typo, small fix, one-liner |
| Engineering | implement, build, create, develop |
| Complex codebase | unfamiliar repo, monorepo, large codebase |
| Security | authentication, authorization, encryption, vulnerability |
| Large feature | multi-file, substantial, "don't stop until done" |
| Design | UI, UX, visual, layout, design system |
| Review/release | review, release, ship, deploy, QA |
| Simplicity | YAGNI, overengineered, too complex |
| Refactor | refactor, restructure, clean up |
| Architecture | system design, design patterns, structure |

### Step 2: Activate Capabilities

Based on the classification, activate ONLY the relevant capabilities:

```yaml
simple-bugfix:      [ecc]
engineering:        [ecc, ?addy]
complex-codebase:   [ecc, graphify]
security:           [ecc, addy]
large-feature:      [ecc, unlazy, ?graphify]
design:             [ecc, opendesign]
review-release:     [ecc, gstack]
simplicity:         [ponytail]
refactor:           [ecc, ?graphify, ?ponytail]
architecture:       [ecc, graphify]
```

`?` = optional, activate only if clearly relevant.

### Step 3: Load Only What's Needed

Do NOT pre-load all capability documentation. Load the SKILL.md or relevant instructions for activated capabilities only.

### Step 4: Execute

Use the activated capabilities to complete the task.

### Step 5: Verify and Unload

After task completion, verify the work meets requirements and unload capability context.

## Conflict Resolution

If two capabilities give conflicting advice, follow the priority hierarchy:

1. User requirements
2. Security/safety
3. Project architecture
4. ECC methodology
5. Security/testing specialists
6. Domain specialists
7. Product/review workflows
8. Simplicity optimization

## Anti-Patterns

- ❌ Loading all capabilities at once
- ❌ Activating Ponytail without explicit request
- ❌ Running the full Agency swarm
- ❌ Keeping Graphify graph active unnecessarily
- ❌ Using Unlazy for simple one-line fixes
