FROM python:3.8

WORKDIR /app

ENV POSTGRES_URL=ec2-54-220-35-19.eu-west-1.compute.amazonaws.com
ENV POSTGRES_USER=svabnfitwvcqpf
ENV POSTGRES_PASSWORD=73716b4cef909bf1129372b572612b9b8a3e100ace455d7461cfe8b247b97aac
ENV POSTGRES_DB=d22l41cd9cqhlc
ENV SECRET_KEY=ohwhataday
ENV PAGE_NO_REPLY_PASSWORD=none

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY src/ ./src/

CMD ["python3", "src/server.py"]