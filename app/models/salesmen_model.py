from datetime import datetime

from . import db, ma

class Salesman(db.Model):
    __tablename__ = 'salesmen'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    limit = db.Column(db.Float(precision=2), nullable=False)
    is_suspended = db.Column(db.Integer, nullable=False, default=0) # 0 is false, 1 is true, 2 is restored
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    def insert_record(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def fetch_all(cls):
        return cls.query.order_by(cls.id.desc()).all()

    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def fetch_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def suspend_salesman(cls, id, is_suspended=None):
        record = cls.fetch_by_id(id)
        if is_suspended:
            record.is_suspended = is_suspended
        db.session.commit()
        return True
    
    @classmethod
    def restore_salesman(cls, id, is_suspended=None):
        record = cls.fetch_by_id(id)
        if is_suspended:
            record.is_suspended = is_suspended
        db.session.commit()
        return True

    @classmethod
    def update_salesman(cls, id, limit=None):
        record = cls.fetch_by_id(id)
        if limit:
            record.limit = limit
        db.session.commit()
        return True

    @classmethod
    def delete_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True


class SalesmanSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_id', 'limit', 'is_suspended', 'created', 'updated')

