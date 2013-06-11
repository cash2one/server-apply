from sa import app, db
from sa.models import User, UserDB

from flask import url_for, request, redirect, json
from flask.ext.login import login_required, login_user, logout_user, current_user

from urllib import urlopen, urlencode


@app.route('/')
@login_required
def index():
    return redirect(url_for('apply.index'))


@app.route('/login')
def login():
    code = request.args.get('code')
    if code:
        return redirect(app.config['ACCESS_TOKEN_URL'] % code)

    access_token = request.args.get('access_token')
    if access_token:
        try:
            f = urlopen(app.config['RESOURCE_URL'], urlencode({'oauth_token':access_token, 'getinfo':True}))
            info = json.loads(f.read())
        except:
            return redirect(app.config['REQUEST_TOKEN_URL'])

        try:
            UserDB.query.filter(UserDB.username == info['username'])[0]
        except:
            userdb = UserDB(info['username'], info['chinese_name'], info['email'], 0, 0, 0)
            db.session.add(userdb)
            db.session.commit()

        user = User(info['username'], info['username'], info['chinese_name'], info['email'], 0, 0, 0)
        login_user(user)
        return redirect(url_for('.index'))

    return redirect(app.config['REQUEST_TOKEN_URL'])


@app.route('/logout')
def logout():
    logout_user()
    return redirect(app.config['LOGOUT_URL'])
