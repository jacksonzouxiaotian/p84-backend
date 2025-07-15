FROM python:3.10-slim-bullseye

# 安装 netcat，用于等待数据库启动
RUN apt-get update && apt-get install -y netcat && apt-get clean

WORKDIR /app
COPY requirements/prod.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000
