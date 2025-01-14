from flask import request, jsonify
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Choices, Question

# Blueprint 생성
choices_bp = Blueprint("choices", __name__, url_prefix="/choice")


@choices_bp.route("/<int:question_id>", methods=["GET"])
def get_choices_by_question(question_id):
    try:
        # 질문 존재 여부 확인
        question = Question.query.get(question_id)
        if not question:
            abort(404, message=f"ID {question_id}의 질문을 찾을 수 없습니다.")

        # 선택지 가져오기
        choices = Choices.query.filter_by(question_id=question_id).all()
        if not choices:
            return jsonify({"message": f"ID {question_id}의 선택지가 없습니다."}), 200

        # 선택지 데이터 반환
        return jsonify([choice.to_dict() for choice in choices]), 200
    except SQLAlchemyError as e:
        abort(500, message=f"선택지 조회 중 오류가 발생했습니다: {str(e)}")


@choices_bp.route("/<int:question_id>", methods=["POST"])
def create_choices(question_id):
    data = request.get_json()
    choices_data = data.get("choices", [])

    if not choices_data:
        abort(400, message="선택지 데이터가 비어 있습니다.")

    try:
        # 질문 존재 여부 확인
        question = Question.query.get(question_id)
        if not question:
            abort(404, message=f"ID {question_id}의 질문을 찾을 수 없습니다.")

        # 선택지 생성
        created_choices = []
        for choice in choices_data:
            new_choice = Choices(
                content=choice.get("content"),
                is_active=choice.get("is_active", True),
                sqe=choice.get("sqe", 1),
                question_id=question_id
            )
            db.session.add(new_choice)
            created_choices.append(new_choice)

        db.session.commit()

        return jsonify({
            "message": f"ID {question_id}의 선택지가 성공적으로 생성되었습니다.",
            "choices": [choice.to_dict() for choice in created_choices]
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, message=f"선택지 생성 중 오류가 발생했습니다: {str(e)}")
