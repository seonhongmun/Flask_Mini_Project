from flask import request, jsonify
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Answer, User, Choices, Question

# Blueprint 생성
answers_bp = Blueprint("answers", __name__)


@answers_bp.route("/submit", methods=["POST"])
def submit_answers():
    """
    답변 제출하기
    """
    data = request.get_json()  # 요청 데이터 가져오기
        # 각 답변 처리
    for answer_data in data:
        user_id = answer_data.get("userId")
        choice_id = answer_data.get("choiceId")

        if not user_id or not choice_id:
            abort(400, message="'userId'와 'choiceId'는 필수 항목입니다.")

        # 답변 데이터 생성 및 추가
        new_answer = Answer(user_id=user_id, choice_id=choice_id)
        db.session.add(new_answer)

    db.session.commit()  # 데이터베이스 저장

    return {"msg":"Successfully created answers.",}, 201

@answers_bp.route("/answers/<int:user_id>", methods=["GET"])
def get_answers_by_user(user_id):
    """
    특정 사용자의 답변 조회
    ---
    요청:
    - user_id: 사용자 ID
    응답:
    - 성공: 해당 사용자의 답변 리스트
    - 실패: 사용자나 답변을 찾을 수 없다는 메시지
    """
    try:
        # 사용자 확인
        user = User.query.get(user_id)
        if not user:
            abort(404, message=f"ID {user_id}에 해당하는 사용자가 존재하지 않습니다.")

        # 사용자의 답변 조회
        answers = Answer.query.filter_by(user_id=user_id).all()
        if not answers:
            return jsonify({"message": "이 사용자는 아직 답변을 제출하지 않았습니다."}), 200

        # 응답 데이터 구성
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
        abort(500, message=f"답변 조회 중 오류가 발생했습니다: {str(e)}")
