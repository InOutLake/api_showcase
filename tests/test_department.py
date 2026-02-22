import pytest


@pytest.mark.asyncio
async def test_create_department_whitespace_trim(client):
    response = await client.post("/departments/", json={"name": "  Backend  ", "parent_id": None})
    assert response.status_code == 200
    assert response.json()["name"] == "Backend"


@pytest.mark.asyncio
async def test_create_duplicate_name_under_same_parent(client):
    await client.post("/departments/", json={"name": "Dev", "parent_id": None})
    response = await client.post("/departments/", json={"name": "Dev", "parent_id": None})
    assert response.status_code in [400, 409]


@pytest.mark.asyncio
async def test_create_employee_non_existent_dept(client):
    response = await client.post(
        "/departments/999/employees",
        json={"full_name": "John Doe", "position": "Engineer", "hired_at": "2023-01-01", "department_id": 999},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_prevent_circular_dependency(client):
    root = await client.post("/departments/", json={"name": "Root", "parent_id": None})
    root_id = root.json()["id"]
    child = await client.post("/departments/", json={"name": "Child", "parent_id": root_id})
    child_id = child.json()["id"]

    response = await client.patch(f"/departments/{root_id}", json={"parent_id": child_id})
    assert response.status_code in [400, 409]


@pytest.mark.asyncio
async def test_get_department_depth(client):
    res_a = await client.post("/departments/", json={"name": "A", "parent_id": None})
    id_a = res_a.json()["id"]
    res_b = await client.post("/departments/", json={"name": "B", "parent_id": id_a})
    id_b = res_b.json()["id"]
    await client.post("/departments/", json={"name": "C", "parent_id": id_b})

    response = await client.get(f"/departments/{id_a}?depth=1")
    data = response.json()
    assert len(data["children"]) == 1
    assert data["children"][0]["children"] is None


@pytest.mark.asyncio
async def test_delete_reassign_mode(client):
    dept_a = (await client.post("/departments/", json={"name": "A", "parent_id": None})).json()
    dept_b = (await client.post("/departments/", json={"name": "B", "parent_id": None})).json()

    emp = await client.post(
        f"/departments/{dept_a['id']}/employees",
        json={"full_name": "Mover", "position": "Staff", "department_id": dept_a["id"]},
    )

    await client.delete(f"/departments/{dept_a['id']}?mode=reassign&reassign_to_department_id={dept_b['id']}")
    res_dep = (await client.get(f"/departments/{dept_b['id']}")).json()
    assert len(res_dep["employees"]) > 0
    assert res_dep["employees"].pop()["id"] == emp["id"]


@pytest.mark.asyncio
async def test_delete_cascade_mode(client):
    parent_res = await client.post("/departments/", json={"name": "Headquarters"})
    p_id = parent_res.json()["id"]

    child_res = await client.post("/departments/", json={"name": "Sub-Office", "parent_id": p_id})
    c_id = child_res.json()["id"]

    await client.post(
        f"/departments/{c_id}/employees",
        json={"full_name": "Ghost in the shell", "position": "Dev", "department_id": c_id},
    )

    response = await client.delete(f"/departments/{p_id}?mode=cascade")
    assert response.status_code == 204

    p_check = await client.get(f"/departments/{p_id}")
    assert p_check.status_code == 404

    c_check = await client.get(f"/departments/{c_id}")
    assert c_check.status_code == 404
