# GoldenGlobe - AI

## 🌏 프로젝트 개요  
이 프로젝트는 시니어와 그 가족들이 효율적으로 여행을 준비할 수 있도록 돕는 LLM과 RAG 기반의 맞춤형 여행 챗봇 및 체크리스트 서비스입니다. 
시니어가 여행지 정보를 쉽게 파악하고 준비할 수 있도록 돕는 챗봇 기능과, 여행지에 맞춘 공유 체크리스트 기능을 통해 여행 준비의 효율성을 높입니다. 

### 주요 기능  
1. **챗봇 기능**  
   - 여행지에 대한 질문 응답 제공  
2. **준비물 추천**  
   - 여행 목적지에 최적화된 준비물 추천  



## 🛠️ 사용 기술  
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1F2437?style=flat-square) ![LangChain](https://img.shields.io/badge/LangChain-43A047?style=flat-square) ![FAISS](https://img.shields.io/badge/FAISS-0073E6?style=flat-square) ![HuggingFace](https://img.shields.io/badge/HuggingFace-FFCA28?style=flat-square&logo=huggingface&logoColor=white) ![OpenAI](https://img.shields.io/badge/OpenAI-GPT4-0072C6?style=flat-square) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-S3-232F3E?style=flat-square&logo=amazonaws&logoColor=white)  



## 💡 시작하기  

### 사전 준비  
- **환경 변수 설정**: `.env` 파일을 생성하고 설정  
```plaintext
DB_USERNAME=<DB 사용자 이름>
DB_PASSWORD=<DB 비밀번호>
DB_HOST=<DB 호스트>
DB_NAME=<DB 이름>

AWS_ACCESS_KEY_ID=<발급받은 AWS S3 Access Key>
AWS_SECRET_ACCESS_KEY=<발급받은 AWS S3 Secret Key>
```

### How to Build
1. **Repository 클론**
```
git clone <repo_url>
cd <repo_directory>
```
2. **가상 환경 설정**
```python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
3. **데이터베이스 초기화**
```python
from app import db  
db.create_all()
```
<br>

### How to Install
1. **프로젝트 코드 및 종속성 설치**<br>
프로젝트에서 사용된 Python 라이브러리를 설치하려면 먼저 가상 환경을 설정한 후 아래 명령어를 실행합니다.<br>

(1) Repository 클론
```bash
git clone <repo_url>
cd <repo_directory>
```
(2) Python 가상 환경 설정<br>
가상 환경을 생성하고 활성화합니다.
```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
source venv/bin/activate  
# Windows: venv\Scripts\activate
```
(3) 라이브러리 설치<br>
`requirements.txt` 파일에 포함된 모든 종속성을 설치합니다.
```bash
pip install -r requirements.txt
```
- `requirements.txt`에는 다음과 같은 주요 라이브러리가 포함되어 있습니다.
```plaintext
Flask
Flask-CORS
Flask-SQLAlchemy
PyMySQL
boto3
python-dotenv
langchain
faiss-cpu
openai
sentence-transformers
```
(4) 설치된 라이브러리 확인<br>
아래 명령어를 사용해 설치된 라이브러리를 확인합니다.
```
pip list
```
<br>

2. **Docker 빌드 및 실행**
```
docker build -t golden-globe-ai .
docker run -p 5000:5000 golden-globe-ai
```
<br>

### How to Test
서버 실행 후 Postman 또는 브라우저를 통해 API를 테스트합니다.
### 1. 챗봇 질문 API
- URL: `POST /chatbot/question/<dest_id>`
- Body
```json
{
  "question": "여행지 정보 알려줘",
  "chat_id": 12345
}
```
- 응답
```json
{
  "answer": "해당 여행지에 대한 설명",
  "chat_id": 12345
}
```
### 2. 준비물 추천 체크리스트 API
- URL : `GET /place/recommendation/<dest_id>`
- 응답
```json
{
  "recommendations": [
    {"number": 1, "recommendation": "특화된 여행 준비물1"},
    {"number": 2, "recommendation": "특화된 여행 준비물2"}
  ]
}
```

## 🌱 담당 기능
| 🍀 이름 | 🍀 담당 기능 |
|:---:|:---|
| [원재영](https://github.com/jaeyeong13) | - **Flask 기반 REST API 개발**<br>- **챗봇 기능 구현**: LLM 기반 질문 응답<br>- **여행 준비물 추천 기능 구현**: RAG 기반 최적화된 준비물 추천<br>- **AWS S3 연동**: PDF 파일 저장 및 처리<br>- **LangChain 및 FAISS 활용**: 문서 임베딩 및 검색 기능 구현<br>- **AI 전체 아키텍처 설계 및 개발** |
| [김근주](https://github.com/tdddt) | - **초기 AI 모델 선정 및 세팅**<br>- **AI 아키텍처 설계** |

## 🗂️ 폴더 구조
```
📂 GoldenGlobe AI
├── app.py                       ▶️ 메인 Flask 애플리케이션
├── chatbot_module.py            ▶️ 챗봇 질문 처리 모듈
├── recommendation_module.py     ▶️ 여행 준비물 추천 모듈
├── requirements.txt             ▶️ 종속 패키지 목록
├── Dockerfile                   ▶️ Docker 설정 파일
├── .env                         ▶️ 환경 변수 설정 파일
├── vector_store_2.faiss         ▶️ FAISS 벡터 스토어 저장소
└── .dockerignore                ▶️ Docker 빌드 시 제외 파일
```

## 📚 오픈소스
1. **Flask** : https://flask.palletsprojects.com/en/stable/
2. **SQLAlchemy** : https://www.sqlalchemy.org/
3. **LangChain** : https://python.langchain.com/docs/introduction/
4. **HuggingFace Embeddings** : https://huggingface.co/docs
5. **FAISS** : https://faiss.ai/index.html
6. **OpenAI GPT-4** : https://openai.com/
7. **AWS S3** : https://aws.amazon.com/ko/s3/
8. **Docker** : https://docs.docker.com/desktop/?_gl=1*1tk0ehy*_gcl_au*OTc3OTU3NjcxLjE3MzQzNzQxNDY.*_ga*NzU4ODg2MzQzLjE3MzQzNzQxNDY.*_ga_XJWPQMJYHQ*MTczNDM3NDE0NS4xLjEuMTczNDM3NDE0Ni41OS4wLjA.
