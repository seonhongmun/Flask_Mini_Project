from flask import Blueprint, request, jsonify
from app.views import users, questions, choices, answers, images, answers

api = Blueprint('api', __name__)  # 블루프린트 생성

# 유저 관련 라우트
@api.route('/users', methods=['POST'])  #사용사 생성 
def create_user_route():
    data = request.json # post한 정보를 data변수에 담는다.
    user = users.create_user(data['name'], data['email']) 
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})
    #생성된 사용자 정보를 json하여 반환한다. 

@api.route('/users/<int:user_id>', methods=['GET'])
def get_user_route(user_id):
    user = users.get_user(user_id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})
    #user_id를 기반으로 특정 사용자 정보를 조회한다.

# 질문 관련 라우트
@api.route('/questions', methods=['POST'])
def create_question_route():
    data = request.json
    question = questions.create_question(data['text'])
    return jsonify({'id': question.id, 'text': question.text})
    #생성된 질문을 json하여 반환한다. 
    
@api.route('/questions/<int:question_id>/choices', methods=['POST'])
def create_choice_route(question_id):
    data = request.json
    choice = choices.create_choice(question_id, data['text'])
    return jsonify({'id': choice.id, 'text': choice.text})
    #question_id를 기반으로 선택 항목을 생성한다? 

@api.route('/answers', methods=['POST'])
def create_answer_route():
    data = request.json
    answer = answers.create_answer(data['user_id'], data['choice_id'])
    return jsonify({'id': answer.id, 'user_id': answer.user_id, 'choice_id': answer.choice_id})
    #생성된 답변 정보를 json하여 반환한다. 