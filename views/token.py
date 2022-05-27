from models import User
import flask_jwt_extended
from flask import Response, request
from flask_restful import Resource
import json
from datetime import timezone, datetime, timedelta

class AccessTokenEndpoint(Resource):

    # Create a route to authenticate your users and return JWT Token. The
    # create_access_token() function is used to actually generate the JWT.
    def post(self):
        body = request.get_json() or {}
        username = body.get('username')
        password = body.get('password')
        
        # Query your database for username and password
        user = User.query.filter_by(username=username).first()
        if user is None:
            # the user was not found on the database
            return Response(json.dumps({"msg": "Bad username"}), mimetype="application/json", status=401)
        
        if user.check_password(password):
            # create a new token with the user id inside
            access_token = flask_jwt_extended.create_access_token(identity=user.id)
            refresh_token = flask_jwt_extended.create_refresh_token(identity=user.id)
            return Response(json.dumps({ 
                "access_token": access_token, 
                "refresh_token": refresh_token
            }), mimetype="application/json", status=200)
        else:
            # bad password
            return Response(json.dumps({"msg": "Bad password"}), mimetype="application/json", status=401)


class RefreshTokenEndpoint(Resource):
    
    def post(self):
        body = request.get_json() or {}
        refresh_token = body.get('refresh_token')
        if not refresh_token:
            return Response(json.dumps({ 
                    "message": "missing refresh_token"
                }), mimetype="application/json", status=400)
        try:
            decoded_token = flask_jwt_extended.decode_token(refresh_token)
            exp_timestamp = decoded_token.get("exp")
            now = datetime.timestamp(datetime.now(timezone.utc))
        except:
            return Response(json.dumps({ 
                "message": "Invalid refresh_token={0}. Could not decode.".format(refresh_token)
            }), mimetype="application/json", status=400)

        # if the refresh token is valid and hasn't expired, issue a
        # new access token:
        if exp_timestamp > now:
            identity = decoded_token.get('sub')
            access_token = flask_jwt_extended.create_access_token(identity=identity)
            return Response(json.dumps({ 
                    "access_token": access_token, 
                    "refresh_token": refresh_token
                }), mimetype="application/json", status=200)
        else:
            return Response(json.dumps({ 
                    "message": "refresh_token has expired"
                }), mimetype="application/json", status=401)

def initialize_routes(api):
    api.add_resource(
        AccessTokenEndpoint, 
        '/api/token', '/api/token/'
    )

    api.add_resource(
        RefreshTokenEndpoint, 
        '/api/token/refresh', '/api/token/refresh/'
    )