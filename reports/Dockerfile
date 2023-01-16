FROM python:3.10
MAINTAINER ALeRCE
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/src/

RUN pip install --no-cache-dir poetry
COPY ./reports /app/src
COPY ./libs /app/libs
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-cache --no-ansi

CMD ["uvicorn", "reports.main:app", "--host", "0.0.0.0", "--port", "8000"]
