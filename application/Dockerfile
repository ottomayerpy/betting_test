FROM python:latest

WORKDIR /application

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONNUNBUFFERED=1

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "__main__.py"]
