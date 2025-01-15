from flask import request, jsonify
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Image, ImageStatus

# Blueprint 생성
images_bp = Blueprint("images", __name__, url_prefix="/image")

@images_bp.route("/main", methods=["GET"])
def get_main_image():

    try:
        # type이 main인 이미지 조회
        main_image = Image.query.filter_by(type=ImageStatus.main).first()
        if not main_image:
            abort(404, message="메인 이미지를 찾을 수 없습니다.")

        # 이미지 URL만 반환
        return jsonify({"image": main_image.url}), 200
    except SQLAlchemyError as e:
        # 데이터베이스 오류 처리
        abort(500, message=f"메인 이미지 조회 중 오류가 발생했습니다: {str(e)}")

@images_bp.route("/", methods=["POST"])
def create_image():
    """새 이미지를 추가합니다"""
    data = request.get_json()
    new_image = Image(url=data["url"], type=data["type"])
    db.session.add(new_image)
    db.session.commit()
    return jsonify({"message": f"ID: {new_image.id} Image Success Create"}), 201

# 특정 이미지 조회
@images_bp.route("/<int:image_id>", methods=["GET"])
def get_image_by_id(image_id):
    """
    특정 이미지를 조회하고 URL만 반환
    """
    try:
        # 이미지 ID로 데이터 조회
        image = Image.query.get(image_id)
        if not image:
            abort(404, message=f"ID {image_id}의 이미지를 찾을 수 없습니다.")
        
        # 이미지 URL만 반환
        return jsonify({"image": image.url}), 200
    except SQLAlchemyError as e:
        # 데이터베이스 오류 처리
        abort(500, message=f"이미지 조회 중 오류가 발생했습니다: {str(e)}")

#이미지 삭제
@images_bp.route("/<int:image_id>", methods=["DELETE"])
def delete_image(image_id):
    try:
        image = Image.query.get(image_id)
        if not image:
            abort(404, message=f"ID {image_id}의 이미지를 찾을 수 없습니다.")
        
        # 이미지 삭제
        db.session.delete(image)
        db.session.commit()
        return jsonify({"message": f"ID {image_id}의 이미지가 삭제되었습니다."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, message=f"이미지 삭제 중 오류가 발생했습니다: {str(e)}")
