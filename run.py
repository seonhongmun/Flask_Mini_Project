from app import create_app  #app파일에서 create_app 함수 가져옴
from config import db

app = create_app()  #가져온 함수를 실행하여 객체 생성하여 application에 저장

with app.app_context():
    db.create_all()  # db schema 생성
    print("Initialized the database.")

if __name__ == "__main__":  # flask 실행 app.run(디버그 기능 켬) 
    app.run(debug=True, port=5001)

