from flask import request, \
    make_response, render_template, redirect
from models import User
import flask_jwt_extended

def logout():
    response = make_response(redirect('/login', 302))
    flask_jwt_extended.unset_jwt_cookies(response)
    return response

def login():
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        print(user, username)
        if user is None:
            # the user was not found on the database
            return render_template(
                'login.html', 
                message='Invalid username'
            )
        
        if user.check_password(password):
            # create a new token with the user id inside
            access_token = flask_jwt_extended.create_access_token(identity=user.id)
            resp = make_response(redirect('/', 302))
            # resp = make_response('Hello world!')
            flask_jwt_extended.set_access_cookies(resp, access_token)
            return resp
        else:
            return render_template(
                'login.html', 
                message='Invalid password'
            )
    else:
        return render_template(
            'login.html'
        )

def initialize_routes(app):
    app.add_url_rule('/login', 
        view_func=login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', view_func=logout)