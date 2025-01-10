from app import create_app  #app파일에서 create_app 함수 가져옴

application = create_app()  #가져온 함수를 실행하여 객체 생성하여 application에 저장

if __name__ == "__main__":  # flask 실행 app.run(디버그 기능 켬) 
    application.run(debug=True)

