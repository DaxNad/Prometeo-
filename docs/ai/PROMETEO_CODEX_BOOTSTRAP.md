# PROMETEO — CODEX BOOTSTRAP

## mandatory read order

Before proposing any code change, always read:

1. docs/ai/prometeo_coder_profile.md
2. docs/ai/PROMETEO_CODER_SYSTEM_PROMPT.md
3. docs/ai/PROMETEO_ARCH_GUARDS.md
4. docs/ai/PROMETEO_DOMAIN_RULES.md
5. docs/ai/PROMETEO_TASK_ROUTING.md
6. docs/ai/PROMETEO_REPO_MAP.md

---

## operational identity

You are working on PROMETEO.

PROMETEO is an event-driven industrial orchestration system.

It is not a generic CRUD app.

It models:

- Order as aggregate root
- ProductionEvent as real execution event
- Station as physical production resource
- SMF as interoperability bridge, not source of truth

---

## hard constraints

Never break:

- Order → ProductionEvent relationship
- station compatibility semantics
- SMF bridge integrity
- planner explainability
- event-driven architecture

Never introduce:

- hidden side effects
- duplicate mapping layers
- silent schema assumptions
- parallel sources of truth
- speculative abstractions

---

## allowed safe work

Preferred tasks:

- read-only diagnostic endpoints
- explicit explainability fields
- small service refactors preserving contracts
- compatibility tables
- typing improvements
- planner improvements with stable output contract

---

## disallowed unsafe work

Do not:

- change canonical order identity
- redefine event semantics
- bypass station constraints
- couple planner to hidden runtime assumptions
- treat SMF as authoritative source of truth

---

## repository focus

Primary safe zones:

- backend/app/api/
- backend/app/services/
- backend/app/planner/
- docs/ai/

Use caution in:

- backend/app/models/
- backend/app/smf/
- backend/app/data/

---

## patch policy

Prefer:

- minimal diff
- explicit reasoning
- one concern per patch
- branch + PR workflow
- no direct push to main

Always show:

- touched files
- architectural impact
- why the change is safe

---

## merge policy

For repository changes:

- create branch
- push branch
- open PR
- wait for required checks
- merge via squash

---

## expected checks

Current required checks for merge:

- frontend
- smf-backend-tests

---

## output style

When proposing a patch:

- be concrete
- be minimal
- be domain-aware
- avoid generic refactors
- prefer consistency over cleverness
