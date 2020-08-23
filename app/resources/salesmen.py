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
    @api.doc('Fetch salesmen')
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
            return {'message': 'Could not fetch salesmen'}, 500

    @jwt_required
    @api.doc('register_salesman')
    @api.expect(salesman_model)
    def post(self):
        '''Register Salesman'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not allowed to access this resource'}, 403
        try:
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
        
            db_salesman = Salesman.fetch_by_user_id(user_id)
            my_salesman = salesman_schema.dump(db_salesman)
            if len(my_salesman) != 0:
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
            return {'message': 'Could not add salesman'}, 500

# - '/salesman/<int:id>'
# get one salesman - Admin, Sales Man(user_id) 
# put salesman - Admin
# delete salesman - Admin
@api.route('/<int:id>')
@api.param('id', 'The salesman identifier')
class SalesmanOperations(Resource):
    @jwt_required
    @api.doc('Get one salesman')
    def get(self, id):
        '''Get one Salesman'''
        try:
            authorised_user = get_jwt_identity()
            claims = get_jwt_claims()

            db_salesman = Salesman.fetch_by_id(id)
            salesman = salesman_schema.dump(db_salesman)
            if len(salesman) != 0:
                if authorised_user['id'] == salesman['user_id'] or claims['is_admin']:
                    

                    # Record this event in user's logs
                    log_method = 'get'
                    log_description = 'Fetched salesman <' + str(id) + '>' 
                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)

                    return {'salesman': salesman}, 200
                return {'message':'You are not authorised to view this salesman!'}, 403
            return {'message': 'There is no such record!'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch salesman.'}, 500
        
    @jwt_required
    @api.doc('Edit credit limits')
    @api.expect(edit_salesman_model)
    def put(self, id):
        '''Edit Credit limits'''
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not authorised to edit this record!'}, 403
        try:
            db_salesman = Salesman.fetch_by_id(id)
            this_salesman = salesman_schema.dump(db_salesman)
            if len(this_salesman) == 0:
                return {'message': 'This salesman does not exist.'}, 404
            
            data =api.payload
            if not data:
                return {'message':'No input data detected'}, 400
            
            limit = data['limit']
            Salesman.update_salesman(id=id, limit=limit)
            db_salesman = Salesman.fetch_by_id(id)
            salesman = salesman_schema.dump(db_salesman)
            
            # Record this event in user's logs
            log_method = 'put'
            log_description = 'Updated salesman <' + str(id) + '>' 
            authorization = request.headers.get('Authorization')
            auth_token  = { "Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)

            return {'salesman': salesman}, 200
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return {'message': 'Could not update salesman'}, 500


    @jwt_required
    @api.doc('Delete salesman')
    def delete(self, id):
        '''Delete Salesman'''
        authorised_user = get_jwt_identity()
        claims = get_jwt_claims()
        try:
            db_salesman = Salesman.fetch_by_id(id)
            salesman = salesman_schema.dump(db_salesman)
            if len(salesman) != 0:
                if claims['is_admin']:
                    Salesman.delete_by_id(id)

                    # Record this event in user's logs
                    log_method = 'delete'
                    log_description = 'Deleted salesman <' + str(id) + '>' 
                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)

                    return {'message': 'Successfully deleted salesman'}, 200
                return {'message':'You are not authorised to delete this salesman!'}, 403
            return {'message': 'There is no such record!'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return {'message': 'Could not delete salesman'}, 500

@api.route('/user/<int:user_id>')
@api.param('user_id', 'The user identifier')
class GetSalesmanUser(Resource):
    @jwt_required
    @api.doc('Get salesman by user')
    def get(self, user_id):
        '''Get Salesman by User'''
        authorised_user = get_jwt_identity()
        claims = get_jwt_claims()

        try:
            if authorised_user['id'] == user_id or claims['is_admin']:
                db_salesman = Salesman.fetch_by_user_id(user_id=user_id)
                salesman = salesman_schema.dump(db_salesman)

                if len(salesman) == 0:
                    return {'message': 'There is no such salesman'}, 404

                # Record this event in user's logs
                log_method = 'get'
                log_description = 'Fetched salesman by user id <' + str(user_id) + '>' 
                authorization = request.headers.get('Authorization')
                auth_token  = { "Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)

                return {'salesman': salesman}, 200
            return {'message': 'You are not authorised to  view this salesman!'}, 403
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch salesman.'}, 500

        

@api.route('/suspend/<int:id>')
@api.param('id', 'The salesman identifier')
class SuspendSalesman(Resource):
    @jwt_required
    @api.doc('suspend_salesman')
    def put(self, id):
        '''Suspend Salesman'''
        authorised_user = get_jwt_identity()
        claims = get_jwt_claims()
        try:
            db_salesman = Salesman.fetch_by_id(id)
            salesman = salesman_schema.dump(db_salesman)
            if len(salesman) != 0:
                if claims['is_admin']:

                    is_suspended = 1
                    Salesman.suspend_salesman(id=id, is_suspended=is_suspended)

                    # Record this event in user's logs
                    log_method = 'put'
                    log_description = 'Suspended salesman <' + str(id) + '>' 
                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)

                    return {'message': 'Successfully suspended salesman'}, 200
                return {'message':'You are not authorised to suspend this salesman!'}, 403
            return {'message': 'There is no such record!'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return {'message': 'Could not delete salesman'}, 500

@api.route('/restore/<int:id>')
@api.param('id', 'The salesman identifier')
class RestoreSalesman(Resource):
    @jwt_required
    @api.doc('suspend_salesman')
    def put(self, id):
        '''Restore Salesman'''
        authorised_user = get_jwt_identity()
        claims = get_jwt_claims()
        try:
            db_salesman = Salesman.fetch_by_id(id)
            salesman = salesman_schema.dump(db_salesman)
            if len(salesman) != 0:
                if claims['is_admin']:
                    
                    is_suspended = 2
                    Salesman.suspend_salesman(id=id, is_suspended=is_suspended)

                    # Record this event in user's logs
                    log_method = 'put'
                    log_description = 'Restored salesman <' + str(id) + '>' 
                    authorization = request.headers.get('Authorization')
                    auth_token  = { "Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)

                    return {'message': 'Successfully restored salesman'}, 200
                return {'message':'You are not authorised to restore this salesman!'}, 403
            return {'message': 'There is no such record!'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return {'message': 'Could not delete salesman'}, 500