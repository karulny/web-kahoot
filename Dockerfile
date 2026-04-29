FROM python:3.14-slim AS python-deps

WORKDIR /install

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install/pkg -r requirements.txt



FROM python:3.14-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy installed packages from build stage
COPY --from=python-deps /install/pkg /usr/local

# Copy application source
COPY backend/ ./backend/
COPY frontend/ ./frontend/

EXPOSE 5000

CMD ["python", "-m", "gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "backend.main:app"]