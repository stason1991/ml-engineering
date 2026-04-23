import requests
from django.conf import settings

class BackendClient:
    def __init__(self, token=None):
        self.base_url = getattr(settings, 'BACKEND_API_URL', "http://app:8080")
        self.headers = {'Authorization': f'Bearer {token}'} if token else {}

    def get_balance(self, user_id):
        try:
            response = requests.get(f"{self.base_url}/api/wallets/{user_id}", headers=self.headers)
            # Если кошелька нет, бэкенд вернет 404. Возвращаем это для обработки во views.py
            if response.status_code == 404:
                return {"detail": "Wallet not found"}
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"balance": 0.0, "error": "Сервер недоступен"}

    def predict(self, data):
        try:
            response = requests.post(f"{self.base_url}/api/predict/", json=data, headers=self.headers)
            return response.json(), response.status_code
        except requests.exceptions.RequestException:
            return {"detail": "Ошибка связи с ML-модулем"}, 503

    def get_history(self, user_id):
        # Если в сессии пусто или строка 'None', вернём пустой список сразу
        if not user_id or str(user_id) == 'None':
            print("DEBUG: user_id отсутствует, запрос истории отменен.")
            return []
            
        try:
            url = f"{self.base_url}/api/history/{str(user_id)}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Если бэкенд прислал не список, а словарь {"history": [...]}, извлекаем список
                if isinstance(data, dict) and 'history' in data:
                    data = data['history']
                
                # Сортируем: новые сверху (если есть поле timestamp)
                if isinstance(data, list):
                    try:
                        data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    except Exception:
                        pass
                
                print(f"DEBUG: Успешно получено записей: {len(data)}")
                return data
            
            print(f"DEBUG: Бэкенд вернул статус {response.status_code} для истории")
            return []
            
        except Exception as e:
            print(f"ОШИБКА ИСТОРИИ: {e}")
            return []

    def deposit_balance(self, user_id, amount):
        try:
            payload = {"balance": float(amount)}
            url = f"{self.base_url}/api/wallets/{user_id}/"
            response = requests.patch(url, json=payload, headers=self.headers)
            return response.json(), response.status_code
        except ValueError:
            return {"detail": "Некорректная сумма"}, 400
        except Exception:
            return {"detail": "Ошибка связи"}, 500

    def create_wallet(self, user_id):
        """Создание кошелька (POST /api/wallets/)"""
        try:
            payload = {
                "user_id": str(user_id),
                "balance": 0.0
            }
            response = requests.post(
                f"{self.base_url}/api/wallets/", 
                json=payload, 
                headers=self.headers
            )
            return response.json(), response.status_code
        except Exception:
            return {"detail": "Ошибка создания кошелька"}, 500