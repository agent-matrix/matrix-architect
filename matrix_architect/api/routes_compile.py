from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..compiler import CompileError, compile_plan

router = APIRouter()


class CompileRequest(BaseModel):
    plan: Dict[str, Any]


@router.post("/compile")
async def compile_v2(req: CompileRequest) -> Dict[str, Any]:
    try:
        return compile_plan(req.plan)
    except CompileError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
