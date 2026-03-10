FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN pip install --upgrade pip && pip install pipenv

COPY Pipfile* /tmp/

RUN cd /tmp \
    && pipenv lock \
    && pipenv requirements > requirements.txt \
    && pip install -r requirements.txt

COPY . .

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
