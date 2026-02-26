import pytest


@pytest.mark.asyncio
async def test_create_department_whitespace_trim(client):
    response = await client.post("/api/v1/departments", json={"name": "  Backend  ", "parent_id": None})
    assert response.status_code == 200
    assert response.json()["name"] == "Backend"


@pytest.mark.asyncio
async def test_create_duplicate_name_under_same_parent(client):
    await client.post("/api/v1/departments", json={"name": "Dev", "parent_id": None})
    response = await client.post("/api/v1/departments", json={"name": "Dev", "parent_id": None})
    assert response.status_code in [400, 409]


@pytest.mark.asyncio
async def test_create_employee(client):
    dept = (await client.post("/api/v1/departments", json={"name": "A", "parent_id": None})).json()

    response = await client.post(
        f"/api/v1/departments/{dept['id']}/employees",
        json={"full_name": "John Doe", "position": "Engineer", "hired_at": "2023-01-01"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_employee_non_existent_dept(client):
    response = await client.post(
        "/api/v1/departments/999/employees",
        json={"full_name": "John Doe", "position": "Engineer", "hired_at": "2023-01-01"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_prevent_circular_dependency(client):
    root = await client.post("/api/v1/departments", json={"name": "Root", "parent_id": None})
    root_id = root.json()["id"]

    child = await client.post("/api/v1/departments", json={"name": "Child", "parent_id": root_id})
    child_id = child.json()["id"]

    response = await client.patch(f"/api/v1/departments/{root_id}", json={"id": root_id, "parent_id": child_id})
    assert response.status_code in [400, 409]


@pytest.mark.asyncio
async def test_get_department_depth(client):
    res_a = await client.post("/api/v1/departments", json={"name": "A", "parent_id": None})
    id_a = res_a.json()["id"]

    res_b = await client.post("/api/v1/departments", json={"name": "B", "parent_id": id_a})
    id_b = res_b.json()["id"]

    res_c = await client.post("/api/v1/departments", json={"name": "C", "parent_id": id_b})
    id_c = res_c.json()["id"]

    response = await client.get(f"/api/v1/departments/{id_a}", params={"depth": 1, "include_employees": True})
    data = response.json()

    assert "children" in data
    assert len(data["children"]) == 0

    response = await client.get(f"/api/v1/departments/{id_a}", params={"depth": 3, "include_employees": True})
    data = response.json()
    assert "children" in data
    assert "children" in data["children"][0]
    assert data["children"][0]["children"][0]["department"]["id"] == id_c


@pytest.mark.asyncio
async def test_delete_reassign_mode(client):
    dept_a = (await client.post("/api/v1/departments", json={"name": "A", "parent_id": None})).json()
    dept_b = (await client.post("/api/v1/departments", json={"name": "B", "parent_id": None})).json()

    emp = await client.post(
        f"/api/v1/departments/{dept_a['id']}/employees",
        json={"full_name": "John Doe", "position": "Engineer", "hired_at": "2023-01-01"},
    )
    assert emp.status_code == 200

    res = await client.delete(f"/api/v1/departments/{dept_a['id']}?mode=reassign&target_id={dept_b['id']}")
    assert res.status_code == 204
    res_dep = (await client.get(f"/api/v1/departments/{dept_b['id']}")).json()
    print(f"res_dep = {res_dep}")
    assert len(res_dep["employees"]) > 0
