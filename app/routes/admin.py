from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from .. import db
from ..models import Cloth
from ..utils import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/items')
@login_required
@admin_required
def moderate_items():
    items = Cloth.query.filter_by(isDeleted=False).all()
    return render_template('admin/items.html', items=items)


@admin_bp.route('/items/<int:cid>/toggle-approval')
@login_required
@admin_required
def toggle_item(cid):
    item = Cloth.query.get_or_404(cid)
    item.isDeleted = not item.isDeleted  # simple toggle to simulate approve/reject
    db.session.commit()
    flash('Item status updated.', 'success')
    return redirect(url_for('admin.moderate_items'))
