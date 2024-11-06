import boto3
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA, LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import tempfile
import re

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

def parse_recommendations(response):
    lines = response.strip().split('\n')
    recommendations = []
    current_item = None
    for line in lines:
        match = re.match(r'^(\d+)\.\s*(.*)', line)
        if match:
            number = int(match.group(1))
            description = match.group(2).strip()
            if current_item:
                recommendations.append(current_item)
            current_item = {'number': number, 'recommendation': description}
        else:
            if current_item:
                current_item['recommendation'] += ' ' + line.strip()
    if current_item:
        recommendations.append(current_item)
    return recommendations

def generate_recommendations(vector_store):
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

    prompt_intro = """당신은 여행 준비 전문가입니다. 
    주어진 여행지 정보와 문서를 바탕으로 사용자에게 필요한 준비물을 상세하게 번호를 매겨 추천해주세요. 
    여권, 여분의 옷 등과 같은 일반적인 여행 준비물 대신, 사용자의 여행 목적지와 여행 기간에 특화된 준비물을 위주로 추천해주면 더 좋습니다.
    """
    prompt_context = "\n\n여행지 정보:\n{context}"
    prompt_request = "\n\n준비물 추천:"

    prompt_template = prompt_intro + prompt_context + prompt_request

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context"]
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    retriever = vector_store.as_retriever()
    docs = retriever.get_relevant_documents("")

    context = "\n".join([doc.page_content for doc in docs])

    response = chain.run(context=context)

    recommendations = parse_recommendations(response)

    return recommendations
