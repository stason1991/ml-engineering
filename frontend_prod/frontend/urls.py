from django.urls import path
from django.views.generic import TemplateView
from django.shortcuts import redirect
from .views import (
    LoginView, 
    RegisterView, 
    DashboardView, 
    PredictView, 
    DepositView,
    HistoryView,
    PredictResultDetailView,
    logout_view
)

urlpatterns = [
    # Главная страница (Лендинг)
    path('', TemplateView.as_view(template_name='landing.html'), name='home'),
    
    # Авторизация и Регистрация
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    # Выход
    path('auth/logout/', logout_view, name='logout'),

    # Личный кабинет (Баланс и История)
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # Пополнение баланса
    path('deposit/', DepositView.as_view(), name='deposit'),

    # ML-анализ
    path('predict/', PredictView.as_view(), name='predict'),

    # Результат анализа (2. УБРАЛИ views. перед классом)
    path('predict/result/<str:task_id>/', PredictResultDetailView.as_view(), name='predict_result'),
    
    # Страница смены пароля
    path('profile/password/', TemplateView.as_view(template_name='auth/password.html'), name='change_password'),
    path('history/', HistoryView.as_view(), name='history'),
]