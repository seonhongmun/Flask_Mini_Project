from flask import request, jsonify
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, User, AgeStatus, GenderStatus

# Blueprint 생성
users_bp = Blueprint("users", __name__)

# 유저 생성/signup
@users_bp.route("/signup", methods=["POST"])
def signup():
    try:
        # 요청 데이터 받아오기
        data = request.json

        # 요청 데이터에서 필드 추출
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        email = data.get('email')

        # 필수 필드 유효성 검사
        if not name or not age or not gender or not email:
            return jsonify({'message': '모든 필드는 필수 항목입니다.'}), 400

        # 이메일 중복 체크
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': '이미 존재하는 계정입니다.'}), 400

        # AgeStatus와 GenderStatus Enum 값 유효성 검사
        try:
            age_status = AgeStatus[age]  # 유효하지 않은 age 값이면 KeyError 발생
            gender_status = GenderStatus[gender]  # 유효하지 않은 gender 값이면 KeyError 발생
        except KeyError as e:
            return jsonify({'message': f'유효하지 않은 값입니다: {str(e)}'}), 400

        # 새로운 유저 생성
        new_user = User(
            name=name,
            email=email,
            age=age_status,
            gender=gender_status
        )
        db.session.add(new_user)  # 세션에 추가
        db.session.commit()  # 데이터베이스에 커밋

        # 성공 메시지 반환
        return jsonify({
            'message': f'{new_user.name}님 회원가입을 축하합니다.',
            'user_id': new_user.id
        }), 201

    except SQLAlchemyError as e:
        # 데이터베이스 관련 오류 처리
        db.session.rollback()  # 트랜잭션 롤백
        return jsonify({'message': f'데이터베이스 오류가 발생했습니다: {str(e)}'}), 500

    except Exception as e:
        # 그 외 예상치 못한 오류 처리
        return jsonify({'message': f'예상치 못한 오류가 발생했습니다: {str(e)}'}), 500

#전체 유저 조회
@users_bp.route("/users", methods=["GET"])
def get_all_users():
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except SQLAlchemyError as e:
        abort(500, message=f"유저 조회 중 오류가 발생했습니다: {str(e)}")

#특정 유저 조회
@users_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            abort(404, message=f"ID {user_id}의 유저를 찾을 수 없습니다.")
        return jsonify(user.to_dict()), 200
    except SQLAlchemyError as e:
        abort(500, message=f"유저 조회 중 오류가 발생했습니다: {str(e)}")

    return new_user
