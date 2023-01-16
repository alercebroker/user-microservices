FROM python:3.10
MAINTAINER ALeRCE
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/src/

RUN pip install --no-cache-dir poetry
COPY ./libs /app/libs
COPY ./reports/poetry.lock ./reports/pyproject.toml /app/src/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-cache --no-ansi

COPY ./reports /app/src

CMD ["uvicorn", "reports.main:app", "--host", "0.0.0.0", "--port", "8000"]
