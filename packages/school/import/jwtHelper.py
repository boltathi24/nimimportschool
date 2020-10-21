import datetime
import json
import jwt

from database import PyMongo




class ApiJWTAuthentication():
    secretKey_Refresh='TempSecretRefresh'
    secretKey_access='accesdasfsToken'
    expirationTime_Refresh=5
    expirationTime_Access = 1

    @staticmethod
    def getAccessTokenWithRefreshToken(refresh_token):
        refreshTokenDecodeResponse =ApiJWTAuthentication.decodeRefreshTokenForUserName(refresh_token)
        if refreshTokenDecodeResponse.get('message').find("success") >= 0:
            db_refresh_token = PyMongo.getData("user","email",refreshTokenDecodeResponse["email"])[0]['refresh_token']
            if db_refresh_token.find(refresh_token) >=0:
                return ApiJWTAuthentication.getAccessToken(refresh_token)
            else:
                 return json.dumps({"message":"Invalid Refresh Token"})
        else:
            return refreshTokenDecodeResponse



    @staticmethod
    def validateAccessToken(access_token):
        accessTokenDecodeResponse=ApiJWTAuthentication.decodeAccesshTokenForRefreshToken(access_token) #Getting refresh Token From Token
        print(accessTokenDecodeResponse)
        if accessTokenDecodeResponse.get('message').find("success") >= 0 :
            refreshTokenDecodeResponse = ApiJWTAuthentication.decodeRefreshTokenForUserName(accessTokenDecodeResponse['refresh_token'])
            print(refreshTokenDecodeResponse)
            if refreshTokenDecodeResponse.get('message').find("success") >= 0:
                db_refresh_token = PyMongo.getData("user", "email", refreshTokenDecodeResponse["email"])[0]['refresh_token']
                if db_refresh_token.find(accessTokenDecodeResponse['refresh_token']) >= 0:
                    return {"message": "success","success":True,"email":refreshTokenDecodeResponse["email"]}
                else:
                    return {"message": "Invalid Refresh Token"}
            else:
                return refreshTokenDecodeResponse
        else:
            return accessTokenDecodeResponse



    @staticmethod
    def decodeRefreshTokenForUserName( refreshToken):
        """
        Decodes the auth token
        :param refreshToken:
        :return: integer|string
        """
        try:
            payload = jwt.decode(refreshToken, ApiJWTAuthentication.secretKey_Refresh)
            return {"message": "success","email":payload['email']}
        except jwt.ExpiredSignatureError:
            return {"message": "Expired Refresh Token"}
        except jwt.InvalidTokenError:
            return {"message": "Invalid Refresh Token"}

    @staticmethod
    def decodeAccesshTokenForRefreshToken( accessToken):
        """
        Decodes the access token
        :param accessToken:
        :return: integer|string
        """
        try:
            payload = jwt.decode(accessToken, ApiJWTAuthentication.secretKey_access)
            return {"message": "success","refresh_token": payload['refresh_token']}
        except jwt.ExpiredSignatureError:
            return {"message": "Expired Access Token"}
        except jwt.InvalidTokenError:
            return {"message": "Invalid access Token"}





    @staticmethod
    def getAccessToken( refresh_token):
            """
            Generates the Access Token
            :return: string
            """
            try:
                payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ApiJWTAuthentication.expirationTime_Access),
                    'refresh_token': refresh_token
                }
                jwttoken= jwt.encode(
                    payload,
                    ApiJWTAuthentication.secretKey_access,
                    algorithm='HS256'
                )
                token=jwttoken.decode('utf-8')
                return {"message": "success", "access_token": token}
            except Exception as e:
                return {"message": "exception","Exception": str(e)}

    @staticmethod
    def getRefreshToken( email):
            """
            Generates the Refresh Token
            :return: string
            """
            try:
                payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ApiJWTAuthentication.expirationTime_Refresh),
                    'email': email
                }
                jwtToken=jwt.encode(

                    payload= payload, key=ApiJWTAuthentication.secretKey_Refresh, algorithm='HS256'
                );
                token=jwtToken.decode('utf-8')
                return {"message": "success", "refresh_token": token}
            except Exception as e:
                return {"message": "exception","Exception": str(e)}

