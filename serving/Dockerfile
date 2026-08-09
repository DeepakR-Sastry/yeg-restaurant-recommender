FROM python:3.12-slim

WORKDIR /app

COPY serving/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY data/edmonton_restaurants.csv ./data/
COPY serving/app ./serving/app

CMD ["uvicorn", "serving.app.main:app", "--host", "0.0.0.0", "--port", "8000"]