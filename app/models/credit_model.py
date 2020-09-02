from datetime import datetime

from . import db, ma
from .salesmen_model import Salesman

class Credit(db.Model):
    __tablename__ = 'credits'
    id = db.Column(db.Integer, primary_key=True)
    salesman_id = db.Column(db.Integer, db.ForeignKey('salesmen.id'), nullable=False)
    salesman = db.relationship('Salesman', backref=db.backref('credits', single_parent=True, lazy=True))
    license_id = db.Column(db.Integer, unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    def insert_record(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def fetch_all(cls):
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def fetch_by_salesman_id(cls, salesman_id):
        return cls.query.filter_by(salesman_id=salesman_id).all()

    @classmethod
    def fetch_by_license_id(cls, license_id):
        return cls.query.filter_by(license_id=license_id).first()

    @classmethod
    def delete_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True

class CreditSchema(ma.Schema):
    class Meta:
        fields = ('id', 'salesman_id', 'license_id', 'created', 'updated')
    