FROM python:3.10-slim-bullseye
WORKDIR /app
COPY requirements/prod.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD gunicorn -b 0.0.0.0:$PORT autoapp:app
