from . import ma
from models.salesman import SalesmanModel
from models.credit import CreditModel
from .credit import CreditSchema

class SalesmanSchema(ma.SQLAlchemyAutoSchema):
    salesman_credits = ma.Nested(CreditSchema, many=True)
    class Meta: 
        model =SalesmanModel
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.salesman_salesman_detail', id='<id>'),
        'collection': ma.URLFor('api.salesman_salesman_list')
    })

