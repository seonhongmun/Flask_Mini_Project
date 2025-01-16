from flask import jsonify, request, abort
from flask_smorest import Blueprint
from ..models import Answer, db

answer_bp = Blueprint("Answer", __name__, url_prefix="/submit")

@answer_bp.route("/", methods=["POST"])
def create_answers():
    """
    답변 생성 API
    """
    try:
        # 요청으로부터 JSON 데이터 가져오기
        data = request.get_json()

        # 데이터를 순회하며 각 답변을 데이터베이스에 추가
        for answer in data:
            user_id = answer.get("userId")
            choice_id = answer.get("choiceId")

            # userId와 choiceId 유효성 검사
            if not user_id or not choice_id:
                return jsonify({"msg": "Invalid data: userId and choiceId are required"}), 400

            # Answer 객체 생성 및 데이터베이스에 추가
            new_answer = Answer(user_id=user_id, choice_id=choice_id)
            db.session.add(new_answer)

        # 데이터베이스 커밋
        db.session.commit()

        # 성공 응답 반환
        return jsonify({"msg": "Successfully created answers."}), 201

    except Exception as e:
        # 에러 처리
        abort(500, description=f"An error occurred while creating answers: {str(e)}")

@answer_bp.route("/<int:user_id>/<int:choice_id>", methods=["GET"])
def get_answers(user_id, choice_id):
    """
    특정 사용자와 선택지에 해당하는 답변 조회 API
    """
    try:
        # 주어진 user_id와 choice_id로 답변 조회
        answers = Answer.query.filter_by(user_id=user_id, choice_id=choice_id).all()

        # 답변이 없으면 메시지 반환
        if not answers:
            return jsonify({"msg": "No found data"}), 404

        # 결과를 JSON 형태로 반환
        result = [answer.to_dict() for answer in answers]
        return jsonify(result), 200

    except Exception as e:
        # 에러 처리
        abort(500, description=f"An error occurred while fetching answers: {str(e)}")

@answer_bp.route("/admin/<int:user_id>/<int:choice_id>", methods=["PUT"])
def update_answer(user_id, choice_id):
    """
    특정 답변 수정 API
    """
    try:
        # user_id와 choice_id로 Answer 객체 찾기
        answer = Answer.query.filter(Answer.user_id == user_id, Answer.choice_id == choice_id).first()

        # Answer 객체가 없으면 404 반환
        if not answer:
            return jsonify({"msg": "Not found user_id or choice_id"}), 404

        # 요청 데이터 가져오기
        data = request.get_json()

        # Answer 객체의 속성 업데이트
        for key, value in data.items():
            if hasattr(answer, key):  # answer 객체에 해당 속성이 존재하는지 확인
                setattr(answer, key, value)  # 해당 속성 값 업데이트

        # 데이터베이스에 변경사항 커밋
        db.session.commit()

        # 수정된 객체를 JSON으로 반환
        return jsonify(answer.to_dict()), 200

    except Exception as e:
        # 에러 처리
        abort(500, description=f"An error occurred while updating the answer: {str(e)}")