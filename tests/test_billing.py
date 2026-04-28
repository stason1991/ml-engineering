import pytest
import requests

BASE_URL = "http://localhost:8080/api/wallets"

def test_wallet_creation_for_new_user(poor_user):
    # Создание кошелька для нового пользователя c 0 на балансе. Используем poor_user, так как у него кошелька нет.
    payload = {
        "user_id": poor_user["id"], 
        "balance": 0.0
    }
    response = requests.post(f"{BASE_URL}/", json=payload, headers=poor_user["headers"])
    
    assert response.status_code == 201
    assert response.json()["balance"] == 0.0
    assert response.json()["user_id"] == poor_user["id"]

def test_get_current_balance(global_user):
    # Получение текущего баланса
    user_id = global_user["id"]
    response = requests.get(f"{BASE_URL}/{user_id}", headers=global_user["headers"])
    
    assert response.status_code == 200
    assert "balance" in response.json()

def test_top_up_balance(global_user):
    # Пополнение и корректное обновление баланса. PATCH-запрос должен увеличивать сумму.
    user_id = global_user["id"]
    headers = global_user["headers"]

    # Узнаем баланс до пополнения
    initial_res = requests.get(f"{BASE_URL}/{user_id}", headers=headers)
    initial_balance = initial_res.json()["balance"]

    # Пополняем на 500.0
    top_up_amount = 500.0
    response = requests.patch(
        f"{BASE_URL}/{user_id}", 
        json={"balance": top_up_amount}, 
        headers=headers
    )
    
    assert response.status_code == 200
    # Проверяем, что баланс увеличился
    new_balance = response.json()["balance"]
    assert new_balance == initial_balance + top_up_amount

def test_duplicate_wallet_error(global_user):
    # проверяем, что нельзя создать второй кошелек для одного юзера.
    payload = {
        "user_id": global_user["id"], 
        "balance": 100.0
    }
    response = requests.post(f"{BASE_URL}/", json=payload, headers=global_user["headers"])
    
    # Ожидаем 400 Bad Request, т.к. кошелек уже был создан в ходе других тестов
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"]