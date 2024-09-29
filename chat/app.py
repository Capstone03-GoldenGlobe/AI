from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import chatbot_module
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://adminnn:Goldenglobe!@goldenglobe-mysql.mysql.database.azure.com/ggDatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class PdfList(db.Model):
    __tablename__ = 'pdf_list'
    pdf_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    dest_id = db.Column(db.Integer, nullable=False)
    pdf_name = db.Column(db.String(255), nullable=False)
    pdf_path = db.Column(db.String(255), nullable=False)

def get_pdf_path_by_dest_id(dest_id):
    pdf_file = PdfList.query.filter_by(dest_id=dest_id).first()
    if not pdf_file:
        return None
    return pdf_file.pdf_path


@app.route('/chatbot/question/<dest_id>', methods=['POST'])
def handle_question(dest_id):
    data = request.get_json()
    question = data.get('question')

    file_path = get_pdf_path_by_dest_id(dest_id)
    if not file_path:
        return jsonify({"error": f"{dest_id}번 여행지에 관한 pdf 파일이 없습니다."}), 404

    try:
        pdf_content = chatbot_module.get_pdf_from_s3('gg-pdfbucket', file_path)
    except Exception as e:
        return jsonify({"error": f"PDF 획득에 실패했습니다 : {str(e)}"}), 500

    vector_store = chatbot_module.load_and_embed_pdfs(pdf_content)

    try:
        result = chatbot_module.generate_answer(vector_store, question)
    except Exception as e:
        return jsonify({"error": f"응답 생성에 실패했습니다 : {str(e)}"}), 500

    return jsonify({
        "answer": result
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
