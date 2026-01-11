FROM python:3.12-slim

WORKDIR /

COPY requirements.txt .
COPY main.py .
COPY adds.py .
COPY callbacks.py .
COPY classes.py .
COPY consts.py .

COPY .env .


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN ls -la

CMD ["python", "main.py"]