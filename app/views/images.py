from flask import Blueprint, request, jsonify #블루프린트, 리퀘스트, jsonify 불러오기
from app.models import db, Image  # 데이터베이스 객체와 테이블
from sqlalchemy.exc import SQLAlchemyError #데이터베이스 Errormessage 출력

images_bp = Blueprint('images', __name__)  # 일반 사용자용 블루프린트

@images_bp.route('/images', methods=['POST'])  # POST 요청으로 이미지 생성
def create_image():
    data = request.json  # 요청에서 JSON 데이터를 가져옴
    url = data.get('url')  # URL 추출
    image_type = data.get('image_type')  # 이미지 유형 추출

    if not url or not isinstance(url, str):  # URL 검증
        return jsonify({"error": "유효하지 않은 URL입니다."}), 400
    if image_type not in {"main", "sub"}:  # 이미지 유형 검증
        return jsonify({"error": f"유효하지 않은 이미지 유형입니다: {image_type}"}), 400

    try:
        new_image = Image(url=url, type=image_type)  # 새로운 이미지 객체 생성
        db.session.add(new_image)  # 데이터베이스에 추가
        db.session.commit()  # 커밋하여 저장
        return jsonify(new_image.to_dict()), 201  # 성공적으로 생성된 이미지 반환
    except SQLAlchemyError:  # 데이터베이스 오류 처리
        db.session.rollback()  # 트랜잭션 롤백
        return jsonify({"error": "이미지 생성 중 오류가 발생했습니다."}), 500

@images_bp.route('/images/<int:image_id>', methods=['GET'])  # GET 요청으로 특정 이미지 조회
def get_image(image_id):
    image = Image.query.get(image_id)  # ID로 이미지 조회
    if not image:  # 이미지가 없을 경우
        return jsonify({"error": f"ID {image_id}에 해당하는 이미지를 찾을 수 없습니다."}), 404
    return jsonify(image.to_dict()), 200  # 이미지 데이터 반환

@images_bp.route('/images', methods=['GET'])  # GET 요청으로 모든 이미지 조회
def get_all_images():
    images = Image.query.all()  # 모든 이미지 조회
    return jsonify([image.to_dict() for image in images]), 200  # JSON 리스트 반환

@images_bp.route('/images/<int:image_id>', methods=['PUT'])  # PUT 요청으로 이미지 업데이트
def update_image(image_id):
    image = Image.query.get(image_id)  # ID로 이미지 조회
    if not image:  # 이미지가 없을 경우
        return jsonify({"error": f"ID {image_id}에 해당하는 이미지를 찾을 수 없습니다."}), 404

    data = request.json  # 요청 데이터 추출
    url = data.get('url')  # URL 추출
    image_type = data.get('image_type')  # 이미지 유형 추출

    if url:  # URL이 제공되었을 경우
        if not isinstance(url, str):  # URL 검증
            return jsonify({"error": "유효하지 않은 URL입니다."}), 400
        image.url = url  # URL 업데이트

    if image_type:  # 이미지 유형이 제공되었을 경우
        if image_type not in {"main", "sub"}:  # 이미지 유형 검증
            return jsonify({"error": f"유효하지 않은 이미지 유형입니다: {image_type}"}), 400
        image.type = image_type  # 이미지 유형 업데이트

    try:
        db.session.commit()  # 변경 사항 저장
        return jsonify(image.to_dict()), 200  # 업데이트된 이미지 반환
    except SQLAlchemyError:  # 오류 처리
        db.session.rollback()  # 트랜잭션 롤백
        return jsonify({"error": "이미지 업데이트 중 오류가 발생했습니다."}), 500

@images_bp.route('/images/<int:image_id>', methods=['DELETE'])  # DELETE 요청으로 이미지 삭제
def delete_image(image_id):
    image = Image.query.get(image_id)  # ID로 이미지 조회
    if not image:  # 이미지가 없을 경우
        return jsonify({"error": f"ID {image_id}에 해당하는 이미지를 찾을 수 없습니다."}), 404

    try:
        db.session.delete(image)  # 이미지 삭제
        db.session.commit()  # 변경 사항 저장
        return jsonify({"message": f"이미지 ID {image_id}가 성공적으로 삭제되었습니다."}), 200  # 성공 메시지 반환
    except SQLAlchemyError:  # 오류 처리
        db.session.rollback()  # 트랜잭션 롤백
        return jsonify({"error": "이미지 삭제 중 오류가 발생했습니다."}), 500
