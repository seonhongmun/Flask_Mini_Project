# 선택지 생성
from flask import Blueprint, request, jsonify
from app.models import db, Question, Choices
from sqlalchemy.exc import SQLAlchemyError

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/questions/<int:question_id>/choices', methods=['POST'])
def create_choices(question_id):
    data = request.json
    choices = data.get('choices')

    if not isinstance(choices, list) or not all(isinstance(choice, str) for choice in choices):
        return jsonify({"error": "유효하지 않은 선택지 리스트입니다."}), 400

    question = Question.query.get(question_id)
    if not question:
        return jsonify({"error": f"ID {question_id}에 해당하는 질문을 찾을 수 없습니다."}), 404

    try:
        for index, content in enumerate(choices, start=1):
            choice = Choices(
                content=content,
                sqe=index,
                question_id=question_id
            )
            db.session.add(choice)
        db.session.commit()
        return jsonify({"message": f"{len(choices)}개의 선택지가 성공적으로 생성되었습니다."}), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "선택지 생성 중 오류가 발생했습니다."}), 500

# 특정 질문의 선택지 조회
@questions_bp.route('/questions/<int:question_id>/choices', methods=['GET'])
def get_choices(question_id):
    question = Question.query.get(question_id)
    if not question:
        return jsonify({"error": f"ID {question_id}에 해당하는 질문을 찾을 수 없습니다."}), 404

    choices = Choices.query.filter_by(question_id=question_id).all()
    return jsonify([choice.to_dict() for choice in choices]), 200
