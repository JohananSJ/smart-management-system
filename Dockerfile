FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p flask_session uploads

EXPOSE 5001

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]