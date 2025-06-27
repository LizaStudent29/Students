import pytest

def register_and_login(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "password": "testpass",
        "read_only": False
    })
    
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    access_token = response.json().get("access_token")
    assert access_token is not None, "Access token not found"
    return {"Authorization": f"Bearer {access_token}"}

def test_add_student_success(client):
    headers = register_and_login(client)
    data = {
        "last_name": "Иванов",
        "first_name": "Иван",
        "faculty": "ФизФак",
        "course": "1",
        "score": 85
    }

    # Добавляем студента
    response = client.post("/students/", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Студент добавлен"}

    # Получаем список студентов
    response = client.get("/students/", headers=headers)
    assert response.status_code == 200
    students = response.json()

    # Проверяем, что в списке есть строка с фамилией и именем
    assert any("Иванов" in s and "Иван" in s for s in students)

def test_add_student_invalid_data(client):
    headers = register_and_login(client)
    data = {"last_name": "Петров"}  # нет обязательных полей
    response = client.post("/students/", json=data, headers=headers)
    assert response.status_code == 422  # ошибка валидации

def test_add_student_unauthorized(client):
    data = {
        "last_name": "Смирнов",
        "first_name": "Сергей",
        "faculty": "ИстФак",
        "course": "3",
        "score": 70
    }
    # Без токена
    response = client.post("/students/", json=data)
    assert response.status_code == 401
