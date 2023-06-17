FROM python:3.9.15
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /erganiser-logbook
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

