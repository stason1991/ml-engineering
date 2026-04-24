from pydantic import BaseModel, Field
from typing import Optional

class EmployeeFeatures(BaseModel):
    # Общие характеристики
    gender: int = Field(..., description="0-жен, 1-муж")
    age: int = Field(..., ge=18, le=75)
    edu_level: int = Field(..., ge=1, le=3)
    edu_type: int = Field(..., ge=1, le=3)
    exp_total: int = Field(..., ge=0)
    exp_profile: int = Field(..., ge=0)
    exp_bank: int = Field(..., ge=0)
    exp_mng: int = Field(..., ge=0)
    exp_premium: int = Field(..., ge=0)
    has_car: int = Field(..., ge=0, le=1)
    skill_it_edu: int = Field(..., ge=0, le=1)
    skill_sql_level: int = Field(..., ge=0, le=5)
    skill_prog_level: int = Field(..., ge=0, le=5)
    skill_agile_exp: int = Field(..., ge=0, le=1)

    # Знания нормативной документации
    know_client_service: float = Field(0.0, ge=0, le=1)
    know_law_base: float = Field(0.0, ge=0, le=1)
    know_bank_struct: float = Field(0.0, ge=0, le=1)
    know_accounting: float = Field(0.0, ge=0, le=1)
    know_fire_safety: float = Field(0.0, ge=0, le=1)
    know_emergency: float = Field(0.0, ge=0, le=1)
    know_docs_flow: float = Field(0.0, ge=0, le=1)
    know_aml_cft: float = Field(0.0, ge=0, le=1)
    know_cybersec: float = Field(0.0, ge=0, le=1)
    know_it_arch: float = Field(0.0, ge=0, le=1)
    know_basel_standards: float = Field(0.0, ge=0, le=1)
    know_lean_method: float = Field(0.0, ge=0, le=1)
    know_db_logic: float = Field(0.0, ge=0, le=1)
    know_reg_reporting: float = Field(0.0, ge=0, le=1)

    # KPI (продажи в штуках)
    kpi_pc_deposit: int = 0
    kpi_pc_acc_saving: int = 0
    kpi_pc_ins_life_save: int = 0
    kpi_pc_ins_life_invest: int = 0
    kpi_pc_pif: int = 0
    kpi_pc_trust_mng: int = 0
    kpi_pc_algo_trade: int = 0
    kpi_pc_pds: int = 0
    kpi_pc_loan_cash: int = 0
    kpi_pc_mortgage: int = 0
    kpi_pc_loan_auto: int = 0
    kpi_pc_loan_car_pledge: int = 0
    kpi_pc_loan_re_pledge: int = 0
    kpi_pc_loan_edu: int = 0
    kpi_pc_card_credit: int = 0
    kpi_pc_card_debit: int = 0
    kpi_pc_ins_loan: int = 0
    kpi_pc_ins_box: int = 0
    kpi_pc_ins_fraud: int = 0

    # KPI (продажи в суммах)
    kpi_sum_deposit: float = 0.0
    kpi_sum_acc_saving: float = 0.0
    kpi_sum_ins_life_save: float = 0.0
    kpi_sum_ins_life_invest: float = 0.0
    kpi_sum_pif: float = 0.0
    kpi_sum_trust_mng: float = 0.0
    kpi_sum_algo_trade: float = 0.0
    kpi_sum_pds: float = 0.0
    kpi_sum_loan_cash: float = 0.0
    kpi_sum_mortgage: float = 0.0
    kpi_sum_loan_auto: float = 0.0
    kpi_sum_loan_car_pledge: float = 0.0
    kpi_sum_loan_re_pledge: float = 0.0
    kpi_sum_loan_edu: float = 0.0
    kpi_sum_ins_loan: float = 0.0
    kpi_sum_ins_box: float = 0.0
    kpi_sum_ins_fraud: float = 0.0

    # Качественные показатели
    qual_penalty: int = Field(0, ge=0, le=1)
    qual_complaints: int = Field(0, ge=0)
    qual_csi: float = Field(0.0, ge=0, le=5)
    qual_speed: float = Field(0.0, ge=0)
    qual_op_errors: int = Field(0, ge=0)
    qual_returns: int = Field(0, ge=0)
    qual_fraud_cases: int = Field(0, ge=0)
    qual_target_clients: int = Field(0, ge=0)
    qual_marketing_deals: int = Field(0, ge=0)
    qual_data_quality: float = Field(0.0, ge=0, le=1)
    qual_edu_courses: float = Field(0.0, ge=0, le=1)
    qual_portal_news: float = Field(0.0, ge=0, le=1)

    # Гибкие навыки
    soft_conflicts: int = Field(3, ge=0, le=5)
    soft_negotiation: int = Field(3, ge=0, le=5)
    soft_mentoring: int = Field(3, ge=0, le=5)
    soft_project_work: int = Field(3, ge=0, le=5)
    soft_mng_feedback: float = Field(3.0, ge=0, le=5)
    it_automation_count: int = Field(0, ge=0)

class PredictionRequest(BaseModel):
    model_id: Optional[str] = "Career Path Pro"
    features: EmployeeFeatures

class PredictionResponse(BaseModel):
    task_id: str
    status: str
    message: str