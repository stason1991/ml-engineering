FROM python:3.11-slim
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . ./app
ENV PYTHONPATH=/src
CMD ["python", "-m", "api.py"]

