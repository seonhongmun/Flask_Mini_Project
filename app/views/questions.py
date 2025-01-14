from flask import jsonify, request
from flask_smorest import Blueprint
from app.models import db, Question, Image
from sqlalchemy.exc import SQLAlchemyError
from app.views.choices import Choices

# Blueprint 생성
questions_bp = Blueprint("questions", __name__, url_prefix="/questions")

@questions_bp.route("/count", methods=["GET"])
def get_questions_count():
    """질문 개수 확인"""
    total_questions = Question.query.count()
    return jsonify({"total": total_questions}), 200

@questions_bp.route("/", methods=["GET"])
def get_all_questions():
    """
    모든 질문 조회
    """
    try:
        # 데이터베이스에서 모든 질문 가져오기
        questions = Question.query.all()
        
        # 질문 데이터를 JSON으로 변환
        result = [
            {
                "id": question.id,
                "title": question.title,
                "is_active": question.is_active,
                "sqe": question.sqe,
                "image_id": question.image_id
            }
            for question in questions
        ]

        return jsonify(result), 200  # 성공 응답
    except Exception as e:
        # 에러 발생 시 오류 메시지 반환
        return jsonify({"error": f"질문 조회 중 오류가 발생했습니다: {str(e)}"}), 500


@questions_bp.route("/", methods=["POST"])
def create_question():
    """질문 생성 (선택지 포함)"""
    data = request.get_json()
    title = data.get("title")
    sqe = data.get("sqe")
    image_id = data.get("image_id")
    choices_data = data.get("choices", [])  # 선택지 데이터 가져오기

    # 질문 데이터 추가
    question = Question(title=title, sqe=sqe, image_id=image_id, is_active=True)
    db.session.add(question)
    db.session.commit()  # 질문 ID 생성 후 선택지와 연결하기 위해 커밋

    # 선택지 데이터 추가
    for choice in choices_data:
        new_choice = Choices(
            content=choice["content"],
            is_active=choice["is_active"],
            sqe=choice.get("sqe", 1),
            question_id=question.id
        )
        db.session.add(new_choice)

    db.session.commit()
    return jsonify({"message": f"Question '{title}' and choices created successfully!"}), 201


@questions_bp.route("/<int:question_id>", methods=["GET"])
def get_question(question_id):
    """
    특정 질문 조회
    """
    try:
        # 데이터베이스에서 질문 ID로 조회
        question = Question.query.get(question_id)
        if not question:
            return jsonify({"error": f"ID {question_id}의 질문을 찾을 수 없습니다."}), 404

        # 질문 데이터 반환
        return jsonify({
            "id": question.id,
            "title": question.title,
            "is_active": question.is_active,
            "sqe": question.sqe,
            "image_id": question.image_id
        }), 200

    except Exception as e:
        # 에러 발생 시 오류 메시지 반환
        return jsonify({"error": f"질문 조회 중 오류가 발생했습니다: {str(e)}"}), 500


@questions_bp.route("/<int:question_id>", methods=["DELETE"])
def delete_question(question_id):
    """
    특정 질문 삭제
    """
    try:
        # 데이터베이스에서 질문 ID로 조회
        question = Question.query.get(question_id)
        if not question:
            return jsonify({"error": f"ID {question_id}의 질문을 찾을 수 없습니다."}), 404

        # 질문 삭제
        db.session.delete(question)
        db.session.commit()

        # 성공 메시지 반환
        return jsonify({"message": f"ID {question_id}의 질문이 삭제되었습니다."}), 200

    except SQLAlchemyError as e:
        # 데이터베이스 에러 처리
        db.session.rollback()
        return jsonify({"error": f"질문 삭제 중 오류가 발생했습니다: {str(e)}"}), 500