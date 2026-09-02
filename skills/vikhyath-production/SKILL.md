---
name: vikhyath-production
description: Production readiness orchestration. Routes to Addy Agent Skills for production engineering and gstack for release workflows.
---

# Vikhyath Production Skill

## Purpose

Ensure production readiness by routing to specialized production engineering and release capabilities.

## When Activated

- Production deployments
- Release preparation
- Performance review
- Reliability engineering
- Production incidents

## Capabilities Routed

### Addy Agent Skills (Production Engineering)
- Code review
- Security hardening
- Testing best practices
- Performance optimization
- Reliability engineering

### gstack (Release Workflows)
- Engineering review
- CEO/product review
- Design review
- QA workflows
- Ship workflows
- Retrospectives

## Workflow

1. **Pre-release**: Use ECC for engineering verification
2. **Review**: Route to gstack review workflows
3. **Security**: Use Addy for security hardening review
4. **QA**: Route to gstack QA workflows
5. **Ship**: Use gstack shipping workflows
6. **Post-release**: gstack retrospective

## Anti-Patterns

- ❌ Running full gstack suite for simple changes
- ❌ Loading all review workflows for non-release tasks
- ❌ Skipping ECC verification before review
