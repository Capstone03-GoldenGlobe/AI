# 베이스 이미지 선택 (Python 3.9 버전 사용)
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 필요한 파일들을 컨테이너로 복사
COPY requirements.txt ./

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# 컨테이너에서 Flask 앱 실행
CMD ["python", "app.py"]
