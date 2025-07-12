from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    from ..models import SwapRequest
    ongoing_swaps = SwapRequest.query.filter(
        ((SwapRequest.senderUid == current_user.uid) | (SwapRequest.recieverUid == current_user.uid)) & (SwapRequest.status == None)  # noqa: E711
    ).all()
    completed_swaps = SwapRequest.query.filter(
        ((SwapRequest.senderUid == current_user.uid) | (SwapRequest.recieverUid == current_user.uid)) & (SwapRequest.status == True)
    ).all()

    return render_template(
        'dashboard.html',
        user=current_user,
        ongoing_swaps=ongoing_swaps,
        completed_swaps=completed_swaps,
    )
