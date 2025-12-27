from __future__ import annotations

from typing import List

from .models import Plan, PolicyGate, RiskLevel

DANGEROUS_CMDS = {"rm -rf", "shutdown", "reboot", "mkfs", "dd "}


def score_plan(plan: Plan) -> PolicyGate:
    reasons: List[str] = []
    risk = RiskLevel.low
    requires_guardian = False

    # Simple heuristics
    total_ops = sum(len(s.ops) for s in plan.steps)
    if total_ops > 25:
        risk = RiskLevel.medium
        reasons.append(f"Large change-set: {total_ops} file ops")

    for step in plan.steps:
        for cmd in step.verify:
            for d in DANGEROUS_CMDS:
                if d in cmd:
                    risk = RiskLevel.high
                    requires_guardian = True
                    reasons.append(f"Dangerous verify command detected: {cmd}")
    allowed = (risk != RiskLevel.high)
    if requires_guardian:
        allowed = False
    return PolicyGate(
        allowed=allowed,
        risk=risk,
        reasons=reasons,
        requires_guardian_approval=requires_guardian,
    )
