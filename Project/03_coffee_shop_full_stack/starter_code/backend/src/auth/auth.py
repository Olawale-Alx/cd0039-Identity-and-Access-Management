import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-j---93tj.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'development'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    # Expected
    # This gets the header from the request and returns the jwt token part of the header (seperated from the first part of the request).
    # Should raise an error (AuthError) if header is not present or properly formed
    if 'Authorization' not in request.headers:
        raise AuthError('Unauthorized request', 401)

    auth_request_header = request.headers['Authorization']
    header_parts = auth_request_header.split(' ')

    if len(header_parts) != 2:
        raise AuthError({
            'error message': 'unauthorized request',
            'description': 'malfunctioned header'
        }, 401)

    if header_parts[0].lower() != 'bearer':
        raise AuthError({
            'error message': 'unauthorized request',
            'description': 'bearer not found'
        }, 401)

    return header_parts[1]


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    # Expected
    # Input: permission, decoded jwt payload
    # Raises an error if requested permission string is not in the jwt user permissions list
    # return true otherwise
    if 'permissions' not in payload:
        raise AuthError({
            'error message': 'invalid claims',
            'description': 'permissions not included in the payload'
        }, 403)

    return True


'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    # This end will contain the jwt keys used to sign all Auth0 issued jwt for this Auth0-tenant
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.load(jsonurl.read())

    unverfied_request_header = jwt.get_unverified_header(token)
    rsa_key = {}

    if 'kid' not in unverfied_request_header:
        raise AuthError({
            'error message': 'invalid request header',
            'description': 'authorization not properly formed'
        }, 401)

    for key in jwks['keys']:
        # Claim validation
        if key['kid'] == unverfied_request_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e'],
            }

        if rsa_key:
            try:
                payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS, audience=API_AUDIENCE, issuer=f'https://{AUTH0_DOMAIN}/')

                return payload

            except jwt.ExpiredSignatureError:
               raise AuthError({
            'error message': 'expired token',
            'description': 'Token has expired'
        }, 401)

            except jwt.JWTClaimsError:
               raise AuthError({
            'error message': 'invalid claims',
            'description': 'Incorrect claims. Kindly check with issuer and API audience'
        }, 401)

            except Exception:
               raise AuthError({
            'error message': 'invalid header',
            'description': 'unable to process the authentication toekn'
        }, 400)

    raise AuthError({
        'error message': 'invalid header',
        'description': 'unable to process token'
    }, 400)

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    """
    :param permission: string permission ('post:drink')
    :return:
    """
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator