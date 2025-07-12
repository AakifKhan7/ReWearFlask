import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .. import db
from ..models import Cloth, ClothImage, Style, Type
from ..forms import ItemForm

items_bp = Blueprint('items', __name__, url_prefix='/items')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@items_bp.route('/')
def list_items():
    items = Cloth.query.filter_by(isDeleted=False).all()
    return render_template('items/items_list.html', items=items)


@items_bp.route('/<int:cid>')
def item_detail(cid):
    item = Cloth.query.get_or_404(cid)
    return render_template('items/item_detail.html', item=item)


@items_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        # Resolve or create style & type
        style = Style.query.filter_by(name=form.style.data).first()
        if not style and form.style.data:
            style = Style(name=form.style.data)
            db.session.add(style)
        type_ = Type.query.filter_by(name=form.type.data).first()
        if not type_ and form.type.data:
            type_ = Type(name=form.type.data)
            db.session.add(type_)
        db.session.flush()

        cloth = Cloth(
            uid=current_user.uid,
            sid=style.sid if style else None,
            tid=type_.tid if type_ else None,
            c_title=form.c_title.data,
            c_description=form.c_description.data,
            condition=form.condition.data,
            genderSuited=form.genderSuited.data,
            size=form.size.data,
        )
        db.session.add(cloth)
        db.session.flush()

        # handle image upload
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            form.image.data.save(filepath)
            img = ClothImage(cid=cloth.cid, url=f'uploads/{filename}')
            db.session.add(img)
        db.session.commit()
        flash('Item added successfully.', 'success')
        return redirect(url_for('items.item_detail', cid=cloth.cid))
    return render_template('items/item_form.html', form=form)


@items_bp.route('/<int:cid>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(cid):
    item = Cloth.query.get_or_404(cid)
    if item.uid != current_user.uid and current_user.role.name != 'admin':
        abort(403)
    form = ItemForm(obj=item)
    if form.validate_on_submit():
        item.c_title = form.c_title.data
        item.c_description = form.c_description.data
        item.condition = form.condition.data
        item.genderSuited = form.genderSuited.data
        item.size = form.size.data
        db.session.commit()
        flash('Item updated.', 'success')
        return redirect(url_for('items.item_detail', cid=item.cid))
    return render_template('items/item_form.html', form=form, edit=True)


@items_bp.route('/<int:cid>/delete', methods=['POST'])
@login_required
def delete_item(cid):
    item = Cloth.query.get_or_404(cid)
    if item.uid != current_user.uid and current_user.role.name != 'admin':
        abort(403)
    item.isDeleted = True
    db.session.commit()
    flash('Item deleted.', 'info')
    return redirect(url_for('items.list_items'))


# Serve uploaded images (simplistic, not for production)
@items_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
