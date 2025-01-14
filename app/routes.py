from flask import jsonify
from flask_smorest import Blueprint

api_bp = Blueprint('api', __name__)  # 블루프린트 생성

@api_bp.route('/')
def index():
    """
    API 연결 상태 확인
    """
    return jsonify({"message": "Success Connect"}), 200
