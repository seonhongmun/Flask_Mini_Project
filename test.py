from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:8573@localhost/flask_mini_project")
try:
    connection = engine.connect()
    print("데이터베이스 연결 성공!")
except Exception as e:
    print(f"데이터베이스 연결 실패: {e}")