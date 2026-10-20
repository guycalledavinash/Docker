FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app

COPY --chown=app:app devops/ /app/devops/

USER app

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "devops.wsgi:application"]
