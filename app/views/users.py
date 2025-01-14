from flask import request, jsonify
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, User, AgeStatus, GenderStatus

# Blueprint 생성
users_bp = Blueprint("users", __name__)

#유저 생성/signup
@users_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json # 요청 데이터 받아오기 

#데이터값 가져오기
    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')
    email = data.get('email')

    new_user = User(
        name=name,
        email=email,
        age=AgeStatus[age],
        gender=GenderStatus[gender]
        )
    db.session.add(new_user)
    db.session.commit()

#유저생성함수
    if not new_user:
        return jsonify({'message': '이미 존재하는 계정 입니다.'}), 400

    # 유저 정보 반환
    return jsonify({
        'message': f'{new_user.name}님 회원가입을 축하합니다',
        'user_id': new_user.id
    }), 201

    return new_user



# def create_user():
#     data = request.get_json()

#     # 데이터 유효성 검사
#     name = data.get("name")
#     email = data.get("email")
#     age = data.get("age")
#     gender = data.get("gender")

#     missing_fields = []
#     if not name:
#         missing_fields.append("name")
#     if not email:
#         missing_fields.append("email")
#     if not age:
#         missing_fields.append("age")
#     if not gender:
#         missing_fields.append("gender")

#     if missing_fields:
#         abort(400, message=f"다음 필드가 누락되었습니다: {', '.join(missing_fields)}")
#     # 중복 이메일 검사
#     if User.query.filter_by(email=email).first():
#         abort(400, message="이미 사용 중인 이메일입니다.")

#     # 유저 생성
#     try:
#         new_user = User(
#             name=name,
#             email=email,
#             age=AgeStatus[age],
#             gender=GenderStatus[gender],
#         )
#         db.session.add(new_user)
#         db.session.commit()
#         return jsonify({
#             "message": f"{name}님 회원가입을 축하합니다.",
#             "user": new_user.to_dict(),
#         }), 201
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         abort(500, message=f"유저 생성 중 오류가 발생했습니다: {str(e)}")

# #전체 유저 조회
# @users_bp.route("/users", methods=["GET"])
# def get_all_users():
#     try:
#         users = User.query.all()
#         return jsonify([user.to_dict() for user in users]), 200
#     except SQLAlchemyError as e:
#         abort(500, message=f"유저 조회 중 오류가 발생했습니다: {str(e)}")

# #특정 유저 조회
# @users_bp.route("/users/<int:user_id>", methods=["GET"])
# def get_user_by_id(user_id):
#     try:
#         user = User.query.get(user_id)
#         if not user:
#             abort(404, message=f"ID {user_id}의 유저를 찾을 수 없습니다.")
#         return jsonify(user.to_dict()), 200
#     except SQLAlchemyError as e:
#         abort(500, message=f"유저 조회 중 오류가 발생했습니다: {str(e)}")
