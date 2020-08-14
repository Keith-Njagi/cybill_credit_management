import requests
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from flask import request

from models.salesmen_model import Salesman, SalesmanSchema
from user_functions.record_user_log import record_user_log

api = Namespace('salesman',description='Salesman management')

salesman_model = api.model('Salesman', {
    'user_id': fields.Integer(required=True, description='User Id'),
    'limit': fields.Float(required=True, description='Credit Limit Amount')
})

edit_salesman_model = api.model('SalesmanEdit', {
    'limit': fields.Float(required=True, description='Credit Limit Amount')
})


salesman_schema = SalesmanSchema()
salesmen_schema = SalesmanSchema(many=True)



# get all credits_limits - Admin - '/salesman'
# post salesman - Admin - '/salesman'
@api.route('')
class SalesmanList(Resource):
    @jwt_required
    @api.doc('fetch_salesmen')
    def get(self):
        '''Fetch Salesmen'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not allowed to access this resource'}, 403
        try:
            db_salesmen = Salesman.fetch_all()
            salesmen = salesmen_schema.dump(db_salesmen)
            if len(salesmen) == 0:
                return {'message': 'There are no salesmen registered yet!'}, 404

            # Record this event in user's logs
            log_method = 'get'
            log_description = 'Fetched all salesmen'
            authorization = request.headers.get('Authorization')
            auth_token  = { "Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)

            return {'salesmen':salesmen}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return {'message': 'Couldn\'t fetch salesmen'}, 400

    @jwt_required
    @api.doc('register_salesman')
    @api.expect(salesman_model)
    def post(self):
        '''Register Salesman'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not allowed to access this resource'}, 403
        
        data = api.payload
        if not data:
            return {'message': 'No input data detected'}, 400

        user_id = data['user_id']

        authorization = request.headers.get('Authorization')
        auth_token  = { "Authorization": authorization}

        url = 'http://172.18.0.1:3100/api/user/' + str(user_id) # 172.18.0.3
        req = requests.get(url, headers=auth_token)
        if req.status_code != 200:    
            if '\"message\"' in req.text: # {\n    \"message\": \"User does not exist\"\n}\n
                msg = req.text.split('\"')
                return {'message':msg[3]},req.status_code
            return {req.text}, req.status_code

        limit = data['limit']
        try:
            db_salesman = Salesman.fetch_by_user_id(user_id)
            my_salesman = salesman_schema.dump(db_salesman)
            if len(my_salesman) != 0:
                print('My db salesman: ', my_salesman)
                return {'message': 'This user has already been registered as a salesman'}, 400
            new_salesman = Salesman(user_id=user_id, limit=limit)
            new_salesman.insert_record()
            salesman = salesman_schema.dump(data)

            # Record this event in user's logs
            log_method = 'post'
            log_description = 'Added salesman'
            record_user_log(auth_token, log_method, log_description)
            return {'salesman':salesman}, 200

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return {'message': 'Couldn\'t add new salesman'}, 400
        


# - '/salesman/<int:id>'
# get one salesman - Admin, Sales Man(user_id) 
# put salesman - Admin
# delete salesman - Admin
@api.route('/<int:id>')
@api.param('id', 'The salesman identifier')
class SalesmanOperations(Resource):
    @jwt_required
    @api.doc('get_salesman')
    def get(self, id):
        '''Get one Salesman'''
        pass

    @jwt_required
    @api.doc('edit_credit_limits')
    @api.expect(edit_salesman_model)
    def put(self, id):
        '''Edit Credit limits'''
        pass


    @jwt_required
    @api.doc('delete_salesman')
    def delete(self, id):
        '''Delete Salesman'''
        pass

@api.route('/suspend/<int:id>')
@api.param('id', 'The salesman identifier')
class SuspendSalesman(Resource):
    @jwt_required
    @api.doc('suspend_salesman')
    def put(self, id):
        '''Suspend Salesman'''
        pass

@api.route('/suspend/<int:id>')
@api.param('id', 'The salesman identifier')
class RestoreSalesman(Resource):
    @jwt_required
    @api.doc('suspend_salesman')
    def put(self, id):
        '''Restore Salesman'''
        pass