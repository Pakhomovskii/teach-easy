import pytest


@pytest.mark.asyncio
async def test_create_course_invalid_teacher(client):
    client_instance = await client

    course_data = {
        "title": "New Test Course",
        "description": "This is a test course description",
        "teacher_id": 99999,
        "icon_id": 1
    }

    response = await client_instance.post("/courses/", json=course_data)
    assert response.status == 400
    response_json = await response.json()
    assert response_json["detail"] == "Teacher not found"
