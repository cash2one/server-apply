# -*- coding: utf-8 -*-

from flask import Blueprint, flash, url_for, render_template, redirect, request
from flask.ext.login import current_user
from flask.ext.wtf import Form, TextField, TextAreaField, SelectField, required, length, regexp
from sqlalchemy import desc, or_, and_
from time import localtime, strftime

import urllib2

from sa import app
from sa import db
from sa.getter import get_smodel_by_id, get_server_by_apply_id, check_vm_apply, create_vm
from sa.models import Stype, Smodel, Sapply, Server
from sa.views import *

mod = Blueprint('apply', __name__,  url_prefix='/apply')


def gen_smodel():
    ret = []
    stype = Stype.query.all()
    smodel = Smodel.query.all()
    for t in stype:
        for m in smodel:
            if t.id==m.stype_id: ret.append((m.id, t.name + ' -- ' + m.name))
    return ret


@mod.route('/')
def index():
    smodel = get_smodel_by_id()
    server = get_server_by_apply_id()
    server_t = Server.query.filter(and_(Server.applier==current_user.id, Server.if_t==1))
    apply = Sapply.query.filter_by(applier=current_user.id).order_by(desc(Sapply.id))
    return render_template('apply/index.html', apply=apply, smodel=smodel, server=server, server_t=server_t, config=app.config)


@mod.route('/new/smodel/<int:smodel_id>', methods=['GET','POST'])
def new(smodel_id, **kvargs):
    form = SapplyForm()
    form.s_id.choices = gen_smodel()

    if request.method != 'POST':
        form.s_id.default = smodel_id
        form.process()

    addition = {}
    addition['smodel_id'] = smodel_id
    if request.headers.get('Referer') != None:
        addition['referer'] = request.headers.get('Referer')
    else:
        addition['referer'] = url_for('.index')

    if not form.validate_on_submit():
        return render_template('apply/new.html', form=form, addition=addition)

    smodel = get_smodel_by_id()
    if not smodel[form.s_id.data].if_t:
        form.days.data = -1
    if smodel[form.s_id.data].if_t and form.days.data == '':
        form.days.data = 7

    try:
        sapply = Sapply(form.name.data, form.s_id.data, form.s_num.data, 1,
                        form.desc.data, current_user.id, smodel[form.s_id.data].approver_value,
                        strftime("%Y-%m-%d %H:%M", localtime()), form.days.data)
        db.session.add(sapply)
        db.session.commit()
    except:
        flash(u'申请失败', 'error')
        return render_template('apply/new.html', form=form, addition=addition)

    if check_vm_apply(sapply.id):
        if create_vm(sapply.id, sapply.days):
            sapply.status = 6
        else:
            sapply.status = 7

        db.session.add(sapply)
        db.session.commit()

    flash(u'申请提交成功，请等待审核!', 'info')
    return redirect(url_for('.index'))


@mod.route('/<int:apply_id>/ack')
@check_load_apply
def ack(apply, **kvargs):
    apply.status = 4

    db.session.add(apply)
    db.session.commit()

    return redirect(url_for('.index'))


@mod.route('/<int:apply_id>/cancle')
@check_load_apply
def cancle(apply, **kvargs):
    apply.status = 5

    server = Server.query.filter(Server.apply_id == apply.id)

    for s in server:
        if s.vm_id != None:
            req = urllib2.Request("%s/%d" % (app.config['APC_URL'], s.vm_id))
            req.add_header('Authorization', app.config['APC_AUTH'])
            req.get_method = lambda: 'DELETE'
            urllib2.urlopen(req)

    db.session.add(apply)
    db.session.commit()

    return redirect(url_for('.index'))


class SapplyForm(Form):
    name = TextField(u'简述', validators=[required(), length(max=64)])
    s_id = SelectField(u'机器型号', coerce=int, validators=[required()])
    s_num = TextField(u'数量', validators=[required(), regexp(u'^[0-9]+$'), length(max=11)])
    status = TextField(u'状态', validators=[])
    desc = TextAreaField(u'描述', validators=[])
    days = TextField(u'天数', validators=[regexp(u'^[0-9]*$')])
