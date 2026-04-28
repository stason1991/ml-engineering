import pytest
import requests
import uuid

BASE_URL = "http://localhost:8080/api"

@pytest.fixture(scope="session")
def valid_employee_data():
    # Полный набор характеристик из EmployeeFeatures для проверки валидации
    return {
        # Общие характеристики
        "gender": 1,
        "age": 30,
        "edu_level": 2,
        "edu_type": 2,
        "exp_total": 120,
        "exp_profile": 60,
        "exp_bank": 36,
        "exp_mng": 12,
        "exp_premium": 6,
        "has_car": 1,
        "skill_it_edu": 0,
        "skill_sql_level": 3,
        "skill_prog_level": 1,
        "skill_agile_exp": 1,

        # Знания нормативной документации (float 0.0 - 1.0)
        "know_client_service": 0.9,
        "know_law_base": 0.8,
        "know_bank_struct": 1.0,
        "know_accounting": 0.5,
        "know_fire_safety": 1.0,
        "know_emergency": 1.0,
        "know_docs_flow": 0.9,
        "know_aml_cft": 1.0,
        "know_cybersec": 0.8,
        "know_it_arch": 0.4,
        "know_basel_standards": 0.3,
        "know_lean_method": 0.7,
        "know_db_logic": 0.6,
        "know_reg_reporting": 0.8,

        # Продажи в штуках
        "kpi_pc_deposit": 50,
        "kpi_pc_acc_saving": 30,
        "kpi_pc_ins_life_save": 10,
        "kpi_pc_ins_life_invest": 5,
        "kpi_pc_pif": 15,
        "kpi_pc_trust_mng": 2,
        "kpi_pc_algo_trade": 1,
        "kpi_pc_pds": 10,
        "kpi_pc_loan_cash": 40,
        "kpi_pc_mortgage": 5,
        "kpi_pc_loan_auto": 8,
        "kpi_pc_loan_car_pledge": 3,
        "kpi_pc_loan_re_pledge": 2,
        "kpi_pc_loan_edu": 4,
        "kpi_pc_card_credit": 100,
        "kpi_pc_card_debit": 200,
        "kpi_pc_ins_loan": 80,
        "kpi_pc_ins_box": 30,
        "kpi_pc_ins_fraud": 45,

        # Продажи в суммах
        "kpi_sum_deposit": 5000000.0,
        "kpi_sum_acc_saving": 2000000.0,
        "kpi_sum_ins_life_save": 1000000.0,
        "kpi_sum_ins_life_invest": 3000000.0,
        "kpi_sum_pif": 500000.0,
        "kpi_sum_trust_mng": 1500000.0,
        "kpi_sum_algo_trade": 100000.0,
        "kpi_sum_pds": 200000.0,
        "kpi_sum_loan_cash": 8000000.0,
        "kpi_sum_mortgage": 25000000.0,
        "kpi_sum_loan_auto": 4000000.0,
        "kpi_sum_loan_car_pledge": 1500000.0,
        "kpi_sum_loan_re_pledge": 5000000.0,
        "kpi_sum_loan_edu": 800000.0,
        "kpi_sum_ins_loan": 400000.0,
        "kpi_sum_ins_box": 150000.0,
        "kpi_sum_ins_fraud": 90000.0,

        # Качественные показатели
        "qual_penalty": 0,
        "qual_complaints": 1,
        "qual_csi": 4.8,
        "qual_speed": 95.5,
        "qual_op_errors": 2,
        "qual_returns": 0,
        "qual_fraud_cases": 0,
        "qual_target_clients": 150,
        "qual_marketing_deals": 45,
        "qual_data_quality": 0.98,
        "qual_edu_courses": 1.0,
        "qual_portal_news": 0.7,

        # Гибкие навыки (0-5)
        "soft_conflicts": 4,
        "soft_negotiation": 5,
        "soft_mentoring": 3,
        "soft_project_work": 4,
        "soft_mng_feedback": 4.5,
        "it_automation_count": 2
    }

@pytest.fixture(scope="session")
def global_user():
    # Регистрируем юзера, авторизуемся и создаём кошелёк
    uid = uuid.uuid4().hex[:6]
    user_payload = {"login": f"test_user_{uid}", "password": "password123"}
    
    # Регистрация
    reg_res = requests.post(f"{BASE_URL}/auth/register", json=user_payload)
    user_id = reg_res.json()["user_id"]
    
    # Авторизация
    login_res = requests.post(f"{BASE_URL}/auth/login", data={
        "username": user_payload["login"], 
        "password": user_payload["password"]
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создание кошелька
    requests.post(f"{BASE_URL}/wallets/", json={"user_id": user_id, "balance": 0.0}, headers=headers)
    
    return {
        "id": user_id,
        "token": token,
        "headers": headers
    }

@pytest.fixture
def poor_user():
    # Фикстура для создания юзера с нулевым балансом перед каждым тестом
    uid = uuid.uuid4().hex[:6]
    login = f"poor_user_{uid}"
    password = "password123"

    # Регистрация
    reg_payload = {"login": login, "password": password}
    reg_res = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    user_id = reg_res.json()["user_id"]

    # Авторизация
    login_res = requests.post(f"{BASE_URL}/auth/login", data={"username": login, "password": password})
    token = login_res.json()["access_token"]

    return {
        "id": user_id,
        "headers": {"Authorization": f"Bearer {token}"}
    }