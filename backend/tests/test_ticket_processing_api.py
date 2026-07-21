import logging

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resolution import Resolution
from app.observability.metrics import pipeline_metrics
from app.schemas.ticket_processing import TicketProcessingResponse


async def resolution_count(session: AsyncSession, ticket_id) -> int:
    return await session.scalar(
        select(func.count(Resolution.id)).where(Resolution.ticket_id == ticket_id)
    ) or 0


async def test_process_ticket_returns_schema_and_persists_resolution(
    client: AsyncClient,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
    seeded_ticket_ids,
) -> None:
    ticket_id = seeded_ticket_ids["eligible_refund"]
    before_count = await resolution_count(db_session, ticket_id)

    response = await client.post(f"/api/v1/tickets/{ticket_id}/process", headers=auth_headers)

    assert response.status_code == 200
    result = TicketProcessingResponse.model_validate(response.json())
    assert result.ticket_id == ticket_id
    assert result.resolution.persisted_resolution_id
    assert await resolution_count(db_session, ticket_id) == before_count + 1
    persisted = await db_session.get(Resolution, result.resolution.persisted_resolution_id)
    assert persisted is not None
    assert persisted.ticket_id == ticket_id


async def test_process_ticket_clears_guardrail_for_eligible_refund(
    client: AsyncClient,
    auth_headers: dict[str, str],
    seeded_ticket_ids,
) -> None:
    ticket_id = seeded_ticket_ids["eligible_refund"]

    response = await client.post(f"/api/v1/tickets/{ticket_id}/process", headers=auth_headers)

    result = TicketProcessingResponse.model_validate(response.json())
    assert result.guardrail.passed is True
    assert result.guardrail.requires_human is False


async def test_process_ticket_requires_human_review_for_high_value_refund(
    client: AsyncClient,
    auth_headers: dict[str, str],
    seeded_ticket_ids,
) -> None:
    ticket_id = seeded_ticket_ids["high_value_refund"]

    response = await client.post(f"/api/v1/tickets/{ticket_id}/process", headers=auth_headers)

    result = TicketProcessingResponse.model_validate(response.json())
    assert result.guardrail.passed is False
    assert result.guardrail.requires_human is True
    assert result.requires_human is True


async def test_processing_happy_path_from_login_to_persisted_resolution(
    client: AsyncClient,
    admin_user,
    db_session: AsyncSession,
    seeded_ticket_ids,
) -> None:
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "test-password"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    tickets = await client.get("/api/v1/tickets", headers=headers)
    assert tickets.status_code == 200
    ticket_id = seeded_ticket_ids["eligible_refund"]
    assert any(ticket["id"] == str(ticket_id) for ticket in tickets.json())

    ticket = await client.get(f"/api/v1/tickets/{ticket_id}", headers=headers)
    assert ticket.status_code == 200

    processing = await client.post(f"/api/v1/tickets/{ticket_id}/process", headers=headers)
    assert processing.status_code == 200
    result = TicketProcessingResponse.model_validate(processing.json())

    persisted = await db_session.get(Resolution, result.resolution.persisted_resolution_id)
    assert persisted is not None
    assert persisted.ticket_id == ticket_id


async def test_processing_emits_observability_metadata(
    client: AsyncClient,
    auth_headers: dict[str, str],
    seeded_ticket_ids,
    caplog,
) -> None:
    before = await pipeline_metrics.snapshot()
    caplog.set_level(logging.INFO, logger="acra.observability")

    response = await client.post(
        f"/api/v1/tickets/{seeded_ticket_ids['eligible_refund']}/process",
        headers=auth_headers,
    )

    assert response.status_code == 200
    after = await pipeline_metrics.snapshot()
    assert after.pipeline_successes == before.pipeline_successes + 1
    observed_agents = (
        "classification",
        "context_retrieval",
        "priority",
        "planning",
        "guardrails",
        "resolution",
    )
    assert all(
        after.agent_successes.get(agent, 0) == before.agent_successes.get(agent, 0) + 1
        for agent in observed_agents
    )

    pipeline_records = [
        record for record in caplog.records if record.name == "acra.observability"
    ]
    correlation_ids = {
        record.correlation_id
        for record in pipeline_records
        if getattr(record, "correlation_id", None)
    }
    assert len(correlation_ids) == 1
