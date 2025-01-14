from flask import request, jsonify
from flask_smorest import Blueprint
from app.models import User, AgeStatus, GenderStatus, db

# 사용자 관련 API를 위한 Blueprint 생성
users_bp = Blueprint('user', __name__, url_prefix='/users')


def create_user(username: str, age: str, gender: str, email: str) -> User:
    """
    유저 생성 및 데이터베이스 저장 함수

    - username (str): 유저 이름
    - age (str): 나이대 ('teen', 'twenty', 'thirty', 'fourty', 'fifty')
    - gender (str): 성별 ('male', 'female')
    - email (str): 이메일 주소
    """
    # 나이 값 검증
    if age not in AgeStatus._value2member_map_:
        raise ValueError(f"잘못된 나이 값입니다. 허용 가능한 값: {list(AgeStatus._value2member_map_.keys())}")

    # 성별 값 검증
    if gender not in GenderStatus._value2member_map_:
        raise ValueError(f"잘못된 성별 값입니다. 허용 가능한 값: {list(GenderStatus._value2member_map_.keys())}")

    # 새로운 사용자 생성
    new_user = User(
        name=username,
        age=AgeStatus(age),
        gender=GenderStatus(gender),
        email=email
    )

    # 데이터베이스에 추가 및 저장
    db.session.add(new_user)
    db.session.commit()

    return new_user


@users_bp.route('', methods=['POST'])
def register_user():
    """
    사용자 등록 API
    """
    try:
        # 요청 데이터 가져오기 (JSON 형식)
        data = request.json

        # 필수 필드 확인
        required_fields = ['username', 'age', 'gender', 'email']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "error": "필수 필드가 누락되었습니다.",
                "missing_fields": missing_fields
            }), 400

        # 사용자 생성
        new_user = create_user(
            username=data['username'],
            age=data['age'],
            gender=data['gender'],
            email=data['email']
        )

        # 성공 응답 반환
        return jsonify({
            "message": "유저가 성공적으로 등록되었습니다.",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "age": new_user.age.value,
                "gender": new_user.gender.value,
                "email": new_user.email
            }
        }), 201

    except ValueError as ve:
        # 유효성 검증 실패
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        # 기타 오류 처리
        return jsonify({"error": f"오류: {str(e)}"}), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id: int):
    """
    특정 유저 조회 API
    - user_id (int): 조회할 유저의 ID
    """
    try:
        # 데이터베이스에서 유저 조회
        user = User.query.get(user_id)

        # 유저가 존재하지 않을 경우
        if not user:
            return jsonify({"error": f"ID {user_id}의 유저를 찾을 수 없습니다."}), 404

        # 성공적으로 유저 데이터 반환
        return jsonify({
            "user": {
                "id": user.id,
                "name": user.name,
                "age": user.age.value,
                "gender": user.gender.value,
                "email": user.email
            }
        }), 200

    except Exception as e:
        # 기타 오류 처리
        return jsonify({"error": f"오류: {str(e)}"}), 500