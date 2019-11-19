from base import request
import config


def login_with_email(email):
    options = {
        'method': 'POST',
        'body' : {
            'email' : email
        }
    }

    return request(options, 'v3/customers/login_with_email')

def login_with_phone(phone):
    options = {
        'method': 'POST',
        'body': {
            'phone': phone
        }
    }

    return request(options, 'v4/customers/login_with_phone')

def generater_costumer_token(otp, login_token):
    options = {
        'method': 'POST',
        'body': {
            'scopes': 'gojek:customer:transaction gojek:customer:readonly',
            'client_name':'gojek:cons:android',
            'grant_type': 'otp',
            'data': {
                'otp_token': login_token,
                'otp' : str(otp)
            },
            'client_id' : 'gojek:cons:android',
            'client_secret': config.get_client_secret()
        }
    }

    return request(options, 'v4/customers/login/verify')

def get_customer_info():
    """
    Usage :
        p = pygojek.get_customer_info()
    Get the costumer info
    :return: requests object
    """
    options = {
        'method': 'GET'
    }

    return request(options, 'gojek/v2/customer')

def logout():
    options = {
        'method': 'DELETE'
    }

    return request(options, 'v3/auth/token')