import requests
from flask import request, jsonify, abort, Response
from flask_smorest import Blueprint
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Image, ImageStatus

# Blueprint 생성
images_bp = Blueprint("images", __name__, url_prefix="/image")

# 외부 이미지 요청에 필요한 헤더 설정 (프록시를 사용하여 우회 처리)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://oz-flask-form.vercel.app/",
}

@images_bp.route("/main", methods=["GET"])
def get_main_image():
    """
    메인 이미지 조회
    """
    try:
        # type이 main인 이미지 조회
        main_image = Image.query.filter_by(type="main").first()
        if not main_image:
            abort(404, message="메인 이미지를 찾을 수 없습니다.")

        # 외부 이미지를 요청하여 반환 (프록시 방식)
        response = requests.get(main_image.url, headers=HEADERS)

        if response.status_code == 200:
            # 성공적으로 이미지를 불러왔다면 해당 이미지를 반환
            return Response(response.content, content_type="image/jpeg"), 200
        else:
            # 외부 요청 실패 시 에러 반환
            abort(500, message="메인 이미지 요청 중 오류가 발생했습니다.")
    except SQLAlchemyError as e:
        # 데이터베이스 오류 처리
        abort(500, message=f"메인 이미지 조회 중 오류가 발생했습니다: {str(e)}")


@images_bp.route("/<int:image_id>", methods=["GET"])
def get_image_by_id(image_id):
    """
    특정 이미지 조회
    """
    try:
        # 이미지 ID로 데이터 조회
        image = Image.query.get(image_id)
        if not image:
            abort(404, message=f"ID {image_id}의 이미지를 찾을 수 없습니다.")

        # 외부 이미지를 요청하여 반환 (프록시 방식)
        response = requests.get(image.url, headers=HEADERS)

        if response.status_code == 200:
            # 성공적으로 이미지를 불러왔다면 해당 이미지를 반환
            return Response(response.content, content_type="image/jpeg"), 200
        else:
            # 외부 요청 실패 시 에러 반환
            abort(500, message=f"ID {image_id}의 이미지 요청 중 오류가 발생했습니다.")
    except SQLAlchemyError as e:
        # 데이터베이스 오류 처리
        abort(500, message=f"이미지 조회 중 오류가 발생했습니다: {str(e)}")


@images_bp.route("/", methods=["POST"])
def create_image():
    """
    새 이미지를 추가합니다
    """
    data = request.get_json()
    new_image = Image(url=data["url"], type=data["type"])
    db.session.add(new_image)
    db.session.commit()
    return jsonify({"message": f"ID: {new_image.id} Image Success Create"}), 201


@images_bp.route("/<int:image_id>", methods=["DELETE"])
def delete_image(image_id):
    """
    특정 이미지 삭제
    """
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