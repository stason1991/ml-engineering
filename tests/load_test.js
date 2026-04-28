import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = 'http://localhost:8080/api';

export const options = {
    stages: [
        { duration: '30s', target: 20 },
        { duration: '1m', target: 50 },
        { duration: '20s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<3000'],
        http_req_failed: ['rate<0.01'],
    },
};

export function setup() {
    const uniqueId = Math.random().toString(36).substring(7);
    const login = `load_tester_${uniqueId}`;
    const password = "password123";


    const regRes = http.post(`${BASE_URL}/auth/register`, JSON.stringify({ 
        login: login, 
        password: password 
    }), { headers: { 'Content-Type': 'application/json' } });
    
    const userId = regRes.json().user_id;


    const loginRes = http.post(`${BASE_URL}/auth/login`, {
        username: login,
        password: password
    });
    const token = loginRes.json().access_token;

    const authHeaders = { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };


    http.post(`${BASE_URL}/wallets/`, JSON.stringify({
        user_id: userId,
        balance: 0.0
    }), { headers: authHeaders });


    const txRes = http.post(`${BASE_URL}/transactions/`, JSON.stringify({
        wallet_id: userId,
        amount: 500000.0, // Даем много денег
        tx_type: "credit"
    }), { headers: authHeaders });


    console.log(`Setup complete for user ${userId}. TX Status: ${txRes.status}`);

    return { authToken: token };
}

export default function (data) {
    const params = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${data.authToken}`,
        },
    };

    const payload = JSON.stringify({
        features: {
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
            "soft_conflicts": 4,
            "soft_negotiation": 5,
            "soft_mentoring": 3,
            "soft_project_work": 4,
            "soft_mng_feedback": 4.5,
            "it_automation_count": 2
        },
        "model_id": "Career Path Pro"
    });

    const res = http.post(`${BASE_URL}/predict/`, payload, params);

    check(res, {
        'status is 200': (r) => r.status === 200,
        'is queued': (r) => r.json().status === 'queued',
    });

    sleep(1);
}