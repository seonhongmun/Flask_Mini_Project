from flask_smorest import Blueprint
from flask.views import MethodView
from marshmallow import Schema, fields
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Question

# Flask-Smorest Blueprint
questions_bp = Blueprint("questions", __name__, url_prefix="/questions")

# Schema Definitions
class QuestionRequestSchema(Schema):
    title = fields.String(required=True, description="질문 제목")
    sqe = fields.Integer(required=True, description="질문 순서")
    image_id = fields.Integer(required=True, description="이미지 ID")


class QuestionResponseSchema(Schema):
    id = fields.Integer(description="질문 ID")
    title = fields.String(description="질문 제목")
    is_active = fields.Boolean(description="활성 상태")
    sqe = fields.Integer(description="질문 순서")
    image_id = fields.Integer(description="이미지 ID")
    created_at = fields.DateTime(description="생성 시간")
    updated_at = fields.DateTime(description="수정 시간")


class QuestionListResponseSchema(Schema):
    questions = fields.List(fields.Nested(QuestionResponseSchema), description="질문 목록")

# API Endpoints
@questions_bp.route("/")
class Questions(MethodView):
    @questions_bp.response(200, QuestionListResponseSchema)
    def get(self):
        """
        모든 질문 조회
        """
        questions = Question.query.all()
        return {"questions": [question.to_dict() for question in questions]}

@questions_bp.arguments(QuestionRequestSchema)
@questions_bp.response(201, QuestionResponseSchema)
def post(self, data):
    """
    질문 생성
    """
    try:
        # 이미지 ID가 유효한지 확인
        if not db.session.query(Image).filter_by(id=data["image_id"]).first():
            return {"message": f"이미지 ID {data['image_id']}를 찾을 수 없습니다."}, 400

        question = Question(
            title=data["title"],
            sqe=data["sqe"],
            image_id=data["image_id"]
        )
        db.session.add(question)
        db.session.commit()
        return question.to_dict()

    except SQLAlchemyError as e:
        db.session.rollback()
        return {"message": "질문 생성 중 오류가 발생했습니다.", "details": str(e)}, 500

@questions_bp.route("/<int:question_id>")
class QuestionDetail(MethodView):
    @questions_bp.response(200, QuestionResponseSchema)
    def get(self, question_id):
        """
        특정 질문 조회
        """
        question = Question.query.get(question_id)
        if not question:
            return {"message": f"ID {question_id}에 해당하는 질문을 찾을 수 없습니다."}, 404
        return question.to_dict()

    def delete(self, question_id):
        """
        특정 질문 삭제
        """
        question = Question.query.get(question_id)
        if not question:
            return {"message": f"ID {question_id}에 해당하는 질문을 찾을 수 없습니다."}, 404

        try:
            db.session.delete(question)
            db.session.commit()
            return {"message": f"ID {question_id}의 질문이 삭제되었습니다."}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "질문 삭제 중 오류가 발생했습니다.", "details": str(e)}, 500