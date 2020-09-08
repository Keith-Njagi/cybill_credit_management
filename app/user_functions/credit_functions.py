import requests
import json

def license_existence(auth_token, license_id):
    license_url = f'http://172.18.0.1:3101/api/license/{license_id}'
    req = requests.get(license_url, headers=auth_token)
    
    if req.status_code != 200:    
        resp = req.json()
        return {'message':resp, 'status_code': req.status_code}

    license_key = req.json()

    status = license_key['license_status']
    if status == 'on_credit' or status == 'sold':
        return {'message':'This license is not available for crediting. It has either already sold or on credit.'}, 400
    
    return license_key

def price_fetcher(auth_token, license_id):
    license_url = f'http://172.18.0.1:3101/api/license/{license_id}'
    req = requests.get(license_url, headers=auth_token)

    if req.status_code != 200:    
        resp = req.json()
        return {'message':resp, 'status_code': req.status_code}

    return req.json()
