# Architect v2: compiler boundary

Matrix Architect v2 has one authority: translate an already-governed `PlanIR v2`
into an executable `WorkGraph v1`.

```
Matrix OS -> Matrix AI -> Guardian -> Treasury
          -> Architect.compile -> Runtime/Hive -> MatrixLab
```

The compile endpoint is `POST /v2/compile`.

## Invariants

- no new goal decomposition,
- no model call is required to compile,
- no policy decision is made here,
- no budget is granted here,
- no execution happens here,
- every node carries the plan's proof obligations and rollback instruction,
- the graph declares Matrix OS as authority.

Existing v1 plan/execute APIs remain during migration and should be deprecated only
after Matrix OS live-service conformance is green.
