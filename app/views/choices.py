from flask import jsonify, abort, request
from flask_smorest import Blueprint
from app.models import db, Choices

choices_bp = Blueprint("choices", __name__, url_prefix="/choice")

@choices_bp.route("/<int:question_id>", methods=["GET"])
def get_choices_by_question(question_id):
    """
    특정 질문의 선택지 리스트 반환
    """
    try:
        # 특정 질문의 선택지 필터링
        choices = Choices.query.filter_by(question_id=question_id).all()
        
        # 선택지 리스트가 비어있으면 404 반환
        if not choices:
            return jsonify({"message": f"ID {question_id}의 선택지를 찾을 수 없습니다."}), 404

        # 선택지 데이터를 JSON으로 변환
        result = {
            "choices": [
                {
                    "id": choice.id,
                    "content": choice.content,
                    "is_active": choice.is_active,
                }
                for choice in choices
            ]
        }
        return jsonify(result), 200

    except Exception as e:
        # 에러 처리
        abort(500, message=f"선택지 조회 중 오류가 발생했습니다: {str(e)}")

@choices_bp.route("/", methods=["POST"])
def create_choice():
    """새 선택지 추가"""
    data = request.get_json()
    choice = Choices(content=data["content"], sqe=data["sqe"], question_id=data["question_id"])
    db.session.add(choice)
    db.session.commit()
    return jsonify({"message": f"Content: {data['content']} choice Success Create"}), 201