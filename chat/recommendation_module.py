import boto3
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA, LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import tempfile

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
)

def get_pdf_from_s3(bucket_name, object_key):
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    pdf_content = response['Body'].read()
    return pdf_content

def load_and_embed_pdfs(pdf_content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_content)
        temp_pdf_path = temp_pdf.name

    loader = PyPDFLoader(temp_pdf_path)
    documents = loader.load()

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(documents, embedding_model)

    return vector_store

def generate_recommendations(vector_store):
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

    # 프롬프트를 분리하여 관리
    prompt_intro = "당신은 여행 준비 전문가입니다. 주어진 여행지 정보를 바탕으로 사용자에게 필요한 준비물을 상세하게 추천해주세요."
    prompt_context = "\n\n여행지 정보:\n{context}"
    prompt_request = "\n\n준비물 추천:"

    # 전체 프롬프트 구성
    prompt_template = prompt_intro + prompt_context + prompt_request

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context"]
    )

    # LLMChain 생성
    chain = LLMChain(llm=llm, prompt=prompt)

    # 컨텍스트를 가져오기 위해 retriever 사용
    retriever = vector_store.as_retriever()
    docs = retriever.get_relevant_documents("")

    context = "\n".join([doc.page_content for doc in docs])

    # LLMChain을 통해 응답 생성
    response = chain.run(context=context)

    return response
