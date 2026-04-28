import pytest
import requests

BASE_URL = "http://localhost:8080/api/auth"

def test_check_me_global_user(global_user):
    # Проверка авторизации глобального юзера
    response = requests.get(f"{BASE_URL}/me", headers=global_user["headers"])
    assert response.status_code == 200
    # Проверка, что API вернуло данные именно того пользователя
    assert response.json()["login"].startswith("test_user_")

def test_check_me_poor_user(poor_user):
    # Проверка авторизации poor пользователя. Проверка, что система не путает сессии разных юзеров.
    response = requests.get(f"{BASE_URL}/me", headers=poor_user["headers"])
    assert response.status_code == 200
    assert response.json()["login"].startswith("poor_user_")

def test_access_denied_without_token():
    # Обработка ошибок при отсутствии токена. Система должна вернуть 401 Unauthorized.
    response = requests.get(f"{BASE_URL}/me") # Без headers
    assert response.status_code == 401
    assert "Not authenticated" in str(response.json())

def test_access_denied_invalid_token():
    # Обработка ошибок при неверном токене.
    headers = {"Authorization": "Bearer click-me-i-am-fake-token"}
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    
    # "Не удалось валидировать токен"
    assert response.status_code == 401
    assert "валидировать" in response.json()["detail"]