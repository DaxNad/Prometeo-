# TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_002

## Status

- `STATUS`: `CLOSED`
- `TESTED`: `true`
- `MERGED`: `true`
- `MODE`: `READ_ONLY_FIRST`
- `CAPABILITY`: `TL_CHAT_UNIFIED_DATA_ACCESS_001`
- `SLICE`: `VERTICAL_SLICE_002`
- `SOURCE_ID`: `customer_demand_registry`
- `RUNTIME_BINDING`: `TL_CHAT_READ_ONLY`
- `DEFAULT_POLICY`: `DENY`

## Objective

Enable the minimal governed order/shipping-date slice for TL Chat:

> TL Chat answers customer-demand questions only through an authorized, read-only source and otherwise returns an explicit blocked or missing-data response.

## Delivered scope

- order and shipping-date intent detection;
- source registration as metadata-only;
- separate executable runtime grant;
- read-only database boundary;
- read-only customer-demand reader;
- reader → Context Resolver binding;
- Context Resolver → TL Chat integration;
- pathless `database_registry` source support;
- deterministic end-to-end runtime mapping;
- authorization before query execution;
- explicit provenance and canonical confidence;
- deny path that does not invoke the reader;
- response fields limited to:
  - `articolo`;
  - `codice_articolo`;
  - `quantita`;
  - `data_spedizione`;
  - `priorita_cliente`.

## Semantic constraints

- `data_spedizione` is rendered as the customer-requested date, not as a production promise, internal deadline, plan, or scheduling decision;
- `semantic_status: DA_VERIFICARE`;
- `confidence: DA_VERIFICARE`;
- TL confirmation remains required;
- `planner_eligible: false`;
- `automatic_promotion: false`;
- no automatic promotion to `CERTO`.

## Governed outcomes

### Authorized source and record available

TL Chat returns only the authorized fields with source, status, confidence and provenance.

### Authorized source, record absent

- `source_status: SOURCE_FOUND`;
- `missing_data: record_customer_demand_not_found`;
- no invented order or date data.

### Runtime authorization denied or unavailable

- `source_status: SOURCE_AUTHORIZED_BUT_UNAVAILABLE`;
- `missing_data: customer_demand_runtime_not_authorized`;
- reader not called;
- database connection not opened.

## Scope out

- OCR;
- UI changes;
- planner;
- autonomous agent runtime;
- database mutation;
- SMFAdapter activation;
- arbitrary path access;
- production planning decisions;
- automatic promotion to `CERTO`;
- cloud processing;
- write operations;
- additional customer-demand fields.

## Acceptance evidence

Implementation and governance were delivered through PRs #478–#489.

Final governance/runtime alignment:

- PR: `#489`;
- merge commit: `f5c39c3a0f317861cc0c32697a11f1044472096a`;
- authorized path: PASS;
- deny path: PASS;
- reader called on deny: NO;
- database connection on deny: NO;
- database write: NONE;
- dedicated tests and repository guards: PASS.

Canonical alignment document:

```text
docs/capabilities/CUSTOMER_DEMAND_GOVERNANCE_RUNTIME_ALIGNMENT_001.md
```

## Closure rule

This closure does not authorize another slice, source, runtime binding, planner integration, UI change or write path. Any subsequent work requires a new preflight and explicit human decision.
