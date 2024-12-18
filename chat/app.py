from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import chatbot_module
import recommendation_module
import os
from dotenv import load_dotenv
import logging
from flask_cors import CORS, cross_origin

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 환경 변수 설정
username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')
host = os.environ.get('DB_HOST')
db_name = os.environ.get('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class PdfList(db.Model):
    __tablename__ = 'pdf_list'
    pdf_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    dest_id = db.Column(db.Integer, nullable=False)
    pdf_name = db.Column(db.String(255), nullable=False)
    pdf_path = db.Column(db.String(255), nullable=False)

class ChatBot(db.Model):
    __tablename__ = 'chat_bot'
    chat_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    dest_id = db.Column(db.Integer, nullable=False)

class ChatBotLog(db.Model):
    __tablename__ = 'chat_bot_log'

    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.BigInteger, db.ForeignKey('chat_bot.chat_id'), nullable=False)
    chat_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    qna = db.Column(db.String(10), nullable=False)
    content = db.Column(db.String(300), nullable=False)

    chat_bot = db.relationship('ChatBot', backref=db.backref('chat_logs', lazy=True))

def get_pdf_path_by_dest_id(dest_id):
    pdf_file = PdfList.query.filter_by(dest_id=dest_id).first()
    if not pdf_file:
        return None
    return pdf_file.pdf_path

@app.route('/chatbot/question/<int:dest_id>', methods=['POST', 'OPTIONS'])
@cross_origin()
def handle_question(dest_id):
    data = request.get_json()
    question = data.get('question')

    chat_id = data.get('chat_id')
    if not chat_id:
        existing_chat_bot = ChatBot.query.filter_by(dest_id=dest_id).first()
        if existing_chat_bot:
            chat_id = existing_chat_bot.chat_id
        else:
            try:
                new_chat_bot = ChatBot(dest_id=dest_id)
                db.session.add(new_chat_bot)
                db.session.commit()
                chat_id = new_chat_bot.chat_id
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": f"새로운 세션 생성에 실패했습니다: {str(e)}"}), 500
    else:
        try:
            chat_id = int(chat_id)
        except ValueError:
            return jsonify({"error": "유효하지 않은 chat_id입니다."}), 400

    max_content_length = 300
    if len(question) > max_content_length:
        question = question[:max_content_length]

    try:
        question_log = ChatBotLog(
            chat_id=chat_id,
            qna='Q',
            content=question
        )
        db.session.add(question_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"질문 로그 저장에 실패했습니다: {str(e)}"}), 500

    file_path = get_pdf_path_by_dest_id(dest_id)
    if not file_path:
        return jsonify({"error": f"{dest_id}번 여행지에 관한 PDF 파일이 없습니다."}), 404

    try:
        pdf_content = chatbot_module.get_pdf_from_s3('gg-pdfbucket', file_path)
    except Exception as e:
        return jsonify({"error": f"PDF 획득에 실패했습니다: {str(e)}"}), 500

    vector_store = chatbot_module.load_and_embed_pdfs(pdf_content)

    try:
        result = chatbot_module.generate_answer(vector_store, question)
    except Exception as e:
        return jsonify({"error": f"응답 생성에 실패했습니다: {str(e)}"}), 500

    if len(result) > max_content_length:
        result = result[:max_content_length]

    try:
        answer_log = ChatBotLog(
            chat_id=chat_id,
            qna='A',
            content=result
        )
        db.session.add(answer_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"답변 로그 저장에 실패했습니다: {str(e)}"}), 500

    return jsonify({
        "answer": result,
        "chat_id": chat_id
    }), 200

@app.route('/place/recommendation/<int:dest_id>', methods=['GET'])
@cross_origin()
def get_recommendations(dest_id):
    file_path = get_pdf_path_by_dest_id(dest_id)
    if not file_path:
        return jsonify({"error": f"{dest_id}번 여행지에 관한 PDF 파일이 없습니다."}), 404

    try:
        pdf_content = recommendation_module.get_pdf_from_s3('gg-pdfbucket', file_path)
    except Exception as e:
        return jsonify({"error": f"PDF 획득에 실패했습니다: {str(e)}"}), 500

    vector_store = recommendation_module.load_and_embed_pdfs(pdf_content)

    try:
        recommendations = recommendation_module.generate_recommendations(vector_store)
    except Exception as e:
        return jsonify({"error": f"추천 생성에 실패했습니다: {str(e)}"}), 500

    max_content_length = 1000
    if len(recommendations) > max_content_length:
        recommendations = recommendations[:max_content_length]

    return jsonify({
        "recommendations": recommendations
    }), 200

@app.route('/load_and_embed_pdfs', methods=['POST'])
@cross_origin()
def load_and_embed_pdfs_api():
    data = request.get_json()
    bucket_name = data.get('bucket_name')
    object_key = data.get('object_key')

    if not bucket_name or not object_key:
        return jsonify({'error': 'bucket_name과 object_key는 필수입니다.'}), 400

    try:
        pdf_content = chatbot_module.get_pdf_from_s3(bucket_name, object_key)
    except Exception as e:
        return jsonify({'error': f"PDF 획득에 실패했습니다: {str(e)}"}), 500

    try:
        vector_store = chatbot_module.load_and_embed_pdfs(pdf_content)
    except Exception as e:
        return jsonify({'error': f"PDF 임베딩에 실패했습니다: {str(e)}"}), 500

    try:
        vector_store_id = f"vector_store_{object_key}.faiss"
        vector_store.save_local(vector_store_id)
    except Exception as e:
        return jsonify({'error': f"벡터 스토어 저장에 실패했습니다: {str(e)}"}), 500

    return jsonify({'message': 'PDF 임베딩 성공', 'vector_store_id': vector_store_id}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
