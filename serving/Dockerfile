FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser

COPY serving/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

USER appuser

COPY data/edmonton_restaurants.csv ./data/
COPY serving/app ./serving/app

CMD ["uvicorn", "serving.app.main:app", "--host", "0.0.0.0", "--port", "8000"]