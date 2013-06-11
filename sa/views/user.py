# -*- coding: utf-8 -*-

from flask import Blueprint, render_template

import simplejson as json

from sa import db
from sa.models import UserDB

mod = Blueprint('user', __name__,  url_prefix='/user')


@mod.route('/')
def index():
    user = UserDB.query.all()
    return render_template('user/index.html', user=user)


@mod.route('/<username>/<role>/<value>')
def authority(username, role, value):
    ret = {}
    user = UserDB.query.filter(UserDB.username==username)[0]

    if value=="true":
        value = 1
    else:
        value = 0

    if role=="admin":
        user.if_admin = value
    elif role=="approver":
        user.if_approver = value
    elif role=="idc":
        user.if_idc = value
    else:
        ret['status'] = 'error'
        return json.dumps(ret)

    try:
        db.session.add(user)
        db.session.commit()
        ret['status'] = 'ok'
    except:
        ret['status'] = 'error'

    return json.dumps(ret)
