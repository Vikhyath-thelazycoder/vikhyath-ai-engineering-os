---
name: vikhyath-review
description: Code review and quality orchestration. Routes to ECC review workflows, Addy quality skills, and optional gstack review perspectives.
---

# Vikhyath Review Skill

## Purpose

Orchestrate code review by routing to the appropriate review capabilities.

## When Activated

- Code review requests
- Pull request review
- Architecture review
- Quality assessment
- Pre-merge checks

## Capabilities Routed

### ECC (Engineering Review)
- Code review workflows
- Verification loops
- Quality standards

### Addy Agent Skills (Quality Practices)
- Code review best practices
- Testing coverage review
- Performance review

### gstack (Review Perspectives)
- Engineering review
- Design review
- DevEx review
- CEO/product review (for major features)

### Ponytail (Simplicity — Explicit Only)
- Only if explicitly requested
- YAGNI / overengineering detection
- Complexity analysis

## Review Workflow

1. **Scope**: Identify what's being reviewed
2. **Engineering review**: Route to ECC review methodology
3. **Quality check**: Route relevant checks to Addy
4. **Specialist review**: If domain expertise needed, route to Agency specialist
5. **Simplicity**: Only if explicitly requested, route to Ponytail

## Anti-Patterns

- ❌ Auto-activating Ponytail for every review
- ❌ Running all gstack reviews for simple PRs
- ❌ Loading full Agency swarm for basic review
