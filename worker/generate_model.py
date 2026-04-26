import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler

# 82 признака/характеристики сотрудника
FEATURE_MAPPING = [
    "gender", "age", "edu_level", "edu_type", "exp_total", "exp_profile", "exp_bank", "exp_mng", "exp_premium", "has_car",
    "skill_it_edu", "skill_sql_level", "skill_prog_level", "skill_agile_exp", "know_client_service", "know_law_base",
    "know_bank_struct", "know_accounting", "know_fire_safety", "know_emergency", "know_docs_flow", "know_aml_cft",
    "know_cybersec", "know_it_arch", "know_basel_standards", "know_lean_method", "know_db_logic", "know_reg_reporting",
    "kpi_pc_deposit", "kpi_pc_acc_saving", "kpi_pc_ins_life_save", "kpi_pc_ins_life_invest", "kpi_pc_pif", "kpi_pc_trust_mng",
    "kpi_pc_algo_trade", "kpi_pc_pds", "kpi_pc_loan_cash", "kpi_pc_mortgage", "kpi_pc_loan_auto", "kpi_pc_loan_car_pledge",
    "kpi_pc_loan_re_pledge", "kpi_pc_loan_edu", "kpi_pc_card_credit", "kpi_pc_card_debit", "kpi_pc_ins_loan", "kpi_pc_ins_box",
    "kpi_pc_ins_fraud", "kpi_sum_deposit", "kpi_sum_acc_saving", "kpi_sum_ins_life_save", "kpi_sum_ins_life_invest",
    "kpi_sum_pif", "kpi_sum_trust_mng", "kpi_sum_algo_trade", "kpi_sum_pds", "kpi_sum_loan_cash", "kpi_sum_mortgage",
    "kpi_sum_loan_auto", "kpi_sum_loan_car_pledge", "kpi_sum_loan_re_pledge", "kpi_sum_loan_edu", "kpi_sum_ins_loan",
    "kpi_sum_ins_box", "kpi_sum_ins_fraud", "qual_penalty", "qual_complaints", "qual_csi", "qual_speed", "qual_op_errors",
    "qual_returns", "qual_fraud_cases", "qual_target_clients", "qual_marketing_deals", "qual_data_quality", "qual_edu_courses",
    "qual_portal_news", "soft_conflicts", "soft_negotiation", "soft_mentoring", "soft_project_work", "soft_mng_feedback",
    "it_automation_count"
]

def create_vec(settings):
    vec = np.zeros(len(FEATURE_MAPPING))
    for feat, weight in settings.items():
        if feat in FEATURE_MAPPING:
            vec[FEATURE_MAPPING.index(feat)] = weight
    return vec.reshape(1, -1)

# 24 центройда/профиля для определения соответствия
profiles = {
    "1. Sales Manager": {"edu_level": 2, "exp_bank": 6, "kpi_pc_loan_cash": 15, "kpi_sum_loan_cash": 3000000},
    "2. Senior Sales Manager": {"edu_level": 2, "exp_bank": 24, "exp_profile": 24, "qual_target_clients": 125, "kpi_pc_loan_cash": 60, "kpi_sum_loan_cash": 15000000},
    "3. Premium Client Manager": {"edu_level": 3, "exp_bank": 36, "exp_premium": 24, "kpi_pc_ins_life_invest": 25, "kpi_sum_ins_life_invest": 60000000},
    "4. Field Sales Manager": {"edu_level": 1, "has_car": 1, "exp_total": 12, "kpi_pc_card_debit": 100, "qual_marketing_deals": 40},
    "5. Corporate Relations Manager": {"edu_level": 2, "edu_type": 2, "exp_bank": 12, "know_law_base": 1, "soft_negotiation": 4},
    "6. Senior Corporate Manager": {"edu_level": 3, "edu_type": 2, "exp_bank": 48, "exp_profile": 36, "kpi_sum_loan_re_pledge": 100000000},
    "7. Hunter": {"edu_level": 2, "exp_total": 24, "qual_marketing_deals": 300, "soft_negotiation": 5},
    "8. Auto Loan Manager": {"edu_level": 2, "exp_bank": 12, "kpi_pc_loan_auto": 40, "kpi_sum_loan_auto": 50000000},
    "9. Mortgage Manager": {"edu_level": 2, "edu_type": 2, "exp_bank": 24, "kpi_pc_mortgage": 30, "kpi_sum_mortgage": 200000000},
    "10. DSA": {"edu_level": 2, "soft_project_work": 5, "qual_marketing_deals": 150},
    "11. Operations Specialist": {"edu_level": 2, "edu_type": 2, "know_accounting": 1, "qual_op_errors": 0, "qual_speed": 5},
    "12. Deputy Office Head": {"edu_level": 2, "exp_bank": 36, "exp_mng": 12, "soft_mentoring": 4},
    "13. Office Head": {"edu_level": 3, "exp_bank": 60, "exp_mng": 36, "soft_mng_feedback": 5, "qual_target_clients": 110},
    "14. Support (Helpdesk)": {"edu_level": 2, "know_bank_struct": 1, "qual_csi": 5, "know_client_service": 1},
    "15. Data Scientist": {"edu_level": 3, "edu_type": 3, "skill_sql_level": 5, "skill_prog_level": 5, "know_db_logic": 1},
    "16. Data Engineer": {"edu_level": 2, "edu_type": 3, "skill_sql_level": 5, "know_it_arch": 1, "it_automation_count": 10},
    "17. Software Developer": {"edu_level": 2, "edu_type": 3, "skill_prog_level": 5, "skill_agile_exp": 1, "it_automation_count": 15},
    "18. Analyst": {"edu_level": 2, "edu_type": 2, "skill_sql_level": 4, "qual_data_quality": 5},
    "19. Investment Direction Head": {"edu_level": 3, "exp_bank": 60, "kpi_sum_trust_mng": 200000000, "soft_mentoring": 5},
    "20. Risk Manager": {"edu_level": 3, "edu_type": 2, "know_basel_standards": 1, "know_law_base": 1, "qual_op_errors": 0},
    "21. Security Officer": {"edu_level": 2, "know_cybersec": 1, "know_aml_cft": 1, "qual_fraud_cases": 10},
    "22. Delivery Courier": {"edu_level": 1, "has_car": 1, "qual_speed": 5, "qual_returns": 0},
    "23. Payroll Project Manager": {"edu_level": 2, "soft_negotiation": 5, "kpi_pc_card_debit": 150, "qual_target_clients": 120},
    "24. Methodologist": {"edu_level": 3, "edu_type": 1, "know_docs_flow": 1, "know_law_base": 1, "qual_data_quality": 5}
}

X_dummy = np.random.rand(3000, len(FEATURE_MAPPING))
sum_indices = [i for i, f in enumerate(FEATURE_MAPPING) if "sum" in f]
X_dummy[:, sum_indices] *= 200000000 

scaler = StandardScaler().fit(X_dummy)
centroids = {role: scaler.transform(create_vec(weights)) for role, weights in profiles.items()}

joblib.dump({"feature_names": FEATURE_MAPPING, "scaler": scaler, "centroids": centroids}, "model_assets.pkl")
print("Assets generated successfully with English keys.")
