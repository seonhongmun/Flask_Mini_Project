from app.models import db, Image  # 데이터베이스 객체와 테이블
from sqlalchemy.exc import SQLAlchemyError  # 데이터베이스 작업 중 발생하는 오류를 처리


class ImagesService:
    image_types = {"main", "sub"}  # 유효한 이미지 유형

    @staticmethod
    def create_image(url, image_type):  #새로운 이미지 생성
        if not url or not isinstance(url, str):  # url이 아니거나 문자열이 아닌경우 ValueError출력
            raise ValueError("유효하지 않은 URL입니다.")
        if image_type not in ImagesService.image_types:  #imagetype이 main, sub가 아니면 ValueError출력
            raise ValueError(f"유효하지 않은 이미지 유형입니다: {image_type}")

        try:
            new_image = Image(url=url, type=image_type) #url, imagetype을 new_image 변수에 저장
            db.session.add(new_image)  #데이터베이스 세션이 추가 
            db.session.commit()         #데이터베이스 세션을 커밋하여 저장
            return new_image  #new_image를 반환
        except SQLAlchemyError:   #작업에 오류가 생길경우 
            db.session.rollback()   #데이터베이스 세션을 되돌린다.
            raise RuntimeError("이미지 생성 중 오류가 발생했습니다.")  #에러를 반환

    @staticmethod
    def get_image(image_id): #이미지 조회 
        return Image.query.get(image_id)   # image_id를 기준으로 이미지 조회

    @staticmethod
    def get_all_images():
        images = Image.query.all()  #모든 이미지 조회 
        return [image.to_dict() for image in images]  #전체 이미지 조회
    
    @staticmethod
    def update_image(image_id, url=None, image_type=None): #이미지 업데이트 (url, imagetype을 수정)
        image = Image.query.get(image_id)  #image_id 기준으로 이미지를 조회한다.
        if not image:
            return None   #이미지가 없으면 None반환

        if url:  #url이 들어오면 
            if not isinstance(url, str):  #url이 문자열이 아니면 Error출력
                raise ValueError("유효하지 않은 URL입니다.")
            image.url = url #받은 url을 image.url에 업데이트 한다.

        if image_type:
            if image_type not in ImagesService.image_types: #이미지 타입이 main, sub가 아니면 Error출력
                raise ValueError(f"유효하지 않은 이미지 유형입니다: {image_type}")
            image.type = image_type #받은 image_type을 image.type에 업데이트 한다.

        try:  #변경사항을 커밋하고 이미지를 반환한다. 
            db.session.commit()
            return image
        except SQLAlchemyError:    #작업에 오류가 생길경우 
            db.session.rollback()    #데이터베이스 세션을 되돌린다.
            raise RuntimeError("이미지 업데이트 중 오류가 발생했습니다.") #오류출력

    @staticmethod
    def delete_image(image_id): #이미지 삭제 
        image = Image.query.get(image_id) #image_id를 기준으로 이미지를 조회한다.
        if not image:  #이미지가 아니면 None값 반환
            return None

        try:
            db.session.delete(image) #이미지를 삭제한다.
            db.session.commit()  #데이터베이스 를 커밋한다.
            return image      #이미지를 반환한다.
        except SQLAlchemyError:  #작업에 오류가 생길경우 
            db.session.rollback()    #데이터베이스 세션을 되돌린다.
            raise RuntimeError("이미지 삭제 중 오류가 발생했습니다.") #오류출력
        

class AdminImagesService(ImagesService):

    @staticmethod
    def admin_get_image(image_id): #관리자전용 이미지 조회
        image = Image.query.get(image_id)  # 주어진 ID로 이미지를 조회
        if not image:
            raise ValueError(f"ID {image_id}에 해당하는 이미지를 찾을 수 없습니다.")  # 이미지가 없을 경우 예외 발생
        return image.to_dict()  # 이미지 데이터를 딕셔너리 형태로 반환

    @staticmethod
    def admin_get_all_images(): #관리자전용 모든 이미지 조회
        images = Image.query.all()  # 모든 이미지 데이터를 조회
        return [image.to_dict() for image in images]  # 이미지 리스트를 JSON 형식으로 변환

    @staticmethod
    def admin_update_image(image_id, url=None, image_type=None): #관리자전용 특정이미지 업데이트
        image = Image.query.get(image_id)  # 주어진 ID로 이미지를 조회
        if not image:
            raise ValueError(f"ID {image_id}에 해당하는 이미지를 찾을 수 없습니다.")  # 이미지가 없을 경우 예외 발생

        if url:  # URL이 제공된 경우
            if not isinstance(url, str):  # URL이 문자열인지 확인
                raise ValueError("유효하지 않은 URL입니다.")  # URL이 아니거나 문자열이 아닌 경우 ValueError 출력
            image.url = url  # URL 업데이트

        if image_type:  # 이미지 유형이 제공된 경우
            if image_type not in ImagesService.VALID_IMAGE_TYPES:  # 유효한 이미지 유형인지 확인
                raise ValueError(f"유효하지 않은 이미지 유형입니다: {image_type}")  # 유효하지 않은 유형일 경우 예외 발생
            image.type = image_type  # 이미지 유형 업데이트

        try:
            db.session.commit()  # 변경 사항 커밋
            return image.to_dict()  # 업데이트된 이미지 데이터를 반환
        except SQLAlchemyError:
            db.session.rollback()  # 오류 발생 시 롤백
            raise RuntimeError("이미지 업데이트 중 오류가 발생했습니다.")  # 오류 메시지 출력

    @staticmethod
    def admin_delete_image(image_id): #관리자전용 특정이미지 삭제
        image = Image.query.get(image_id)  # 주어진 ID로 이미지를 조회
        if not image:
            raise ValueError(f"ID {image_id}에 해당하는 이미지를 찾을 수 없습니다.")  # 이미지가 없을 경우 예외 발생

        try:
            db.session.delete(image)  # 이미지 삭제
            db.session.commit()  # 변경 사항 커밋
            return {"message": f"이미지 ID {image_id}가 성공적으로 삭제되었습니다."}  # 성공 메시지 반환
        except SQLAlchemyError:
            db.session.rollback()  # 오류 발생 시 롤백
            raise RuntimeError("이미지 삭제 중 오류가 발생했습니다.")  # 오류 메시지 출력

    @staticmethod
    def admin_bulk_delete_images(image_ids): #관리자전용 여러개의 이미지 삭제
        try:
            images = Image.query.filter(Image.id.in_(image_ids)).all()  # 주어진 ID 리스트에 해당하는 이미지 조회
            if not images:
                raise ValueError("삭제할 이미지가 없습니다.")  # 삭제할 이미지가 없을 경우 예외 발생

            for image in images:  # 각 이미지를 순회하며 삭제
                db.session.delete(image)

            db.session.commit()  # 변경 사항 커밋
            return {"message": f"{len(images)}개의 이미지가 성공적으로 삭제되었습니다."}  # 성공적으로 삭제된 이미지 개수 반환
        except SQLAlchemyError:
            db.session.rollback()  # 오류 발생 시 롤백
            raise RuntimeError("여러개의 이미지를 삭제하는 중 오류가 발생했습니다.")  # 오류 메시지 출력
