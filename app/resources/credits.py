import requests
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from models.credit_model import Credit, CreditSchema
from models.salesmen_model import Salesman, SalesmanSchema
from user_functions.record_user_log import record_user_log
from user_functions.credit_functions import license_existence, price_fetcher

api = Namespace('credit', description='Credits Management')

salesman_schema = SalesmanSchema()
credit_schema = CreditSchema()
credit_schemas = CreditSchema(many=True)

credit_model = api.model('Credit', {
    'salesman_id': fields.Integer(required=True, description='Salesman ID'),
    'license_id': fields.Integer(required=True, description='License ID')
})

# '/'
# get all credits - Admin
# post credit - Admin, SalesMan
@api.route('')
class CreditList(Resource):
    @api.doc('Get all credits')
    @jwt_required
    def get(self):
        '''Get All Credits'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not allowed to access this resource'}, 403
        try:
            db_credits = Credit.fetch_all()
            all_credits = credit_schemas.dump(db_credits)
            if len(all_credits) == 0:
                return {'message':'There are no credits recorded yet.'}, 404

            # Record this event in user's logs
            log_method = 'get'
            log_description = 'Fetched all credits'
            authorization = request.headers.get('Authorization')
            auth_token  = { "Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)
            return {'credits': all_credits}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return {'message': 'Could not fetch credits'}, 500

    @api.doc('Post credit item')
    @jwt_required
    @api.expect(credit_model)
    def post(self):
        '''Post Credit Item'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not allowed to access this resource'}, 403
        try:
            data = api.payload
            if not data:
                return {'message':'No input data detected.'}, 400

            salesman_id = data['salesman_id']
            license_id = data['license_id']

            # Check if salesman exists
            db_salesman = Salesman.fetch_by_id(id=salesman_id)
            salesman = salesman_schema.dump(db_salesman)
            if len(salesman) == 0:
                return {'message': 'The specified salesman does not exist'}, 404


            db_license = Credit.fetch_by_license_id(license_id)
            license_record = credit_schema.dump(db_license)
            if len(license_record) != 0:
                return {'message': 'This license has already been credited.'}, 400

            # Check if license exists
            authorization = request.headers.get('Authorization')
            auth_token  = { "Authorization": authorization}
            # license existence
            # Check if license is already credited or sold
            license_response = license_existence(auth_token, license_id)
            if 'license' not in license_response.keys():
                return license_response['message'],license_response['status_code']
            # check if credit limits will be surpassed
            # if sum(credits.limits) + license['price'] - sales.payments.amount > salesman.limit
            #     return {'message':'Submission Denied. You cannot add credits if they will pass the limit.'}, 400
            salesman_credits = Credit.fetch_by_salesman_id(salesman_id)
            if salesman_credits:
                license_prices = []
                for credit in salesman_credits:
                    license_key = credit.license_id
                    price_response = price_fetcher(auth_token, license_key)
                    if 'license' in price_response.keys():
                        if price_response['license']['status'] == 'on_credit':
                            price = float(price_response['license']['price'])
                            license_prices.append(price)
                    else:
                        return price_response['message'], price_response['status_code']
                if sum(license_prices) + float(license_response['license']['price']) > db_salesman.limit:
                    return {'message': 'Could not add credit item. Adding this item will exceed the salesman limits.'}, 400
                
            # Add credit record to database
            new_credit_record = Credit(salesman_id=salesman_id, license_id=license_id)
            new_credit_record.insert_record()

            credit_data = credit_schema.dump(data)

            # Record this event in user's logs
            log_method = 'post'
            log_description = f'Added new credit record to salesman <{salesman_id}>'           
            record_user_log(auth_token, log_method, log_description)

            credit_license_url = f'http://172.18.0.1:3101/api/license/credit/{license_id}'
            res = requests.put(credit_license_url, headers=auth_token)
            if res.status_code != 200:    
                return {'message':{1:'Updated credits but was unable to set license status to on credit.', 2:res.json()}}, res.status_code
            
            return {'credit': credit_data }, 201
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return {'message': 'Could not post credit item'}, 500
        

# - '/<int:id>'
# get one credit - Admin, SalesMan
# delete credit - Admin
@api.route('/<int:id>')
@api.param('id', 'The credit identifier')
class CreditOperations(Resource):
    @api.doc('Get specific credit')
    @jwt_required
    def get(self, id):
        '''Get Specific Credit'''
        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        this_user = authorised_user['id']
        try:
            db_credit = Credit.fetch_by_id(id)
            credit_record = credit_schema.dump(db_credit)
            if len(credit_record) != 0:
                user = db_credit.salesman.user_id
                if user == this_user or claims['is_admin']:
                    # Record this event in user's logs
                    log_method = 'get'
                    log_description = f'Fetched credit record <{id}>'
                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)
                    return {'credit':credit_record}, 200
                return {'message':'You are not authorised to fetch this record'}, 403
            return {'message':'This record does not exist.'}, 404

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return {'message': 'Could not get credit item'}, 500

    @api.doc('Delete credits')
    @jwt_required
    def delete(self, id):
        '''Delete Credit'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message':'You are not authorised to access this resource'}, 403
        try:
            db_credit = Credit.fetch_by_id(id)
            credit_record = credit_schema.dump(db_credit)
            if len(credit_record) == 0:
                return {'message':'This record does not exist.'}, 404
        
            Credit.delete_by_id(id)

            # Record this event in user's logs
            log_method = 'delete'
            log_description = f'Deleted credit record <{id}>'
            authorization = request.headers.get('Authorization')
            auth_token  = { "Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)

            sales_url = f'http://172.18.0.1:3101/api/license_sale/license/{id}'
            req = requests.get(sales_url, headers=auth_token)
            if req.status_code == 404:
                credit_license_url = f'http://172.18.0.1:3101/api/license/avail/{license_id}'
                res = requests.post(credit_license_url, headers=auth_token)
                if req.status_code != 200:    
                    if '\"message\"' in req.text: # {\n    \"message\": \"User does not exist\"\n}\n
                        msg = req.text.split('\"')
                        return {'message':{1:'Deleted credit but was unable to avail license status.', 2:msg[3]}},req.status_code
                    return {'message':{1:'Deleted credit but was unable to avail license status.', 2:req.text}}, req.status_code

            return {'message':'Successfully deleted Credit record'}, 200

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return {'message': 'Could not delete credit item'}, 500

# - '/salesman/<int:salesman_id>'
# get credits by salesman - Admin, SalesMan
@api.route('/salesman/<int:salesman_id>')
@api.param('salesman_id', 'The salesman identifier')
class CreditBySalesman(Resource):
    @api.doc('Get credits by salesman')
    @jwt_required
    def get(self, salesman_id):
        '''Get Credits By Salesman'''
        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        
        db_credits = Credit.fetch_by_salesman_id(salesman_id)
        credit_records = credit_schemas.dump(db_credits)
        if len(credit_records) != 0:
            this_user = authorised_user['id']
            db_salesman = Salesman.fetch_by_id(id=salesman_id)
            user = db_salesman.user_id
            if user == this_user or claims['is_admin']:
                # Record this event in user's logs
                log_method = 'get'
                log_description = f'Fetched credit records by salesman <{salesman_id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return {'credits':credit_records}
            return {'message':'You are not authorised to access this resource'}, 403
        return {'message':'There are no credits yet.'}, 404
