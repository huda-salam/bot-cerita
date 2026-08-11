from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .visual_benchmark import create_case, start_run, score_run
from .benchmark_persistence import save_case, save_run

router = APIRouter()
_CASES = {}
_RUNS = {}

class BenchmarkCaseRequest(BaseModel):
    name: str
    panel_prompts: list[str] = Field(min_length=1, max_length=100)
    reference_asset_ids: list[str] = Field(default_factory=list)
    requirements: dict[str, bool] = Field(default_factory=dict)

class BenchmarkRunRequest(BaseModel):
    case_id: str
    provider: str
    model: str

class BenchmarkScoreRequest(BaseModel):
    scores: dict[str, float]

@router.post('/benchmarks/cases')
async def create_benchmark_case(request: BenchmarkCaseRequest):
    case = create_case(request.name, request.panel_prompts, request.reference_asset_ids, request.requirements)
    _CASES[case.id] = case
    save_case(case)
    return case

@router.get('/benchmarks/cases')
async def list_benchmark_cases():
    return list(_CASES.values())

@router.post('/benchmarks/runs')
async def create_benchmark_run(request: BenchmarkRunRequest):
    case = _CASES.get(request.case_id)
    if not case: raise HTTPException(status_code=404, detail='Benchmark case not found')
    run = start_run(case, request.provider, request.model)
    _RUNS[run.id] = run
    save_run(run)
    return run

@router.post('/benchmarks/runs/{run_id}/score')
async def score_benchmark_run(run_id: str, request: BenchmarkScoreRequest):
    run = _RUNS.get(run_id)
    if not run: raise HTTPException(status_code=404, detail='Benchmark run not found')
    run = score_run(run, request.scores)
    _RUNS[run.id] = run
    save_run(run)
    return run

@router.get('/benchmarks/runs/{run_id}')
async def get_benchmark_run(run_id: str):
    run = _RUNS.get(run_id)
    if not run: raise HTTPException(status_code=404, detail='Benchmark run not found')
    return run
