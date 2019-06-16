import urllib.request
import json
import time
from jose import jwk, jwt
from jose.utils import base64url_decode

region = 'us-east-1'
userpool_id = 'us-east-1_70RGq0dzd'
app_client_id = '3ijq6ag7hihdm2rchduerhd0p4'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
response = urllib.request.urlopen(keys_url)
keys = json.loads(response.read())['keys']

def lambda_handler(event, context):
    token = event['token']
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    print(claims)
    return claims
        
# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
if __name__ == '__main__':
    # for testing locally you can enter the JWT ID Token here
    event = {'token': 'eyJraWQiOiJUcVd2NGlJQTR5NEsrMCtWSVRYMklYM2JDV1RVU3JoNnhNdGl5aVh5QkE0PSIsImFsZyI6IlJTMjU2In0.eyJjdXN0b206cmVnaW9uIjoidXMtZWFzdC0xIiwiYXRfaGFzaCI6IndkN0k5RUdfdTJ5VUdvS190WHVadlEiLCJzdWIiOiJmYzdkNzJjNy01MGIzLTQ0NmEtYTE0NC03OTZhMDAxYzI3NjUiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfNzBSR3EwZHpkIiwicGhvbmVfbnVtYmVyX3ZlcmlmaWVkIjp0cnVlLCJjdXN0b206YWNjb3VudGlkIjoiMTkyODkxMDI5ODExIiwiY29nbml0bzp1c2VybmFtZSI6ImZjN2Q3MmM3LTUwYjMtNDQ2YS1hMTQ0LTc5NmEwMDFjMjc2NSIsImN1c3RvbTpvcmdhbml6YXRpb25pZCI6Im9nMzI3MDYyNjY2MSIsImF1ZCI6IjNpanE2YWc3aGloZG0ycmNoZHVlcmhkMHA0IiwiZXZlbnRfaWQiOiJmODdhMzRmYS04YjAwLTExZTktYTk4Ni0yZjBiMDdhY2I5ZTkiLCJ0b2tlbl91c2UiOiJpZCIsImN1c3RvbTpjYW1wdXNpZCI6ImNwOTYxNDQxNDg4OSIsImF1dGhfdGltZSI6MTU2MDExNzE4OSwicGhvbmVfbnVtYmVyIjoiKzE5NTQ4NjE3MjcxIiwiZXhwIjoxNTYwMTIwNzg5LCJjdXN0b206cm9sZSI6Im1hc3RlciIsImlhdCI6MTU2MDExNzE4OSwiY3VzdG9tOmVudmlyb25tZW50IjoiZGV2IiwiZW1haWwiOiJsYXN0aHl1bjgyMkBnbWFpbC5jb20ifQ.IJcaFhntOrxZw5eDOstCjWKssdlBpdFC0MO0LQym-TRtJLSBJsUyRls6IU1FRA8ehcSkv63TYZoHNX0goAsgcpQngVUcWkLnfUQTjxRcyqlqJlTCMnqKzM0Ldes6nIaYgpx2XokhpPaB7PbQ5pVhcRaDED13R1dm-YxGK0jJKnFVbBiLI5kOYJivzNdqCGbiPpo3itGGaXH-WJPy7GbxdccGwjLjAWD8ZWdvHaLAz4mqEF5iCqzm5uRopC3hym7zfJhhRoAonGx2epIWgB7oNje1UXyFqGjSJ0toWFBxT8Kl0wieevFt_qxUlo6rYemVV9yBPyWQmxDmM5BDl6YoIw'}
    lambda_handler(event, None)