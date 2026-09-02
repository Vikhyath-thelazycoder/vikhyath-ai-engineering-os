# Bugfix Workflow

## Scope
Bug identification, fix, and verification.

## Steps

### 1. Understand (ECC)
- Reproduce the bug
- Identify root cause

### 2. Analyze (Graphify — only if unfamiliar codebase)
- Trace affected code paths
- Identify dependencies

### 3. Fix (ECC)
- Minimal surgical change
- Follow existing patterns

### 4. Test (ECC)
- Add regression test
- Verify fix doesn't break other code

### 5. Verify (ECC)
- Verification loop
- Confirm bug is resolved

## Capabilities Activated
- **Always**: ECC
- **Unfamiliar codebase**: + Graphify
- **Security bug**: + Addy security
