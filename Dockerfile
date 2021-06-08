FROM python:3.8

WORKDIR /app

ENV POSTGRES_URL=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=euros
ENV SECRET_KEY=secret
ENV PAGE_NO_REPLY_PASSWORD=none

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY src/ ./src/

CMD ["python3", "src/server.py"]