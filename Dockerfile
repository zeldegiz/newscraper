FROM python:3.10.9-alpine3.17

WORKDIR ./Project

COPY Project ./

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev && pip install -r requirements.txt

RUN crontab crontab

CMD ["crond", "-f"]