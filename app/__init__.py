from config import db, api  # 데이터베이스와 API 객체 가져오기
from flask import Flask  # Flask 애플리케이션 객체
from flask_migrate import Migrate  # 데이터베이스 마이그레이션 도구

migrate = Migrate()  # 마이그레이션 객체 생성


def create_app():
    """
    Flask 애플리케이션 생성 및 초기화 함수
    """
    app = Flask(__name__)  # Flask 애플리케이션 인스턴스 생성

    # Flask 설정
    app.config.from_object("config.Config")  # config.py에서 설정 로드
    app.secret_key = "oz_form_secret"  # 비밀키 설정

    # OpenAPI 및 Swagger UI 설정
    app.config['API_TITLE'] = 'oz_form'
    app.config['API_VERSION'] = '1.0'
    app.config['OPENAPI_VERSION'] = '3.1.3'
    app.config['OPENAPI_URL_PREFIX'] = '/'  # OpenAPI 문서의 기본 URL
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # 확장 초기화
    db.init_app(app)  # SQLAlchemy 데이터베이스 초기화
    api.init_app(app)  # Flask-Smorest API 초기화
    migrate.init_app(app, db)  # Flask-Migrate 초기화

    # 블루프린트 가져오기 및 등록
    from app.views.images import images_bp
    from app.views.questions import questions_bp
    from app.views.users import users_bp

    app.register_blueprint(images_bp, url_prefix='/images')  # 이미지 관련 API
    app.register_blueprint(questions_bp, url_prefix='/questions')  # 질문 관련 API
    app.register_blueprint(users_bp, url_prefix='/users')  # 사용자 관련 API

    return app  # 생성된 Flask 애플리케이션 반환