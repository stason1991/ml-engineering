from prometheus_client import Counter

PREDICTIONS_TOTAL = Counter(
    "ml_predictions_total", 
    "Total number of ML predictions made",
    ["model_type"]
)

TRANSACTIONS_AMOUNT_TOTAL = Counter(
    "app_transactions_amount_total", 
    "Total amount of all transactions"
)