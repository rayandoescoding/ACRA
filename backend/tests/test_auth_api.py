from uuid import uuid4

from httpx import AsyncClient


async def test_login_succeeds_for_active_admin(client: AsyncClient, admin_user) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "test-password"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


async def test_login_rejects_invalid_credentials(client: AsyncClient, admin_user) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "incorrect-password"},
    )

    assert response.status_code == 401


async def test_protected_ticket_endpoint_rejects_missing_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/tickets")

    assert response.status_code == 401


async def test_support_agent_cannot_approve_resolution(
    client: AsyncClient,
    support_agent_headers: dict[str, str],
) -> None:
    response = await client.post(
        f"/api/v1/resolutions/{uuid4()}/approve",
        headers=support_agent_headers,
    )

    assert response.status_code == 403
