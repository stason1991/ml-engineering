FROM python:3.10-slim

WORKDIR /worker_app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .
COPY model_assets.pkl .

ENV PYTHONPATH="${PYTHONPATH}:/shared"

CMD ["python", "worker.py"]