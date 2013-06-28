# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, url_for, redirect
from flask.ext.login import login_required, current_user
from flask.ext.wtf import Form, TextField, TextAreaField, required, length

import simplejson as json
from copy import copy

from sa import db
from sa.models import UserDB
from sa.views import *

mod = Blueprint('user', __name__,  url_prefix='/user')


@mod.route('/')
@login_required
@check_admin
def index():
    user = UserDB.query.all()
    return render_template('user/index.html', user=user)


@mod.route('/my', methods=['GET','POST'])
@login_required
def my():
    addition = {}
    user = UserDB.query.filter(UserDB.username==current_user.username)[0]
    form = UserForm(obj=user)

    if request.headers.get('Referer') != None:
        addition['referer'] = request.headers.get('Referer')
    else:
        addition['referer'] = url_for('.my')

    if not form.validate_on_submit():
        return render_template('user/my.html', form=form, addition=addition)

    old_user = copy(user)
    form.populate_obj(user)
    user.username = old_user.username
    user.chinese_name = old_user.chinese_name
    db.session.add(user)
    db.session.commit()

    flash(u'修改成功', 'success')
    return redirect(url_for('.my'))


@mod.route('/<username>/<role>/<value>')
@login_required
@check_admin
def authority(username, role, value):
    ret = {}
    user = UserDB.query.filter(UserDB.username==username)[0]

    value = 1 if(value=="true") else 0

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


class UserForm(Form):
    username = TextField(u'用户名', validators=[])
    chinese_name = TextField(u'中文名', validators=[])
    email = TextField(u'邮箱', validators=[required(), length(max=32)])
    ssh_pubkey = TextAreaField(u'SSH公钥', validators=[])
