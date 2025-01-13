from flask_smorest import Blueprint
from flask.views import MethodView
from marshmallow import Schema, fields
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Image, ImageStatus

# Blueprint 생성 - 이미지 관련 API 관리
images_bp = Blueprint("images", __name__, url_prefix="/images")

# 요청 및 응답에 사용될 스키마 정의
class ImageRequestSchema(Schema):
    """요청 데이터를 검증하는 스키마"""
    url = fields.String(required=True, description="이미지 URL")
    type = fields.String(
        required=True,
        validate=lambda x: x in ImageStatus._value2member_map_,
        description="이미지 유형 (main/sub)"
    )


class ImageResponseSchema(Schema):
    """단일 이미지 응답 스키마"""
    id = fields.Integer(description="이미지 ID")
    url = fields.String(description="이미지 URL")
    type = fields.String(description="이미지 유형 (main/sub)")
    created_at = fields.DateTime(description="생성 시간")
    updated_at = fields.DateTime(description="수정 시간")


class ImageListResponseSchema(Schema):
    """이미지 목록 응답 스키마"""
    images = fields.List(fields.Nested(ImageResponseSchema), description="이미지 목록")


# API 엔드포인트 정의
@images_bp.route("/")
class Images(MethodView):
    @images_bp.response(200, ImageListResponseSchema)
    def get(self):
        """
        모든 이미지 조회
        """
        images = Image.query.all()  # 데이터베이스에서 모든 이미지 가져오기
        return {"images": [image.to_dict() for image in images]}  # JSON 형태로 반환

    @images_bp.arguments(ImageRequestSchema)
    @images_bp.response(201, ImageResponseSchema)
    def post(self, data):
        """
        이미지 생성
        """
        try:
            # 새 이미지 객체 생성
            new_image = Image(
                url=data["url"],  # 요청 데이터에서 URL 가져오기
                type=ImageStatus(data["type"])  # 요청 데이터에서 유형 가져오기
            )
            db.session.add(new_image)  # 데이터베이스에 추가
            db.session.commit()  # 변경 사항 저장
            return new_image.to_dict()  # 생성된 이미지 데이터 반환

        except SQLAlchemyError as e:
            db.session.rollback()  # 트랜잭션 롤백
            return {"message": "이미지 생성 중 오류가 발생했습니다.", "details": str(e)}, 500  # 오류 응답


@images_bp.route("/<int:image_id>")
class ImageDetail(MethodView):
    @images_bp.response(200, ImageResponseSchema)
    def get(self, image_id):
        """
        특정 이미지 조회
        """
        image = Image.query.get(image_id)  # ID로 이미지 검색
        if not image:  # 이미지가 없으면
            return {"message": f"ID {image_id}에 해당하는 이미지를 찾을 수 없습니다."}, 404
        return image.to_dict()  # 이미지 데이터 반환

    def delete(self, image_id):
        """
        특정 이미지 삭제
        """
        image = Image.query.get(image_id)  # ID로 이미지 검색
        if not image:  # 이미지가 없으면
            return {"message": f"ID {image_id}에 해당하는 이미지를 찾을 수 없습니다."}, 404

        try:
            db.session.delete(image)  # 이미지 삭제
            db.session.commit()  # 변경 사항 저장
            return {"message": f"ID {image_id}의 이미지가 성공적으로 삭제되었습니다."}, 200

        except SQLAlchemyError as e:
            db.session.rollback()  # 트랜잭션 롤백
            return {"message": "이미지 삭제 중 오류가 발생했습니다.", "details": str(e)}, 500