# TL_CHAT_UNIFIED_DATA_ACCESS_VERTICAL_SLICE_002

## Status

- `STATUS`: `AUTHORIZED`
- `MODE`: `READ_ONLY_FIRST`
- `CAPABILITY`: `TL_CHAT_UNIFIED_DATA_ACCESS_001`
- `SLICE`: `VERTICAL_SLICE_002`

## Objective

Enable the next minimal governed slice for TL Chat unified data access:

> TL Chat answers questions about order/shipping-date data only when an authorized, read-only, governed source exists; otherwise it returns an explicit blocked or missing-data response.

## Scope in

- order-related question detection;
- shipping-date-related question detection;
- source authorization check;
- read-only source availability check;
- response with `source`, `status`, and `confidence` when data is available;
- explicit `MISSING_DATA`, `SOURCE_AUTHORIZED_BUT_UNAVAILABLE`, or equivalent governed block when data is unavailable;
- no invented order or shipping-date data.

## Scope out

- OCR;
- UI changes;
- planner;
- autonomous agent runtime;
- DB mutation;
- SMFAdapter activation;
- arbitrary path access;
- production planning decisions;
- automatic promotion to `CERTO`;
- cloud processing;
- write operations.

## Acceptance criteria

Given a TL Chat prompt about an order or shipping date:

1. If an authorized read-only source is available, TL Chat returns the relevant data with `source`, `status`, and `confidence`.
2. If the source is unavailable, unsafe, or not governed, TL Chat declares the missing or blocked state.
3. TL Chat does not invent order data.
4. TL Chat does not make production decisions.
5. No mutation occurs.
6. No runtime implementation is authorized by this document alone.

## Governance

This slice authorizes only the perimeter definition.

Runtime changes require a separate preflight and explicit approval after source mapping.
