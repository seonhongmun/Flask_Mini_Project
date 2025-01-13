from flask import Blueprint, request, jsonify  # Flask 모듈 가져오기
from app.models import db, Question, Choices  # 데이터베이스 모델 가져오기
from sqlalchemy.exc import SQLAlchemyError  # SQLAlchemy 예외 처리

# Blueprint 생성 - 선택지 관련 API 관리
choices_bp = Blueprint("choices", __name__, url_prefix="/questions")

@choices_bp.route("/<int:question_id>/choices", methods=["POST"])
def create_choices(question_id):
    """
    특정 질문에 대한 선택지 생성
    """
    try:
        # 요청 데이터 가져오기
        data = request.json

        # 요청 데이터에서 'choices' 키 확인 및 유효성 검사
        choices = data.get("choices")
        if not isinstance(choices, list) or not all(isinstance(choice, str) for choice in choices):
            return jsonify({"error": "유효하지 않은 선택지 리스트입니다. 문자열로 구성된 리스트를 제공해야 합니다."}), 400

        # 질문 ID로 질문 객체 조회
        question = Question.query.get(question_id)
        if not question:
            return jsonify({"error": f"ID {question_id}에 해당하는 질문을 찾을 수 없습니다."}), 404

        # 선택지 생성 및 데이터베이스에 저장
        for index, content in enumerate(choices, start=1):
            choice = Choices(
                content=content,
                sqe=index,
                question_id=question_id
            )
            db.session.add(choice)
        db.session.commit()

        return jsonify({"message": f"{len(choices)}개의 선택지가 성공적으로 생성되었습니다."}), 201

    except SQLAlchemyError as e:
        # SQLAlchemy 오류 발생 시 롤백 처리
        db.session.rollback()
        return jsonify({"error": f"선택지 생성 중 오류가 발생했습니다: {str(e)}"}), 500

@choices_bp.route("/<int:question_id>/choices", methods=["GET"])
def get_choices(question_id):
    """
    특정 질문에 대한 선택지 조회
    """
    try:
        # 질문 ID로 질문 객체 조회
        question = Question.query.get(question_id)
        if not question:
            return jsonify({"error": f"ID {question_id}에 해당하는 질문을 찾을 수 없습니다."}), 404

        # 해당 질문에 연결된 선택지 조회
        choices = Choices.query.filter_by(question_id=question_id).all()

        # 선택지 데이터를 JSON으로 변환하여 반환
        return jsonify([choice.to_dict() for choice in choices]), 200

    except Exception as e:
        # 기타 오류 발생 시 처리
        return jsonify({"error": f"선택지 조회 중 오류가 발생했습니다: {str(e)}"}), 500