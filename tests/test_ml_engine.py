import pytest
import requests

BASE_URL = "http://localhost:8080/api"

def test_ml_prediction_full_flow(global_user, valid_employee_data):
    # Сквозной сценарий. У global_user уже есть кошелек. Пополняем его, создаем профиль и делаем запрос.
    headers = global_user["headers"]
    user_id = global_user["id"]

    # Пополнение баланса
    requests.patch(f"{BASE_URL}/wallets/{user_id}", json={"balance": 500.0}, headers=headers)

    # Создание профиля
    profile_payload = {
        "user_id": user_id,
        "attributes": valid_employee_data
    }
    resp_prof = requests.post(f"{BASE_URL}/profiles/", json=profile_payload, headers=headers)
    # Используем 201 или 200 (если профиль уже был создан)
    assert resp_prof.status_code in [200, 201]

    # Выполнение ML-запроса
    bal_before = requests.get(f"{BASE_URL}/wallets/{user_id}", headers=headers).json()["balance"]
    
    predict_payload = {
        "model_id": "Career Path Pro",
        "features": valid_employee_data
    }
    resp_ml = requests.post(f"{BASE_URL}/predict/", json=predict_payload, headers=headers)
    
    # Валидация ответа и списания
    assert resp_ml.status_code == 200
    data = resp_ml.json()
    assert data["status"] == "queued"
    
    # Проверка уменьшения баланса
    bal_after = requests.get(f"{BASE_URL}/wallets/{user_id}", headers=headers).json()["balance"]
    assert bal_after == bal_before - 100.0

def test_predict_validation_error(global_user):
    # Проверка защиты от некорректных данных (Pydantic)
    headers = global_user["headers"]
    invalid_payload = {
        "model_id": "Career Path Pro",
        "features": {"gender": 1, "age": 10} # age < 18
    }
    response = requests.post(f"{BASE_URL}/predict/", json=invalid_payload, headers=headers)
    assert response.status_code == 422

def test_predict_insufficient_funds(poor_user, valid_employee_data):
    # Запрет при нулевом балансе. Авто-создание кошелька в predict.py обеспечит баланс 0 для poor_user.
    payload = {"model_id": "Career Path Pro", "features": valid_employee_data}
    
    # Создаем профиль для poor_user
    requests.post(
        f"{BASE_URL}/profiles/", 
        json={"user_id": poor_user["id"], "attributes": valid_employee_data}, 
        headers=poor_user["headers"]
    )

    response = requests.post(f"{BASE_URL}/predict/", json=payload, headers=poor_user["headers"])
    assert response.status_code == 402
    assert "Недостаточно средств" in response.json()["detail"]

def test_history_consistency(global_user):
    # Проверка сохранения истории операций
    headers = global_user["headers"]
    user_id = global_user["id"]

    import time
    time.sleep(0.5) # Даём системе больше времени на запись в БД

    response = requests.get(f"{BASE_URL}/history/{user_id}", headers=headers)
    
    assert response.status_code == 200
    history = response.json()
    
    # Проверяем, что в истории появилась запись после нашего ML-запроса
    print(f"DEBUG History for {user_id}: {history}")
    assert len(history) > 0
    # Проверяем наличие ключевых полей из HistoryResponse
    assert "result" in history[0]
    assert "timestamp" in history[0]