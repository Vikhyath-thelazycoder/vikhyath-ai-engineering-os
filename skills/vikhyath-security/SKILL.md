---
name: vikhyath-security
description: Security-focused capability activation. Routes to ECC security practices, Addy hardening skills, and Agency security specialists.
---

# Vikhyath Security Skill

## Purpose

Activate security-relevant capabilities when the task involves security-sensitive code.

## When Activated

- Authentication/authorization changes
- Credential management
- Encryption implementation
- Vulnerability remediation
- Security audits
- OWASP compliance
- Input validation
- API security

## Capabilities Routed

### ECC (Security Practices)
- Security scanning workflows
- Security-aware code review
- Verification loops for security changes

### Addy Agent Skills (Security Hardening)
- OWASP Top 10 checks
- Security hardening practices
- Vulnerability detection
- Secure coding patterns

### Agency Agents (Security Specialist)
- Security specialist agent for domain-specific review
- Only activated when expert review adds clear value

## Security Review Checklist

When this skill is activated, ensure the routing addresses:

1. [ ] Input validation
2. [ ] Authentication/authorization correctness
3. [ ] Credential exposure (no secrets in code)
4. [ ] SQL injection / XSS / CSRF protection
5. [ ] Dependency vulnerability check
6. [ ] API security (rate limiting, auth)
7. [ ] Error handling (no stack trace exposure)
8. [ ] Logging (no sensitive data in logs)

## Anti-Patterns

- ❌ Running full security audit for non-security changes
- ❌ Skipping security review for auth-related code
- ❌ Loading all Agency specialists for a simple security fix
