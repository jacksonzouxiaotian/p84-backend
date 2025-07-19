FROM python:3.10-slim-bullseye

# 安装 netcat，用于检测数据库端口开放状态
RUN apt-get update \
    && apt-get install -y netcat \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制并安装 Python 依赖
COPY requirements/prod.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码和入口脚本
COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 暴露容器内的 5000 端口
EXPOSE 5000

# 设置容器启动后执行的入口脚本
ENTRYPOINT ["/entrypoint.sh"]
