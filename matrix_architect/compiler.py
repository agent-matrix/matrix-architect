"""Deterministic PlanIR v2 -> WorkGraph compiler.

Architect v2 compiles approved intent. It does not plan, govern, fund, execute,
or decide whether work succeeded.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List


class CompileError(ValueError):
    pass


def compile_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    if plan.get("schema_version") != "2.0":
        raise CompileError("PlanIR schema_version must be 2.0")
    steps = list(plan.get("steps") or [])
    if not steps:
        raise CompileError("PlanIR requires at least one step")

    nodes: List[Dict[str, Any]] = []
    ids = set()
    for step in steps:
        sid = str(step.get("step_id") or "")
        if not sid or sid in ids:
            raise CompileError(f"invalid or duplicate step_id: {sid!r}")
        ids.add(sid)
        if not step.get("success_criteria") or not step.get("verifiers"):
            raise CompileError(f"step {sid} is missing proof obligations")
        nodes.append({
            "node_id": sid,
            "kind": "capability",
            "capability": step["capability"],
            "objective": step["objective"],
            "depends_on": list(step.get("depends_on") or []),
            "inputs": list(step.get("inputs") or []),
            "preconditions": list(step.get("preconditions") or []),
            "expected_outputs": list(step.get("expected_outputs") or []),
            "proof": {
                "success_criteria": list(step["success_criteria"]),
                "verifiers": list(step["verifiers"]),
            },
            "rollback": step.get("rollback"),
            "risk": step.get("risk", "medium"),
        })

    for node in nodes:
        unknown = set(node["depends_on"]) - ids
        if unknown:
            raise CompileError(f"{node['node_id']} depends on unknown nodes: {sorted(unknown)}")

    digest_source = repr([(n["node_id"], n["capability"], n["depends_on"]) for n in nodes])
    return {
        "schema_version": "1.0",
        "graph_id": hashlib.sha256(digest_source.encode()).hexdigest()[:20],
        "plan_id": plan["plan_id"],
        "goal": plan["goal"],
        "nodes": nodes,
        "execution_policy": {
            "authority": "matrix-os",
            "requires_policy_grant": True,
            "requires_budget_grant": True,
            "verification_required": True,
        },
    }
