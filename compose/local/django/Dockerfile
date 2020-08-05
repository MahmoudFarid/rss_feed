FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt

COPY ./compose/production/django/entrypoint /entrypoint
COPY ./compose/local/django/start /start-dev
COPY ./compose/local/django/celery/worker/start /start-celeryworker
COPY ./compose/local/django/celery/beat/start /start-celerybeat
COPY ./compose/local/django/celery/flower/start /start-flower

RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint \
  && sed -i 's/\r$//g' /start-dev && chmod +x /start-dev \
  && sed -i 's/\r$//g' /start-celeryworker && chmod +x /start-celeryworker \
  && sed -i 's/\r$//g' /start-celerybeat && chmod +x /start-celerybeat \
  && sed -i 's/\r$//g' /start-flower && chmod +x /start-flower

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
