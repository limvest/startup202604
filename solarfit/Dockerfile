FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libgdal-dev libgeos-dev libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드
COPY api/ ./api/

# HF Space: limit tiles for CPU inference speed
ENV MAX_BASE_TILES=4
ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
