from . import ma
from models.credit import CreditModel
from models.salesman import SalesmanModel

class CreditSchema(ma.SQLAlchemyAutoSchema):
    class Meta:    
        model =CreditModel
        load_only = ('salesman',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.credit_credit_detail', id='<id>'),
        'collection': ma.URLFor('api.credit_credit_list')
    })

