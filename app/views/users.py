from flask import request
from app.models import User, AgeStatus, GenderStatus, db

def create_user(username, age, gender, email):
    '''
    유저 생성 및 데이터베이스 저장 함수

    - username (str): 유저 이름
    - age (str): 나이대 ('teen', 'twenty', 'thirty', 'fourty', 'fifty')
    - gender (str): 성별 ('male', 'female')
    - email (str): 이메일 주소

    '''
    if age not in AgeStatus._value2member_map_:
        raise ValueError(f"잘못된 나이 값입니다. 허용 가능한 값: {list(AgeStatus._value2member_map_.keys())}")
    if gender not in GenderStatus._value2member_map_:
        raise ValueError(f"잘못된 성별 값입니다. 허용 가능한 값: {list(GenderStatus._value2member_map_.keys())}")

    new_user = User(name=username, age=AgeStatus(age), gender=GenderStatus(gender), email=email)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def register_user():

    try:
        data = request.form

        if not all(key in data for key in ('username', 'age', 'gender', 'email')):
            return "필수 필드가 누락되었습니다.", 400

        new_user = create_user(data['username'], data['age'], data['gender'], data['email'])
        return f"유저가 성공적으로 등록되었습니다. ID: {new_user.id}, 이름: {new_user.name}", 201

    except ValueError as ve:
        return str(ve), 400
    except Exception as e:
        return f"오류: {str(e)}", 500

def get_user_by_id(user_id):
    '''
    유저 조회 함수

    - user_id (int): 조회할 유저의 ID

    '''
    try:
        user = User.query.get(user_id)
        if not user:
            return f"ID {user_id}의 유저를 찾을 수 없습니다.", 404

        return f"유저 ID: {user.id}, 이름: {user.name}, 나이: {user.age.value}, 성별: {user.gender.value}, 이메일: {user.email}", 200

    except Exception as e:
        return f"오류: {str(e)}", 500
