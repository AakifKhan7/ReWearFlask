from datetime import datetime
from flask_login import UserMixin
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


class TimeStampedModelMixin:
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    createdBy = db.Column(db.Integer, nullable=True)
    updatedBy = db.Column(db.Integer, nullable=True)
    isDeleted = db.Column(db.Boolean, default=False)


class UserRole(db.Model, TimeStampedModelMixin):
    __tablename__ = 'user_role'
    roleId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)


class User(db.Model, UserMixin, TimeStampedModelMixin):
    __tablename__ = 'user'
    uid = db.Column(db.Integer, primary_key=True)
    profileImg = db.Column(db.String(255))
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    city = db.Column(db.String(120))
    contact = db.Column(db.String(20))

    role_id = db.Column(db.Integer, db.ForeignKey('user_role.roleId'), default=1)

    auth = db.relationship('Auth', backref='user', uselist=False)
    cloths = db.relationship('Cloth', backref='uploader', lazy=True)
    activities = db.relationship('Activity', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'

    # Flask-Login requirement: return a unicode that uniquely identifies this user
    def get_id(self):
        return str(self.uid)

    @property
    def coins(self):
        """Simple coins logic: +10 for each active item not yet swapped, +20 for each completed swap."""
        active_items = [c for c in self.cloths if not c.hasSwapped]
        completed_swaps = SwapRequest.query.filter(
            ((SwapRequest.senderUid == self.uid) | (SwapRequest.recieverUid == self.uid)) & (SwapRequest.status == True)
        ).count()
        return len(active_items) * 10 + completed_swaps * 20


class Auth(db.Model, TimeStampedModelMixin):
    __tablename__ = 'auth'
    aid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password = db.Column('password', db.String(128), nullable=False)

    def set_password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    def __repr__(self):
        return f'<Auth {self.email}>'


class Style(db.Model, TimeStampedModelMixin):
    __tablename__ = 'styles'
    sid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    cloths = db.relationship('Cloth', backref='style', lazy=True)


class Type(db.Model, TimeStampedModelMixin):
    __tablename__ = 'types'
    tid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    cloths = db.relationship('Cloth', backref='type', lazy=True)


class Cloth(db.Model, TimeStampedModelMixin):
    __tablename__ = 'cloths'
    cid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    sid = db.Column(db.Integer, db.ForeignKey('styles.sid'))
    tid = db.Column(db.Integer, db.ForeignKey('types.tid'))

    c_title = db.Column(db.String(120), nullable=False)
    c_description = db.Column(db.Text)
    condition = db.Column(db.String(120))
    hasSwapped = db.Column(db.Boolean, default=False)
    genderSuited = db.Column(db.String(10), default='both')
    size = db.Column(db.String(10), default='M')

    images = db.relationship('ClothImage', backref='cloth', lazy=True)

    def __repr__(self):
        return f'<Cloth {self.c_title}>'


class ClothImage(db.Model, TimeStampedModelMixin):
    __tablename__ = 'cloth_img'
    imgId = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.Integer, db.ForeignKey('cloths.cid'))
    url = db.Column(db.String(255))


class SwapRequest(db.Model, TimeStampedModelMixin):
    __tablename__ = 'swap_requests'
    senderCid = db.Column(db.Integer, db.ForeignKey('cloths.cid'), primary_key=True)
    recieverCid = db.Column(db.Integer, db.ForeignKey('cloths.cid'), primary_key=True)
    senderUid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    recieverUid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    status = db.Column(db.Boolean, nullable=True)  # None / True / False


class Activity(db.Model):
    __tablename__ = 'activity'
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True)
    ip = db.Column(db.String(45))
    loginAt = db.Column(db.DateTime, default=datetime.utcnow)
    logoutAt = db.Column(db.DateTime, nullable=True)

    updatedBy = db.Column(db.Integer, nullable=True)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
