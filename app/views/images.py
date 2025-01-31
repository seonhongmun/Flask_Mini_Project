import requests
from flask import request, jsonify, abort, Response
from flask_smorest import Blueprint
from sqlalchemy.exc import SQLAlchemyError
from flask.views import MethodView
from app.models import db, Image, ImageStatus

# Blueprint 생성
images_bp = Blueprint("images", __name__, url_prefix="/image")

@images_bp.route("/main", methods=["GET"])
def get_main_image():
    """
    메인 이미지를 조회
    """
    # type이 main인 이미지 조회
    main_image = Image.query.filter_by(type=ImageStatus.main).first()
    if not main_image:
        abort(404, description="메인 이미지를 찾을 수 없습니다.")
    return jsonify({"image":main_image.url}), 200


@images_bp.route("/<int:image_id>", methods=["GET"])
def get_image_by_id(image_id):
    """
    특정 이미지를 조회하고, Flask가 중계(proxy)하도록 설정
    """
    try:
        # 이미지 ID로 데이터 조회
        image = Image.query.get(image_id)
        if not image:
            abort(404, description=f"ID {image_id}의 이미지를 찾을 수 없습니다.")
        
        # 외부 이미지 요청을 Flask가 중계
        return proxy_image(image.url)
    except SQLAlchemyError as e:
        abort(500, description=f"이미지 조회 중 오류가 발생했습니다: {str(e)}")


def proxy_image(image_url):
    """
    외부 이미지 URL을 Flask가 중계하여 반환
    """
    try:
        # 외부 URL로 이미지 요청
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            # 성공 시 이미지 데이터를 반환
            return Response(
                response.content,
                content_type=response.headers.get("Content-Type"),
                status=response.status_code
            )
        else:
            abort(502, description="외부 서버에서 이미지를 가져오는 데 실패했습니다.")
    except requests.exceptions.RequestException as e:
        abort(502, description=f"이미지 요청 중 오류가 발생했습니다: {str(e)}")

#이미지 생성
@images_bp.route("/", methods=["POST"])
def create_image():
    data = request.get_json()
    url = data.get("url")
    image_type = data.get("type")

    # 데이터 유효성 검사
    if not url or not image_type:
        abort(400, message="url과 type은 필수 필드입니다.")
    if image_type not in ImageStatus.__members__:
        abort(400, message=f"유효하지 않은 이미지 유형입니다: {image_type}")

    try:
        # 새 이미지 생성
        new_image = Image(url=url, type=ImageStatus[image_type])
        db.session.add(new_image)
        db.session.commit()
        return jsonify({
            "message": f"ID {new_image.id} 이미지가 성공적으로 생성되었습니다.",
            "image": new_image.to_dict(),
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, message=f"이미지 생성 중 오류가 발생했습니다: {str(e)}")

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
