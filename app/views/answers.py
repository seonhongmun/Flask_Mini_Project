from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from ..models import Answer, db

answer_bp = Blueprint('Answer', 'answer', url_prefix='/submit')

# 답변 정보 생성
@answer_bp.route('/', methods=["POST"])
class AnswerCreate(MethodView):
    def post(self):
        data = request.json

        for answer in data:
            user_id = answer.get("userId")
            choice_id=answer.get("choiceId")
        # userId와 choiceId 유효성 검사
            if not user_id or not choice_id:
                return {"msg": "Invalid data: userId and choiceId are required"}, 400

            # Answer 객체 생성 및 데이터베이스에 추가
            new_answer = Answer(user_id=user_id, choice_id=choice_id)
            db.session.add(new_answer)


        # 데이터베이스에 변경사항 커밋
        db.session.commit()

        # 성공적으로 생성된 응답 반환
        return {"msg":"Successfully created answers.",}, 201


# 답변 조회
@answer_bp.route('/<int:user_id>/<int:choice_id>')
class AnswerGet(MethodView):
    def get(self,user_id, choice_id):
        answers = Answer.query.filter_by(user_id=user_id, choice_id=choice_id).all()
        if not answers:
            return {"msg":"No Found Data"}
        return [answer.to_dict() for answer in answers]

# 특정 답변 수정
@answer_bp.route('/admin/<int:user_id>/<int:choice_id>')
class PostAnswer(MethodView):
    def put(self, user_id, choice_id):
        # choice_id에 맞는 Answer 객체를 찾기
        answer = Answer.query.filter(Answer.user_id == user_id, Answer.choice_id == choice_id).first()

        if not answer:
            return jsonify({"msg": "Not found user_id or choice_id"}), 404
        data = request.json
        for key, value in data.items():
            if hasattr(answer, key):  # answer 객체에 해당 속성이 있는지 확인
                setattr(answer, key, value)  # 해당 속성을 수정

        db.session.commit()

        return jsonify(answer.to_dict()), 200  # 수정된 객체 반환