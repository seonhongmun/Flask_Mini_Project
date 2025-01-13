from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Answer, User, Choices, Question

# Blueprint 생성
answers_bp = Blueprint("answers", __name__, url_prefix="/answers")


@answers_bp.route("/", methods=["POST"])
def create_answer():
    """
    답변 생성 API
    - 특정 질문(question)에 대해 특정 선택지(choice)를 선택한 답변을 생성합니다.
    """
    try:
        # 요청 데이터 가져오기
        data = request.json

        # 필수 필드 확인
        if not all(key in data for key in ["user_id", "choice_id"]):
            return jsonify({"error": "필수 필드가 누락되었습니다. 'user_id'와 'choice_id'를 입력하세요."}), 400

        # 데이터 유효성 검사
        user = User.query.get(data["user_id"])
        if not user:
            return jsonify({"error": f"ID {data['user_id']}에 해당하는 사용자가 존재하지 않습니다."}), 404

        choice = Choices.query.get(data["choice_id"])
        if not choice:
            return jsonify({"error": f"ID {data['choice_id']}에 해당하는 선택지가 존재하지 않습니다."}), 404

        question = Question.query.get(choice.question_id)
        if not question:
            return jsonify({"error": f"선택지가 연결된 질문(ID {choice.question_id})을 찾을 수 없습니다."}), 404

        # 답변 생성
        answer = Answer(user_id=data["user_id"], choice_id=data["choice_id"])
        db.session.add(answer)
        db.session.commit()

        return jsonify({
            "message": "답변이 성공적으로 생성되었습니다.",
            "answer": {
                "id": answer.id,
                "user_id": answer.user_id,
                "choice_id": answer.choice_id,
                "question_id": question.id
            }
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"답변 생성 중 오류가 발생했습니다: {str(e)}"}), 500


@answers_bp.route("/<int:user_id>", methods=["GET"])
def get_answers_by_user(user_id):
    """
    특정 사용자가 제출한 답변 조회 API
    """
    try:
        # 사용자 유효성 확인
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": f"ID {user_id}에 해당하는 사용자가 존재하지 않습니다."}), 404

        # 사용자가 제출한 답변 조회
        answers = Answer.query.filter_by(user_id=user_id).all()
        if not answers:
            return jsonify({"message": "이 사용자는 아직 답변을 제출하지 않았습니다."}), 200

        # 답변 데이터를 JSON으로 변환
        result = []
        for answer in answers:
            choice = Choices.query.get(answer.choice_id)
            question = Question.query.get(choice.question_id) if choice else None
            result.append({
                "answer_id": answer.id,
                "user_id": answer.user_id,
                "choice_id": answer.choice_id,
                "choice_content": choice.content if choice else None,
                "question_id": question.id if question else None,
                "question_title": question.title if question else None
            })

        return jsonify(result), 200

    except SQLAlchemyError as e:
        return jsonify({"error": f"답변 조회 중 오류가 발생했습니다: {str(e)}"}), 500