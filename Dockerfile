FROM python:3.12-slim

RUN apt-get update

WORKDIR /bot

COPY requirements.txt .
COPY bot.py .
COPY .env .
COPY adds.py .


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN ls -la

CMD ["python", "bot.py"]