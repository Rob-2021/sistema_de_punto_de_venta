FROM python:3.10.8-alpine3.16

ENV PYTHONUNBUFFERD=1

WORKDIR /app

RUN apk update \
    && pip install --upgrade pip

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY ./ ./

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]