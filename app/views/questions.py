from flask import jsonify, request
from flask_smorest import Blueprint
from app.models import db, Question, Image
from sqlalchemy.exc import SQLAlchemyError

# Blueprint 생성
questions_bp = Blueprint("questions", __name__, url_prefix="/questions")


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
    """
    새로운 질문 생성
    """
    try:
        # 클라이언트 요청 데이터 가져오기
        data = request.json

        # 필수 데이터 확인
        required_fields = ["title", "sqe", "image_id"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"}), 400

        # 이미지 ID 유효성 확인
        image = Image.query.get(data["image_id"])
        if not image:
            return jsonify({"error": f"이미지 ID {data['image_id']}를 찾을 수 없습니다."}), 400

        # 새 질문 생성
        question = Question(
            title=data["title"],
            sqe=data["sqe"],
            image_id=data["image_id"]
        )

        # 데이터베이스에 저장
        db.session.add(question)
        db.session.commit()

        # 성공적으로 생성된 질문 반환
        return jsonify({
            "id": question.id,
            "title": question.title,
            "is_active": question.is_active,
            "sqe": question.sqe,
            "image_id": question.image_id
        }), 201

    except SQLAlchemyError as e:
        # 데이터베이스 에러 처리
        db.session.rollback()
        return jsonify({"error": f"질문 생성 중 오류가 발생했습니다: {str(e)}"}), 500


@questions_bp.route("/<int:question_id>", methods=["GET"])
def get_question_by_id(question_id):
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