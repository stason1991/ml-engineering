import requests
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings
from .services import BackendClient

class LoginView(View):
    template_name = 'auth/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            response = requests.post(
                f"{settings.BACKEND_API_URL}/api/auth/login", 
                data={"username": username, "password": password}
            )

            if response.status_code == 200:
                token = response.json().get('access_token')
                request.session['access_token'] = token
                
                user_info = requests.get(
                    f"{settings.BACKEND_API_URL}/api/auth/me",
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                if user_info.status_code == 200:
                    data = user_info.json()
                    u_id = data.get('id')
                    if u_id:
                        request.session['user_id'] = str(u_id)
                    
                    messages.success(request, "Добро пожаловать в систему!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Ошибка получения данных профиля")
            else:
                messages.error(request, "Неверные учетные данные")
                
        except Exception as e:
            messages.error(request, "Бэкенд-сервис недоступен")
            
        return render(request, self.template_name)

class RegisterView(View):
    template_name = 'auth/register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        payload = {
            "login": request.POST.get('username'),
            "password": request.POST.get('password'),
        }
        try:
            response = requests.post(f"{settings.BACKEND_API_URL}/api/auth/register", json=payload)
            if response.status_code == 201:
                messages.success(request, "Регистрация завершена успешно!")
                return redirect('login')
            
            error_data = response.json()
            messages.error(request, f"Ошибка: {error_data.get('detail', 'Запрос отклонен')}")
        except Exception:
            messages.error(request, "Ошибка связи с сервером")
            
        return render(request, self.template_name)


class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.request.session.get('access_token')
        user_id = self.request.session.get('user_id')
        
        if not user_id:
            return context

        client = BackendClient(token=token)
        
        # Получаем актуальный баланс
        wallet_data = client.get_balance(user_id)
        
        # Автосоздание кошелька при первом входе, если он не найден
        if isinstance(wallet_data, dict) and (wallet_data.get('detail') == "Wallet not found"):
            client.create_wallet(user_id)
            wallet_data = client.get_balance(user_id)
            
        context['wallet'] = wallet_data
        context['history'] = client.get_history(user_id)
        context['transactions'] = client.get_transaction_history(user_id)
        return context


class PredictView(View):
    template_name = 'dashboard/predict.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        token = request.session.get('access_token')
        client = BackendClient(token=token)
        
        ml_data_raw = request.POST.get('ml_data')
        
        try:
            features = json.loads(ml_data_raw)
            payload = {"model_id": "Career Path Pro", "features": features}
            
            result, status = client.predict(payload)

            if status == 200:
                messages.info(request, "Прогноз запущен! Результат будет готов через 10 секунд. Ждите!")
                return redirect('dashboard')
            
            error_msg = result.get('detail', result)
            messages.error(request, f"Ошибка формирования прогноза: {error_msg}")
        except Exception as e:
            messages.error(request, f"Ошибка входных данных: {str(e)}")
            
        return render(request, self.template_name)

class PredictResultDetailView(View):
    def get(self, request, task_id):
        token = request.session.get('access_token')
        user_id = request.session.get('user_id')
        client = BackendClient(token=token)
        
        history = client.get_history(user_id)
        
        # Поиск записи по task_id или внутреннему ID
        result = next(
            (item for item in history if str(item.get('task_id')) == str(task_id) or str(item.get('id')) == str(task_id)), 
            None
        )
        
        if not result:
            messages.warning(request, "Результат еще формируется или запись не найдена.")
            return redirect('dashboard')

        # Приведение полей к формату шаблона
        if 'result' in result and not result.get('target_class'):
            result['target_class'] = result.get('result')
            
        if result.get('confidence') is None:
            result['confidence'] = 0.0

        return render(request, 'dashboard/predict_result.html', {'result': result})

class DepositView(View):
    def post(self, request):
        token = request.session.get('access_token')
        user_id = request.session.get('user_id')
        amount = request.POST.get('amount')
        
        if not user_id:
            messages.error(request, "Ошибка авторизации. Войдите заново.")
            return redirect('login')

        client = BackendClient(token=token)
        result, status = client.deposit_balance(user_id, amount)
        
        if status in [200, 201]:
            messages.success(request, f"Баланс успешно пополнен на {amount} credits")
        else:
            error_msg = result.get('detail', "Не удалось провести транзакцию")
            messages.error(request, f"Ошибка: {error_msg}")
            
        return redirect('dashboard')

class HistoryView(TemplateView):
    template_name = 'dashboard/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.request.session.get('access_token')
        user_id = self.request.session.get('user_id')
        
        if not user_id:
            return context
            
        client = BackendClient(token=token)
        context['history'] = client.get_history(user_id)
        context['transactions'] = client.get_transaction_history(user_id)
        return context

def logout_view(request):
    request.session.flush()
    messages.info(request, "Сессия завершена. Вы вышли из системы")
    return redirect('home')