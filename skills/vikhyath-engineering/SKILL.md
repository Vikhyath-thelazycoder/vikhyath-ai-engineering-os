---
name: vikhyath-engineering
description: Engineering task orchestration via ECC foundation. Routes engineering work to ECC workflows, planning, implementation, testing, and verification capabilities.
---

# Vikhyath Engineering Skill

## Purpose

Route engineering tasks to the ECC engineering foundation and supplement with relevant capabilities.

## When Activated

This skill activates for any engineering task including:
- Implementation
- Planning
- Testing
- Code review
- Verification
- Bug fixing

## Routing

### Standard Engineering Task

1. Use ECC engineering workflows for planning, implementation, and verification
2. Follow ECC's TDD, security scanning, and code review practices
3. Do NOT duplicate ECC's methodology — route to it

### With Codebase Complexity

If the codebase is unfamiliar or complex, supplement with:
- **Graphify** for codebase intelligence and dependency analysis

### With Security Requirements

If the task involves security-sensitive code, supplement with:
- **Addy Agent Skills** for security hardening and OWASP practices
- Relevant **Agency** security specialist if needed

### With Completion Requirements

If the task is substantial or explicitly requires exhaustive completion, supplement with:
- **Unlazy** for acceptance gates and depth trees

## ECC Integration

ECC provides the following that this skill routes to:
- Engineering workflows (planning → implementation → testing → review → verification)
- TDD workflow skills
- Security scanning skills
- Code review skills
- Verification loops
- Production readiness checks

### Installation Verification

Before routing to ECC, verify it is installed:
- Codex: Check if `affaan-m/ECC` plugin is installed
- Claude: Check for CLAUDE.md / .claude-plugin from ECC
- Antigravity: Check for ECC skills in workspace

If ECC is not installed, provide installation instructions from `integrations/ecc.yaml`.

## Anti-Patterns

- ❌ Reimplementing ECC's planning methodology
- ❌ Duplicating ECC's security checklists
- ❌ Creating parallel testing workflows
- ❌ Loading all ECC skills when only one is needed
