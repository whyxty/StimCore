"""API-эндпоинты для расчётов СКО.

Стратегия: для каждой задачи существует функция в core/solvers.py, которая
обёртывает существующие solve() из sko_calculator/modules/tasks/*.py
(чтобы не дублировать математику). Здесь — только маршрутизация HTTP.
"""
from fastapi import APIRouter, HTTPException
from .schemas import WellInputs, CalcResults
from ..core import solvers
from ..core.config import load_default_config

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/config/default")
def get_default_config():
    """Возвращает дефолтный профиль месторождения (Предкарпатье)."""
    return load_default_config()


@router.post("/calc/all", response_model=CalcResults)
def calc_all(inputs: WellInputs):
    """Запускает все 12 задач и возвращает агрегированный результат."""
    try:
        cfg = load_default_config()
        results = solvers.calc_all(inputs.model_dump(), cfg)
        return CalcResults(
            inputs=inputs.model_dump(),
            constants=cfg,
            tasks=results,
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
