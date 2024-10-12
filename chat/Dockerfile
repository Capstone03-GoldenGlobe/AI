# Stage 1: Build Stage
FROM python:3.10-slim AS builder

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 파일을 컨테이너로 복사 및 Python 패키지 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Image Stage
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# Build Stage에서 설치된 패키지 복사
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 소스 코드 복사
COPY . .

# Flask 앱 실행
CMD ["python", "app.py"]