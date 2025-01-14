from flask import jsonify, request  # Flask 모듈 가져오기
from flask_smorest import Blueprint
from app.models import db, Image, ImageStatus  # 데이터베이스 모델 및 열거형 상태 가져오기
from sqlalchemy.exc import SQLAlchemyError  # 데이터베이스 예외 처리

# Blueprint 생성
images_bp = Blueprint("images", __name__, url_prefix="/images")

# 모든 이미지 조회
@images_bp.route("/", methods=["GET"])
def get_all_images():
    """
    모든 이미지를 조회합니다.
    """
    try:
        images = Image.query.all()  # 데이터베이스에서 모든 이미지 가져오기
        # 각 이미지 데이터를 JSON 형식으로 변환
        result = [
            {
                "id": image.id,
                "url": image.url,
                "type": image.type.value,
                "created_at": image.created_at.isoformat(),
                "updated_at": image.updated_at.isoformat()
            }
            for image in images
        ]
        return jsonify(result), 200  # JSON 응답 반환
    except Exception as e:
        return jsonify({"error": f"이미지 조회 중 오류가 발생했습니다: {str(e)}"}), 500


# 새로운 이미지 생성
@images_bp.route("/", methods=["POST"])
def create_image():
    """
    새 이미지를 생성합니다.
    """
    try:
        data = request.json  # 클라이언트 요청 데이터 가져오기

        # 필수 필드 확인
        if "url" not in data or "type" not in data:
            return jsonify({"error": "필수 필드가 누락되었습니다. 'url'과 'type'을 입력하세요."}), 400

        # 이미지 유형 유효성 확인
        if data["type"] not in ImageStatus._value2member_map_:
            return jsonify({"error": f"유효하지 않은 이미지 유형입니다: {data['type']}. 허용된 값: main, sub"}), 400

        # 새 이미지 객체 생성
        new_image = Image(
            url=data["url"],
            type=ImageStatus(data["type"])
        )
        db.session.add(new_image)  # 데이터베이스에 추가
        db.session.commit()  # 변경 사항 저장

        # 성공적으로 생성된 이미지 반환
        return jsonify({
            "id": new_image.id,
            "url": new_image.url,
            "type": new_image.type.value,
            "created_at": new_image.created_at.isoformat(),
            "updated_at": new_image.updated_at.isoformat()
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()  # 데이터베이스 오류 발생 시 롤백
        return jsonify({"error": f"이미지 생성 중 오류가 발생했습니다: {str(e)}"}), 500


# 특정 이미지 조회
@images_bp.route("/<int:image_id>", methods=["GET"])
def get_image_by_id(image_id):
    """
    특정 ID의 이미지를 조회합니다.
    """
    try:
        image = Image.query.get(image_id)  # ID로 이미지 검색
        if not image:  # 이미지가 없으면 404 반환
            return jsonify({"error": f"ID {image_id}에 해당하는 이미지를 찾을 수 없습니다."}), 404

        # 이미지 데이터 반환
        return jsonify({
            "id": image.id,
            "url": image.url,
            "type": image.type.value,
            "created_at": image.created_at.isoformat(),
            "updated_at": image.updated_at.isoformat()
        }), 200

    except Exception as e:
        return jsonify({"error": f"이미지 조회 중 오류가 발생했습니다: {str(e)}"}), 500


# 특정 이미지 삭제
@images_bp.route("/<int:image_id>", methods=["DELETE"])
def delete_image(image_id):
    """
    특정 ID의 이미지를 삭제합니다.
    """
    try:
        image = Image.query.get(image_id)  # ID로 이미지 검색
        if not image:  # 이미지가 없으면 404 반환
            return jsonify({"error": f"ID {image_id}에 해당하는 이미지를 찾을 수 없습니다."}), 404

        db.session.delete(image)  # 이미지 삭제
        db.session.commit()  # 변경 사항 저장
        return jsonify({"message": f"ID {image_id}의 이미지가 성공적으로 삭제되었습니다."}), 200

    except SQLAlchemyError as e:
        db.session.rollback()  # 데이터베이스 오류 발생 시 롤백
        return jsonify({"error": f"이미지 삭제 중 오류가 발생했습니다: {str(e)}"}), 500