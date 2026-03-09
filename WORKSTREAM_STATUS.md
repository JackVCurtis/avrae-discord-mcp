# Workstream Status Board

## Assumptions & Ambiguities
- `PLAN.md` is missing from repository root; architecture execution was derived from `README.md` MVP integration plan and milestone checklist.
- Minimal assumptions applied:
  1. MVP `avrae_command` maps to Discord message format `!{command} {args}` (with args optional).
  2. Response correlation uses FIFO per channel + Avrae bot author identity.
  3. Parsed response fields are intentionally lightweight for MVP (`dice_total` best-effort extraction).

## Dependency Graph
- WS-1 (Planning/Status) -> [WS-2, WS-3, WS-4]
- WS-2 (Discord Relay Core) -> WS-3 (MCP Tool Interface)
- WS-2 (Discord Relay Core) -> WS-4 (QA/Async Tests)
- WS-3 (MCP Tool Interface) -> WS-4 (QA/Smoke)

Parallelizable groups:
- Group A: WS-2 + WS-4 (TDD test authoring and implementation loop)
- Group B: WS-3 + WS-4 (integration and smoke checks)

Critical path (executed): WS-1 -> WS-2 -> WS-3 -> WS-4

## Streams

### WS-1: Planning & Status Tracking
- **Owner Role:** Program Manager / Docs
- **Dependency IDs:** none
- **Start Criteria:** Repository initialized.
- **Done Criteria:** Workstreams defined, dependency graph recorded, status board maintained through completion.
- **Status:** done

### WS-2: Discord Relay Core
- **Owner Role:** Backend Engineer
- **Dependency IDs:** WS-1
- **Start Criteria:** Stream plan approved.
- **Done Criteria:** Command formatting, response correlation, timeout, and metadata handling implemented.
- **Deliverables:** `src/avrae_mcp_server/relay.py`, relay tests.
- **Status:** done

### WS-3: MCP Tool Interface
- **Owner Role:** Platform/Backend Integration
- **Dependency IDs:** WS-1, WS-2
- **Start Criteria:** Relay core available.
- **Done Criteria:** MCP server registers `avrae_command` and returns required payload.
- **Deliverables:** Updated `src/avrae_mcp_server/server.py` + config wiring.
- **Status:** done

### WS-4: QA & Validation
- **Owner Role:** QA Engineer
- **Dependency IDs:** WS-2, WS-3
- **Start Criteria:** Initial test scaffolding exists.
- **Done Criteria:** Relevant unit/async/smoke tests passing.
- **Deliverables:** `tests/test_relay.py`, `tests/test_server.py`, expanded `tests/test_config.py`.
- **Status:** done

## Live Status Board
| ID | Stream | Status |
|---|---|---|
| WS-1 | Planning & Status Tracking | done |
| WS-2 | Discord Relay Core | done |
| WS-3 | MCP Tool Interface | done |
| WS-4 | QA & Validation | done |

## Major Step Log
1. Planned workstreams + dependency graph and initialized status board.
2. Added failing relay/config tests first (TDD red).
3. Implemented relay and config updates (TDD green).
4. Integrated `avrae_command` MCP tool with relay/lifecycle wiring.
5. Added smoke test with isolated dependency stubs for offline environment.
6. Ran full `pytest` successfully.

## Remaining Blockers / Open Questions
- No functional blockers remain for the implemented MVP scope.
- Open question for future iteration: improve overlap correlation beyond FIFO if Avrae responses arrive out of command order.

## Critical Path Analysis & ETC
- Remaining critical path length: 0 active streams.
- Estimated time-to-complete remaining work in current scope: 0h.
- Suggested future enhancement path: advanced correlation strategy (~2-4h), richer parsed fields (~2h), Discord integration smoke in networked CI (~1-2h).
