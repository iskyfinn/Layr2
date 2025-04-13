from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'Layr API is alive!'})
