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

# Define API resources

registration_view = RegisterAPI.as_view('register_api')

auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST']
)