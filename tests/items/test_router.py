import pytest
from httpx import AsyncClient


@pytest.fixture
async def item(client: AsyncClient) -> dict:
    """Create a single item and return its JSON payload."""
    response = await client.post("/items", json={"title": "Fixture Item"})
    assert response.status_code == 201
    return response.json()


async def test_create_item(client: AsyncClient) -> None:
    response = await client.post(
        "/items", json={"title": "My Item", "description": "A description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Item"
    assert data["description"] == "A description"
    assert "id" in data
    assert "created_at" in data


async def test_create_item_without_description(client: AsyncClient) -> None:
    response = await client.post("/items", json={"title": "No Desc"})
    assert response.status_code == 201
    assert response.json()["description"] is None


async def test_create_item_empty_title_rejected(client: AsyncClient) -> None:
    response = await client.post("/items", json={"title": ""})
    assert response.status_code == 422


async def test_list_items_returns_total(client: AsyncClient) -> None:
    await client.post("/items", json={"title": "Item A"})
    await client.post("/items", json={"title": "Item B"})

    response = await client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] == 2
    assert len(data["items"]) == 2


async def test_list_items_pagination(client: AsyncClient) -> None:
    for i in range(5):
        await client.post("/items", json={"title": f"Page Item {i}"})

    page1 = await client.get("/items", params={"limit": 2, "offset": 0})
    assert page1.status_code == 200
    data1 = page1.json()
    assert len(data1["items"]) == 2
    assert data1["total"] == 5

    page2 = await client.get("/items", params={"limit": 2, "offset": 2})
    assert page2.status_code == 200
    data2 = page2.json()
    assert len(data2["items"]) == 2
    ids1 = {item["id"] for item in data1["items"]}
    ids2 = {item["id"] for item in data2["items"]}
    assert ids1.isdisjoint(ids2)


async def test_list_items_limit_validation(client: AsyncClient) -> None:
    response = await client.get("/items", params={"limit": 0})
    assert response.status_code == 422

    response = await client.get("/items", params={"limit": 101})
    assert response.status_code == 422


async def test_get_item(client: AsyncClient, item: dict) -> None:
    response = await client.get(f"/items/{item['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == item["id"]


async def test_get_item_not_found(client: AsyncClient) -> None:
    response = await client.get("/items/999999")
    assert response.status_code == 404


async def test_update_item_title(client: AsyncClient, item: dict) -> None:
    response = await client.patch(
        f"/items/{item['id']}", json={"title": "Updated Title"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


async def test_update_item_description(client: AsyncClient, item: dict) -> None:
    response = await client.patch(
        f"/items/{item['id']}", json={"description": "New desc"}
    )
    assert response.status_code == 200
    assert response.json()["description"] == "New desc"
    assert response.json()["title"] == item["title"]


async def test_update_item_empty_body_is_noop(client: AsyncClient, item: dict) -> None:
    response = await client.patch(f"/items/{item['id']}", json={})
    assert response.status_code == 200
    assert response.json()["title"] == item["title"]


async def test_update_item_null_title_rejected(client: AsyncClient, item: dict) -> None:
    response = await client.patch(f"/items/{item['id']}", json={"title": None})
    assert response.status_code == 422


async def test_update_item_not_found(client: AsyncClient) -> None:
    response = await client.patch("/items/999999", json={"title": "Ghost"})
    assert response.status_code == 404


async def test_delete_item(client: AsyncClient, item: dict) -> None:
    response = await client.delete(f"/items/{item['id']}")
    assert response.status_code == 204

    get_response = await client.get(f"/items/{item['id']}")
    assert get_response.status_code == 404


async def test_delete_item_not_found(client: AsyncClient) -> None:
    response = await client.delete("/items/999999")
    assert response.status_code == 404
