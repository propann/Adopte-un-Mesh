FROM python:3.12-slim

WORKDIR /app

COPY services/radio-bridge/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/radio-bridge /app

CMD ["python", "bridge.py"]
