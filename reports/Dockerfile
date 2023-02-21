FROM python:3.10
MAINTAINER ALeRCE
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/src/

RUN pip install --no-cache-dir poetry
COPY ./libs /app/libs
COPY ./reports/poetry.lock ./reports/pyproject.toml /app/src/
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-cache --without=dev --no-root

COPY ./reports /app/src
RUN poetry install --no-interaction --no-cache --only-root

EXPOSE 8000
CMD ["uvicorn", "reports.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "logging.yml"]
