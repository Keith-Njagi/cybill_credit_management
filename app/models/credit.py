from datetime import datetime
from typing import List

from . import db

class CreditModel(db.Model):
    __tablename__ = 'salesman_credits'
    id = db.Column(db.Integer, primary_key=True)
    salesman_id = db.Column(db.Integer, db.ForeignKey('salesmen.id'), nullable=False)
    salesman = db.relationship('SalesmanModel')
    license_id = db.Column(db.Integer, unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_all(cls) -> List['CreditModel']:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_salesman_id(cls, salesman_id:int) -> List ['CreditModel']:
        return cls.query.filter_by(salesman_id=salesman_id).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'CreditModel':
        return cls.query.get(id)

    @classmethod
    def fetch_by_license_id(cls, license_id:int) -> 'CreditModel':
        return cls.query.filter_by(license_id=license_id).first()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
