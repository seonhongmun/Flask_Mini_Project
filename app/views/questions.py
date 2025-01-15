from flask import request, jsonify
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Question, Image, Choices

# Blueprint 생성
questions_bp = Blueprint("questions", __name__)

@questions_bp.route("/question", methods=["GET"])
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

@questions_bp.route("/questions/count", methods=["GET"])
def count_questions():
    """질문 개수 확인"""
    total_questions = Question.query.count()
    return jsonify({"total": total_questions}), 200

@questions_bp.route("/question/<int:question_id>", methods=["GET"])
def get_question(question_id):
    """특정 질문 가져오기"""
    question = Question.query.get(question_id)
    if not question:
        return jsonify({"message": f"ID {question_id}의 질문을 찾을 수 없습니다."}), 404
    return jsonify({
        "question": {
            "id": question.id,
            "title": question.title,
            "image": {"url": question.image.url} if question.image else None,
        }
    }), 200

@questions_bp.route("/question", methods=["POST"])
def create_question():
    """새 질문 추가"""
    data = request.get_json()
    question = Question(title=data["title"], sqe=data["sqe"], image_id=data["image_id"])
    db.session.add(question)
    db.session.commit()
    for choice_data in data.get("choices", []):
        choice = Choices(
            content=choice_data["content"], sqe=choice_data["sqe"], question_id=question.id
        )
        db.session.add(choice)
    db.session.commit()
    return jsonify({"message": f"Title: {data['title']} question Success Create"}), 201


@questions_bp.route("/question/<int:question_id>", methods=["DELETE"])
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
