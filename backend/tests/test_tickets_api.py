from uuid import uuid4

from httpx import AsyncClient


async def test_list_tickets_returns_seeded_records(
    client: AsyncClient,
    auth_headers: dict[str, str],
    seeded_ticket_ids,
) -> None:
    response = await client.get("/api/v1/tickets", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 10
    assert {ticket["id"] for ticket in payload} == {str(ticket_id) for ticket_id in seeded_ticket_ids.values()}


async def test_get_ticket_returns_requested_seeded_ticket(
    client: AsyncClient,
    auth_headers: dict[str, str],
    seeded_ticket_ids,
) -> None:
    ticket_id = seeded_ticket_ids["eligible_refund"]
    response = await client.get(f"/api/v1/tickets/{ticket_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == str(ticket_id)


async def test_get_ticket_returns_404_for_missing_ticket(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.get(f"/api/v1/tickets/{uuid4()}", headers=auth_headers)

    assert response.status_code == 404
