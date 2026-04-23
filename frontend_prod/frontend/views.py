import requests
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings
from .services import BackendClient

class LoginView(View):
    # Реализуем следующую логику: заходим -> получаем токен -> идем в /api/auth/me за ID -> сохраняем всё в сессию
    template_name = 'auth/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Авторизация (получаем токен)
            response = requests.post(
                f"{settings.BACKEND_API_URL}/api/auth/login", 
                data={"username": username, "password": password}
            )

            if response.status_code == 200:
                token = response.json().get('access_token')
                request.session['access_token'] = token
                
                # Получаем UUID пользователя через /api/auth/me
                user_info = requests.get(
                    f"{settings.BACKEND_API_URL}/api/auth/me",
                    headers={'Authorization': f'Bearer {token}'}
                )
                
                if user_info.status_code == 200:
                    data = user_info.json()
                    u_id = data.get('id')
                    if u_id:
                        request.session['user_id'] = str(u_id)
                    
                    messages.success(request, "Добро пожаловать!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Ошибка получения данных профиля")
            else:
                messages.error(request, "Неверные учетные данные")
                
        except Exception as e:
            print(f"Ошибка: {e}")
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
                messages.success(request, "Регистрация успешна!")
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
        
        client = BackendClient(token=token)
        
        # Получаем баланс
        wallet_data = client.get_balance(user_id)
        
        # Кошелек не найден
        if isinstance(wallet_data, dict) and (wallet_data.get('detail') == "Wallet not found"):
            print(f"DEBUG: Кошелек для {user_id} не найден. Создаю новый...")
            
            # Создаем кошелек
            client.create_wallet(user_id)
            
            # Получаем баланс еще раз
            wallet_data = client.get_balance(user_id)
            
        context['wallet'] = wallet_data
        context['history'] = client.get_history(user_id)
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
                # Ассинхронность не даёт вернуть результат мгновенно, просим подождать
                task_id = result.get('task_id')
                messages.info(request, f"Анализ запущен! ID задачи: {task_id}. Обновите страницу через 10 секунд, чтобы увидеть результат")
                return redirect('dashboard')
            
            messages.error(request, f"Ошибка: {result}")
        except Exception as e:
            messages.error(request, f"Ошибка данных: {str(e)}")
            
        return render(request, self.template_name)

class PredictResultDetailView(View):
    def get(self, request, task_id):
        token = request.session.get('access_token')
        user_id = request.session.get('user_id')
        client = BackendClient(token=token)
        
        # Получаем всю историю
        history = client.get_history(user_id)
        
        # Ищем в списке задачу по task_id
        result = next((item for item in history if item.get('task_id') == task_id), None)
        
        if not result:
            messages.warning(request, "Результат еще готовится или не найден. Обновите страницу позже.")
            return redirect('dashboard')

        # В воркере поле называется 'result', 
        # а в шаблоне используется 'target_class' и другие. 
        # Для совместимости:
        result['target_class'] = result.get('result') 

        return render(request, 'dashboard/predict_result.html', {'result': result})

class DepositView(View):
    def post(self, request):
        token = request.session.get('access_token')
        user_id = request.session.get('user_id')
        amount = request.POST.get('amount')
        
        # Если в сессии нет user_id, перенаправляем на вход снова
        if not user_id:
            messages.error(request, "Ошибка авторизации. Попробуйте войти заново.")
            return redirect('login')

        client = BackendClient(token=token)
        result, status = client.deposit_balance(user_id, amount)
        
        if status == 200:
            messages.success(request, "Баланс успешно обновлен")
        else:
            # Вывод детальной ошибки для отладки
            error_msg = result.get('detail', "Не удалось пополнить баланс")
            messages.error(request, f"Ошибка: {error_msg}")
            
        return redirect('dashboard')

class HistoryView(TemplateView):
    template_name = 'dashboard/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.request.session.get('access_token')
        user_id = self.request.session.get('user_id')
        client = BackendClient(token=token)
        history_data = client.get_history(user_id)
        # ПРОВЕРКА: Печатаем данные в консоль Django
        print(f"DEBUG VIEW: History for {user_id} -> {history_data}")
        
        context['history'] = client.get_history(user_id)
        return context

def logout_view(request):
    request.session.flush()
    messages.info(request, "Вы вышли из системы")
    return redirect('home')