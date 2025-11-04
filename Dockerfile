FROM python:3.11-alpine3.20 AS builder


RUN echo "https://mirror.clarkson.edu/alpine/v3.20/main" > /etc/apk/repositories \
    && echo "https://mirror.clarkson.edu/alpine/v3.20/community" >> /etc/apk/repositories \
    && apk update \
    && apk add --no-cache build-base libffi-dev postgresql-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

FROM python:3.11-alpine3.20
WORKDIR /app
RUN adduser -D appuser
USER appuser
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
