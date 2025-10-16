from flask import Blueprint

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/', methods=['GET'])
def get_feedback():
    return {'message': 'Feedback endpoint ready'}, 200
