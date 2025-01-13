from config import db   # config 모듈에서 db 객체 가져옴
from flask import Flask  # flask 클래스에서 애플리케이션 객제 가져옴
from flask_migrate import Migrate  # 데이터베이스 마이그레이션 도구로 데이터베이스 스키마 변경기능


import app.models  # models에서 정의된 모델을 가져옴

migrate = Migrate()  # 마이그레이션 객체 생성 애플리케이션과 데이터베이스 초기화진행


def create_app():  # create 함수 정의 
    application = Flask(__name__)  # flask 인스턴스 생성

    # config클래스 속성을 사용해 설정 (데이터베이스URl, 디버그 옵션, 기타 설정)
    application.config.from_object("config.Config") 
    application.secret_key = "oz_form_secret" # 비밀키 설정 

    db.init_app(application)  #db를 flask에 연결

    migrate.init_app(application, db) # 마이그레이션을 flask에 연결
    from app.views.images import images_bp
    # 블루 프린트 등록
    application.register_blueprint(images_bp, url_prefix='/api')

    return application  #flask 객체 반환

