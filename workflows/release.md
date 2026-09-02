# Release Workflow

## Scope
Production release preparation, review, and shipping.

## Steps

### 1. Pre-release Check (ECC)
- All tests passing
- Verification loops complete
- No known critical issues

### 2. Engineering Review (gstack)
- Route to gstack engineering review
- Architecture validation

### 3. Security Review (Addy + ECC)
- Security hardening check
- Dependency vulnerability scan
- Credential exposure check

### 4. QA (gstack)
- Quality assurance workflow
- Regression testing

### 5. Completion Audit (Unlazy — if substantial)
- Acceptance gates
- Verify all stated requirements met
- Depth tree verification

### 6. Product Review (gstack — optional)
- CEO/product review for major features
- Design review if UI changes

### 7. Ship (gstack)
- Version bump
- Changelog update
- Deploy

### 8. Post-release (gstack)
- Monitor
- Retrospective if needed

## Capabilities Activated
- **Always**: ECC + gstack
- **Security review**: + Addy
- **Substantial release**: + Unlazy
- **UI changes**: + OpenDesign or Agency design specialist
