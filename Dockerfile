FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential gcc python3-distutils && \
    apt-get clean


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "application.py", "--server.port=8501", "--server.enableCORS=false"]
