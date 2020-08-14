import requests
log_submission_url = 'http://172.18.0.1:3100/api/logs' # 'http://0.0.0.0:3100/api/logs' # 172.18.0.3

def record_user_log(auth_token, method, description):
    payload = {'method': method, 'description': description}
    res = requests.post(log_submission_url, json=payload, headers=auth_token)
    if res.status_code != 201:
        print ("Error:", res.status_code)
        print(res.text)
        return {'Message': description + ', but log was never recorded in database.'}, 400 