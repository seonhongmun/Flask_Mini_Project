from flask import request, jsonify
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Question, Image, Choices

# Blueprint 생성
questions_bp = Blueprint("questions", __name__, url_prefix="/questions")

@questions_bp.route("/", methods=["GET"])
def get_all_questions():

    try:
        questions = Question.query.all()
        result = [
            {
                "id": question.id,
                "title": question.title,
                "is_active": question.is_active,
                "sqe": question.sqe,
                "image_id": question.image_id,
            }
            for question in questions
        ]
        return jsonify(result), 200
    except SQLAlchemyError as e:
        abort(500, message=f"질문 조회 중 오류가 발생했습니다: {str(e)}")

#총 질문 갯수 카운트
@questions_bp.route("/count", methods=["GET"])
def get_questions_count():
    try:
        # 데이터베이스에서 질문 개수 조회
        total_questions = Question.query.count()
        return jsonify({"total": total_questions}), 200
    except SQLAlchemyError as e:
        abort(500, message=f"질문 개수 조회 중 오류가 발생했습니다: {str(e)}")

@questions_bp.route("/<int:question_id>", methods=["GET"])
def get_question_by_id(question_id):
    try:
        question = Question.query.get(question_id)
        if not question:
            abort(404, message=f"ID {question_id}의 질문을 찾을 수 없습니다.")

        choices = [
            choice.to_dict() for choice in question.choices
        ]
        return jsonify({
            "id": question.id,
            "title": question.title,
            "is_active": question.is_active,
            "sqe": question.sqe,
            "image_id": question.image_id,
            "choices": choices,
        }), 200
    except SQLAlchemyError as e:
        abort(500, message=f"질문 조회 중 오류가 발생했습니다: {str(e)}")


@questions_bp.route("/", methods=["POST"])
def create_question():
    data = request.get_json()
    title = data.get("title")
    sqe = data.get("sqe")
    image_id = data.get("image_id")
    choices_data = data.get("choices", [])

    if not title or not sqe or not image_id:
        abort(400, message="title, sqe, image_id는 필수 필드입니다.")

    try:
        # 질문 생성
        question = Question(title=title, sqe=sqe, image_id=image_id, is_active=True)
        db.session.add(question)
        db.session.commit()  # 질문 ID 확보를 위해 커밋

        # 선택지 생성
        for choice in choices_data:
            new_choice = Choices(
                content=choice.get("content"),
                is_active=choice.get("is_active", True),
                sqe=choice.get("sqe", 1),
                question_id=question.id,
            )
            db.session.add(new_choice)
        db.session.commit()

        return jsonify({"message": f"Question '{title}' and choices created successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, message=f"질문 생성 중 오류가 발생했습니다: {str(e)}")


@questions_bp.route("/<int:question_id>", methods=["DELETE"])
def delete_question(question_id):
    try:
        question = Question.query.get(question_id)
        if not question:
            abort(404, message=f"ID {question_id}의 질문을 찾을 수 없습니다.")

        # 질문과 연관된 선택지 삭제
        for choice in question.choices:
            db.session.delete(choice)

        # 질문 삭제
        db.session.delete(question)
        db.session.commit()

        return jsonify({"message": f"ID {question_id}의 질문이 삭제되었습니다."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, message=f"질문 삭제 중 오류가 발생했습니다: {str(e)}")
