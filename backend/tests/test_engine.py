from typing import Any

from app import engine


def _answers(**overrides: Any) -> dict[str, Any]:
    base = {
        "stage": "greenfield",
        "current_stack": "none",
        "ops_capacity": "server",
        "high_availability": "no",
        "traffic_pattern": "steady",
        "traffic_volume": "moderate",
        "data_type": "relational",
        "team_size": "small",
        "structure": "monolith",
        "request_duration": "short",
        "portability": "no",
        "commitment": "no",
        "requests_per_month": 1_000_000,
        "storage_gb": 10,
        "transfer_gb": 10,
    }
    base.update(overrides)
    return base


def test_serverless() -> None:
    result = engine.recommend(
        _answers(ops_capacity="managed", traffic_pattern="spiky", traffic_volume="low")
    )
    assert result["archetype"] == "serverless"


def test_single_server() -> None:
    result = engine.recommend(
        _answers(
            stage="existing",
            current_stack="server",
            traffic_pattern="flat",
            traffic_volume="low",
            team_size="solo",
        )
    )
    assert result["archetype"] == "single_server"


def test_classic() -> None:
    result = engine.recommend(
        _answers(stage="existing", current_stack="server", high_availability="yes")
    )
    assert result["archetype"] == "classic"


def test_fargate() -> None:
    result = engine.recommend(
        _answers(
            ops_capacity="containers", request_duration="long", high_availability="yes"
        )
    )
    assert result["archetype"] == "fargate"


def test_eks() -> None:
    result = engine.recommend(
        _answers(
            stage="existing",
            current_stack="containers",
            ops_capacity="kubernetes",
            high_availability="yes",
            traffic_volume="high",
            team_size="several",
            structure="microservices",
            portability="yes",
        )
    )
    assert result["archetype"] == "eks"


def test_cost_is_positive() -> None:
    result = engine.recommend(_answers())
    assert result["monthly_cost"] > 0
    assert result["candidates"]
