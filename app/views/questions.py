from flask import Blueprint, request, jsonify
from app.models import db, Question, Choices
from sqlalchemy.exc import SQLAlchemyError

questions_bp = Blueprint('questions', __name__)

# 질문 생성
@questions_bp.route('/questions', methods=['POST'])
def create_question():
    data = request.json
    title = data.get('title')
    sqe = data.get('sqe')
    image_id = data.get('image_id')

    if not title or not isinstance(title, str):
        return jsonify({"error": "유효하지 않은 제목입니다."}), 400
    if not isinstance(sqe, int):
        return jsonify({"error": "유효하지 않은 순서입니다."}), 400
    if not image_id or not isinstance(image_id, int):
        return jsonify({"error": "유효하지 않은 이미지 ID입니다."}), 400

    try:
        question = Question(
            title=title,
            sqe=sqe,
            image_id=image_id
        )
        db.session.add(question)
        db.session.commit()
        return jsonify(question.to_dict()), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "질문 생성 중 오류가 발생했습니다."}), 500

# 특정 질문 조회
@questions_bp.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.query.get(question_id)
    if not question:
        return jsonify({"error": f"ID {question_id}에 해당하는 질문을 찾을 수 없습니다."}), 404
    return jsonify(question.to_dict()), 200

# 모든 질문 조회
@questions_bp.route('/questions', methods=['GET'])
def get_all_questions():
    questions = Question.query.all()
    return jsonify([question.to_dict() for question in questions]), 200