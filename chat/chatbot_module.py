import boto3
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import tempfile

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
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

def generate_answer(vector_store, question):
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

    prompt_template = """당신은 친절한 여행 상담원입니다. 주어진 문서를 바탕으로 사용자의 질문에 대해 정확하고 상세한 답변을 제공해주세요.

    문서 내용: {context}

    사용자 질문: {question}

    답변:"""

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        return_source_documents=False
    )

    response = qa.run(question)

    return response

