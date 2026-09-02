# Feature Workflow

## Scope
End-to-end feature implementation from planning to verification.

## Steps

### 1. Planning (ECC)
- Understand requirements
- Design the approach
- Identify affected components

### 2. Codebase Analysis (Graphify — if needed)
- Only for complex/unfamiliar codebases
- Map dependencies and relationships
- Understand impact scope

### 3. Implementation (ECC)
- Follow ECC engineering methodology
- TDD where appropriate
- Security-aware coding

### 4. Testing (ECC + Addy)
- Unit tests
- Integration tests where relevant
- Security testing for sensitive code

### 5. Review (ECC + optional gstack)
- Self-review via ECC verification loop
- Engineering review if significant
- Security review if auth/security-related

### 6. Completion Check (Unlazy — if substantial)
- Only for multi-part implementations
- Acceptance gates
- Depth tree verification

### 7. Ship
- Commit with meaningful message
- PR if applicable

## Capabilities Activated
- **Always**: ECC
- **Complex codebase**: + Graphify
- **Substantial**: + Unlazy
- **Security-sensitive**: + Addy security
- **Specialist needed**: + Agency specialist
