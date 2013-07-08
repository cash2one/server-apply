# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for
from flask.ext.login import current_user, login_required
from sqlalchemy import or_, and_, desc

from sa import app
from sa import db
from sa.getter import *
from sa.models import Sapply
from sa.views import *

mod = Blueprint('approve', __name__,  url_prefix='/approve')


@mod.route('/')
@login_required
@check_approver
def index():
    user_dict = get_user_by_username()
    appling = Sapply.query.filter(and_(or_(Sapply.approver==current_user.id,
                                           Sapply.approver.like(current_user.id +"->%"),
                                           Sapply.approver.like("%:ok"+ current_user.id),
                                           Sapply.approver.like("%:ok"+ current_user.id +"->%")),
                                       Sapply.status==1)).order_by(desc(Sapply.id)).all()

    applied = Sapply.query.filter(Sapply.approver.like("%"+ current_user.id +":%")).order_by(desc(Sapply.id)).all()

    smodel = get_smodel_by_id()
    return render_template('approve/index.html', appling=appling, applied=applied, smodel=smodel, user_dict=user_dict, config=app.config)


@mod.route('/<int:apply_id>/ratify')
@login_required
@check_approver
@check_load_apply
def ratify(apply, **kvargs):
    smodel_dict = get_smodel_by_id()
    apply.approver = apply.approver.replace(current_user.id, current_user.id+':ok')

    if check_apply_status(apply.id):
        if smodel_dict[apply.s_id].if_v:
            apply.status = 6 if create_vm(apply.id, apply.days) else 7
        else:
            subject = "您有新的物理机需求需要处理"
            content = "%s%s" % (app.config['HOST'], url_for('apply.detail', apply_id=apply.id))
            for u in UserDB.query.filter(UserDB.if_idc==1):
                send_mail(u.email, subject, content)

    db.session.add(apply)
    db.session.commit()

    return redirect(url_for('apply.detail', apply_id=apply.id))


@mod.route('/<int:apply_id>/deny')
@login_required
@check_approver
@check_load_apply
def deny(apply, **kvargs):
    apply.approver = apply.approver.replace(current_user.id, current_user.id+':deny')
    apply.status = 2

    db.session.add(apply)
    db.session.commit()

    return redirect(url_for('.index'))
