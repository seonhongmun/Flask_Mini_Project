from datetime import datetime 
from enum import Enum
from zoneinfo import ZoneInfo

from config import db


KST = ZoneInfo("Asia/Seoul")  # 한국 표준시 설정

class BaseModel(db.Model):  #기본 베이스
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)  #기본키 
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(tz=KST), nullable=False
    )   # 생성시간 저장 
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(tz=KST),
        onupdate=lambda: datetime.now(tz=KST), nullable=False
    )  # 수정시간 저장

class AgeStatus(Enum):  #값 제한 age = teen~fifty 
    teen = "teen"      #10대
    twenty = "twenty"  #20대
    thirty = "thirty"  #30대
    fourty = "fourty"  #40대
    fifty = "fifty"    #50대


class GenderStatus(Enum): #값 제한 gender = male, female
    male = "male"  #남성
    female = "female"  #여성


class ImageStatus(Enum): #값 제한 image = main, sub
    main = "main" #메인 main.html -> 이미지파일
    sub = "sub"  # -> 각 질문의 이미지파일 


class User(BaseModel):  #User (기본모델을 가져옴(상속))
    __tablename__ = "users"  #테이블이름 = users
    name = db.Column(db.String(10), nullable=False) #이름
    age = db.Column(db.Enum(AgeStatus), nullable=False)  #나이(agestatus = 10~50)
    gender = db.Column(db.Enum(GenderStatus), nullable=False)  # 성별(genderstatus = male, female)
    email = db.Column(db.String(120), unique=True, nullable=False)  # 이메일

    def to_dict(self):  #user클래스에서 가져와 id, name, age, gender, email, 생성시간, 수정시간을 json화 
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age.value if hasattr(self.age, "value") else self.age,
            "gender": (
                self.gender.value if hasattr(self.gender, "value") else self.gender
            ),
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class Image(BaseModel):  #image 
    __tablename__ = "images"  #테이블 = images
    url = db.Column(db.TEXT, nullable=False)  #url 주소 text
    type = db.Column(db.Enum(ImageStatus), nullable=False)  #이미지 유형 (image status = main, sub)

    questions = db.relationship("Question", back_populates="image") #Question 테이블 참조 1:N관계 

    def to_dict(self): #images클래스에서 가져와 id, url, type, 생성시간, 수정시간을 json화
        return {
            "id": self.id,
            "url": self.url,
            "type": self.type.value if hasattr(self.type, "value") else self.type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Question(BaseModel): #Question
    __tablename__ = "questions"  #테이블 = question
    title = db.Column(db.String(100), nullable=False)  #질문
    is_active = db.Column(db.Boolean, nullable=False, default=True) #활성여부? 질문활성, 비활성?
    sqe = db.Column(db.Integer, nullable=False)  #질문순서

    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), nullable=False)  #image테이블 id와 foreignkey 관계 not null

    image = db.relationship("Image", back_populates="questions") #image테이블 참조 1:N관계 

    def to_dict(self):  #Question테이블에서 가져와 id, title, 활성상태, 순서, image, 생성시간, 수정시간 json화 
        return {
            "id": self.id,
            "title": self.title,
            "is_active": self.is_active,
            "sqe": self.sqe,
            "image": self.image.to_dict() if self.image else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Choices(BaseModel): #Choices
    __tablename__ = "choices" #테이블 choices
    content = db.Column(db.Text, nullable=False)  #선택내용
    is_active = db.Column(db.Boolean, nullable=False, default=True)  #활성여부?
    sqe = db.Column(db.Integer, nullable=False) #순서

    question_id = db.Column(db.Integer, db.ForeignKey("questions.id")) #Question테이블 id와 foreignkey관계 

    def to_dict(self):  #choices테이블에서 가져와 id, content, 활성상태, 순서, 질문id, 생성시간, 수정시간 json화 
        return {
            "id": self.id,
            "content": self.content,
            "is_active": self.is_active,
            "sqe": self.sqe,
            "question_id": self.question_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Answer(BaseModel):  #Answer
    __tablename__ = "answers" #테이블 = answers
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  #user_id와 Foreignkey관게
    choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"))  #choice_id와 Foreignkey관계

    def to_dict(self):  #Answer테이블에서 가져와 id, user_id, choice_id, 생성시간, 수정시간 json화 
        return {
            "id": self.id,
            "user_id": self.user_id,
            "choice_id": self.choice_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }