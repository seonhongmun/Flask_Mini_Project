from flask_sqlalchemy import SQLAlchemy #데이터베이스, 파이썬 객체 매핑

db = SQLAlchemy()  #db 객체 초기화(생성)

# 데베 설정
class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:8573@localhost/flask_mini_project"  #root:데이터베이스비밀번호@localhost/스키마이름
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 5
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_MAX_OVERFLOW = 5
    SQLALCHEMY_ECHO = False
    reload = True

