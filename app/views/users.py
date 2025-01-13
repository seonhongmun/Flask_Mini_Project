from flask_smorest import Blueprint
from flask.views import MethodView
from marshmallow import Schema, fields
from sqlalchemy.exc import SQLAlchemyError
from app.models import User, AgeStatus, GenderStatus, db

# 블루프린트 생성
users_bp = Blueprint("users", __name__, url_prefix="/users")


# 요청 및 응답 스키마 정의
class UserRequestSchema(Schema):
    username = fields.String(required=True, description="사용자 이름")
    age = fields.String(required=True, validate=lambda x: x in AgeStatus._value2member_map_, description="나이대")
    gender = fields.String(required=True, validate=lambda x: x in GenderStatus._value2member_map_, description="성별")
    email = fields.Email(required=True, description="이메일 주소")


class UserResponseSchema(Schema):
    id = fields.Integer(description="유저 ID")
    name = fields.String(description="사용자 이름")
    age = fields.String(description="나이대")
    gender = fields.String(description="성별")
    email = fields.Email(description="이메일 주소")


class UserListResponseSchema(Schema):
    users = fields.List(fields.Nested(UserResponseSchema), description="사용자 목록")


# 사용자 관리 API 클래스
@users_bp.route("/")
class UserList(MethodView):
    @users_bp.response(200, UserListResponseSchema)
    def get(self):
        """
        모든 사용자 조회
        """
        users = User.query.all()
        return {"users": [user.to_dict() for user in users]}

    @users_bp.arguments(UserRequestSchema)
    @users_bp.response(201, UserResponseSchema)
    def post(self, user_data):
        """
        사용자 생성
        """
        try:
            # 사용자 생성
            new_user = User(
                name=user_data["username"],
                age=AgeStatus(user_data["age"]),
                gender=GenderStatus(user_data["gender"]),
                email=user_data["email"],
            )
            db.session.add(new_user)
            db.session.commit()

            return new_user.to_dict()

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "데이터베이스 오류가 발생했습니다.", "details": str(e)}, 500


@users_bp.route("/<int:user_id>")
class UserDetail(MethodView):
    @users_bp.response(200, UserResponseSchema)
    def get(self, user_id):
        """
        특정 사용자 조회
        """
        user = User.query.get(user_id)
        if not user:
            return {"message": f"ID {user_id}의 유저를 찾을 수 없습니다."}, 404
        return user.to_dict()

    @users_bp.arguments(UserRequestSchema)
    @users_bp.response(200, UserResponseSchema)
    def put(self, user_data, user_id):
        """
        특정 사용자 업데이트
        """
        user = User.query.get(user_id)
        if not user:
            return {"message": f"ID {user_id}의 유저를 찾을 수 없습니다."}, 404

        try:
            # 사용자 데이터 업데이트
            user.name = user_data["username"]
            user.age = AgeStatus(user_data["age"])
            user.gender = GenderStatus(user_data["gender"])
            user.email = user_data["email"]

            db.session.commit()
            return user.to_dict()

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "데이터베이스 오류가 발생했습니다.", "details": str(e)}, 500

    def delete(self, user_id):
        """
        특정 사용자 삭제
        """
        user = User.query.get(user_id)
        if not user:
            return {"message": f"ID {user_id}의 유저를 찾을 수 없습니다."}, 404

        try:
            db.session.delete(user)
            db.session.commit()
            return {"message": f"ID {user_id}의 유저가 성공적으로 삭제되었습니다."}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "데이터베이스 오류가 발생했습니다.", "details": str(e)}, 500