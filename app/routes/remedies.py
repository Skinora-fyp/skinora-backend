import json
from flask import Blueprint, request, jsonify
from ..models.remedy import Remedy
from ..services.recommendation_engine import get_remedies
from ..utils import token_required

remedies_bp = Blueprint('remedies', __name__)
@remedies_bp.route('', methods=['GET'])
@token_required
def list_remedies(current_user):
    final_condition = request.args.get('final_condition', '').strip()
    if not final_condition:
        return jsonify({'error': 'final_condition query parameter is required'}), 400
    lifestyle = {}
    lifestyle_raw = request.args.get('lifestyle', '')
    if lifestyle_raw:
        try:
            lifestyle = json.loads(lifestyle_raw)
        except (ValueError, TypeError):
            pass
    remedies = get_remedies(final_condition, lifestyle)
    return jsonify({'remedies': remedies, 'final_condition': final_condition}), 200

@remedies_bp.route('/<int:remedy_id>', methods=['GET'])
@token_required
def get_remedy(current_user, remedy_id):
    remedy = db.session.get(Remedy, remedy_id)
    if not remedy:
        return jsonify({'error': 'Remedy not found'}), 404
    return jsonify(remedy.to_dict()), 200

from ..extensions import db  
