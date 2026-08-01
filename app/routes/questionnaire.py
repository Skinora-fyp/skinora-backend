from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.question import Question
from ..models.questionnaire_response import QuestionnaireResponse
from ..models.detection import Detection
from ..services.questionnaire_engine import (
    summarize_lifestyle, generate_advices, calculate_validation_score
)
from ..utils import token_required

questionnaire_bp = Blueprint('questionnaire', __name__)


@questionnaire_bp.route('/questions', methods=['GET'])
@token_required
def get_questions(current_user):
    questions = Question.query.order_by(Question.sort_order).all()
    return jsonify({'questions': [q.to_dict() for q in questions]}), 200


@questionnaire_bp.route('/submit', methods=['POST'])
@token_required
def submit_answers(current_user):
    data        = request.get_json() or {}
    answers     = data.get('answers', {})
    detection_id = data.get('detection_id')
    skin_type   = data.get('skin_type', '')
    acne_status = data.get('acne_status', '')

    if not answers:
        return jsonify({'error': 'No answers provided'}), 400

    # Persist answers to questionnaire_responses table
    if detection_id:
        detection = Detection.query.filter_by(
            id=detection_id, user_id=current_user.id
        ).first()
        if detection:
            for key, answer_value in answers.items():
                question = Question.query.filter_by(category=key).first()
                if question:
                    resp = QuestionnaireResponse(
                        detection_id=detection_id,
                        question_id=question.id,
                        answer_value=str(answer_value),
                    )
                    db.session.add(resp)
            db.session.commit()

    lifestyle_summary = summarize_lifestyle(answers)
    advices           = generate_advices(answers)
    validation        = calculate_validation_score(answers, skin_type, acne_status)

    return jsonify({
        'lifestyle_summary':  lifestyle_summary,
        'advices':            advices,
        'validation_score':   validation['score'],
        'validation_max':     validation['max_score'],
        'validation_status':  validation['status'],
    }), 200


@questionnaire_bp.route('/lifestyle', methods=['GET'])
@token_required
def get_lifestyle(current_user):
    return jsonify({'lifestyle': {}}), 200
