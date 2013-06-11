from flask import Flask, render_template
from flask.ext.login import current_user

app = Flask(__name__)


#
# Configs
#
try:
    app.config.from_object("website_config")
except:
    print 'Config file not found!'

#
# DB
#
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

#
# Login
#
from flask.ext.login import LoginManager
from sa.models import User, UserDB

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(userid):
    userdb = UserDB.query.filter(UserDB.username == userid)
    return User(userid, userdb[0].username, userdb[0].chinese_name, userdb[0].email,
                userdb[0].if_admin, userdb[0].if_approver, userdb[0].if_idc)

#
# Views
#
from sa.views import general
from sa.views import apply
from sa.views import approve
from sa.views import stype
from sa.views import smodel
from sa.views import approver
from sa.views import server
from sa.views import user

app.register_blueprint(apply.mod)
app.register_blueprint(approve.mod)
app.register_blueprint(stype.mod)
app.register_blueprint(smodel.mod)
app.register_blueprint(approver.mod)
app.register_blueprint(server.mod)
app.register_blueprint(user.mod)

#
# Handlers
#
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403
