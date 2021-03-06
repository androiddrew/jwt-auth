# project/server/auth/views.py

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server import bcrypt, db
from project.server.models import User

auth_blueprint = Blueprint('auth', __name__)

class RegisterAPI(MethodView):
    """User Registration Resource"""

    def post(self):
        # Get the post data
        post_data = request.get_json()
        # check of user already exists
        user = User.query.filter_by(email=post_data.get('email')).first()
        if not user:
            try:
                user = User(
                    email=post_data.get('email'),
                    password=post_data.get('password')
                )

                #insert new user
                db.session.add(user)
                db.session.commit()
                # gen auth token
                auth_token = User.encode_auth_token(user.id)
                responseObject = {
                    "status": "success",
                    "message": "Successfully registered.",
                    "auth_token": auth_token.decode()
                }
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    "status": "failure",
                    "message": "An error occurred. Please try again"
                }
                return make_response(jsonify(responseObject)), 500
        else:
            responseObject = {
                "status": "failure",
                "message": "User already exists. Please log in."
            }
            return make_response(jsonify(responseObject)), 202


class LoginAPI(MethodView):
    """User Login Resource"""

    def post(self):
        post_data = request.get_json()
        try:
            user = User.query.filter_by(
                email=post_data.get('email')
            ).first()
            if not user:
                responseObject = {
                    'status': 'failure',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(responseObject)), 404

            if bcrypt.check_password_hash(
                    user.password, post_data.get('password')):
                auth_token = User.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode()
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'failure',
                    'message': 'Password provided was incorrect.'
                }
                return make_response(jsonify(responseObject)), 401

        except Exception as e:
            print(e) # Want to make this a logging statement
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500


class UserAPI(MethodView):
    """User Resource"""

    def get(self):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token=''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                responseObject = {
                    'status': 'success',
                    'data':{
                        'user_id': user.id,
                        'email': user.email,
                        'admin': user.admin,
                        'registered_on': user.registered_on
                    }
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'failure',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'failure',
                'message': 'Valid auth token required'
            }
            return make_response(jsonify(responseObject)), 401


# Define API resources

registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_view = UserAPI.as_view('user_api')


auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)

auth_blueprint.add_url_rule(
    '/auth/status',
    view_func=user_view,
    methods=['GET']
)