# Agent Priorities

## 1. Test-Driven Development (TDD) — REQUIRED
- The agent **MUST** use Test-Driven Development for all code changes whenever tests are feasible.
- Follow the red/green/refactor loop:
  1. Write or update a failing test that captures the desired behavior.
  2. Implement the minimal code needed to make the test pass.
  3. Refactor while keeping all tests passing.
- New features, bug fixes, and behavioral changes should be accompanied by tests first.

## 2. SOLID Principles — STRONGLY RECOMMENDED
- The agent **SHOULD** follow all SOLID principles whenever possible:
  - **S**ingle Responsibility Principle: each class/module should have one clear reason to change.
  - **O**pen/Closed Principle: design components to be open for extension but closed for modification.
  - **L**iskov Substitution Principle: derived types must be safely substitutable for their base types.
  - **I**nterface Segregation Principle: prefer focused interfaces over large, general-purpose ones.
  - **D**ependency Inversion Principle: depend on abstractions, not concretions.
- If constraints prevent full SOLID compliance, choose the design that best preserves maintainability and clarity.
