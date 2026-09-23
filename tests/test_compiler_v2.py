import pytest

from matrix_architect.compiler import CompileError, compile_plan


def _plan():
    return {
        "schema_version": "2.0",
        "plan_id": "p1",
        "goal": "repair service",
        "steps": [
            {
                "step_id": "s1",
                "objective": "inspect",
                "capability": "repo.read",
                "depends_on": [],
                "success_criteria": ["root cause identified"],
                "verifiers": ["diagnostic_check"],
                "risk": "low",
            },
            {
                "step_id": "s2",
                "objective": "patch",
                "capability": "fs.apply_patch",
                "depends_on": ["s1"],
                "success_criteria": ["tests pass"],
                "verifiers": ["pytest"],
                "rollback": "git reset --hard",
                "risk": "medium",
            },
        ],
    }


def test_compiles_dependency_graph():
    graph = compile_plan(_plan())
    assert graph["plan_id"] == "p1"
    assert graph["nodes"][1]["depends_on"] == ["s1"]
    assert graph["execution_policy"]["authority"] == "matrix-os"


def test_rejects_missing_proof():
    plan = _plan()
    plan["steps"][0]["verifiers"] = []
    with pytest.raises(CompileError):
        compile_plan(plan)
