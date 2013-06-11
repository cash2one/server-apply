# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for
from flask.ext.login import current_user
from sqlalchemy import or_, and_

from sa import app
from sa import db
from sa.getter import get_smodel_by_id, check_vm_apply, create_vm
from sa.models import Sapply
from sa.views import *

mod = Blueprint('approve', __name__,  url_prefix='/approve')


@mod.route('/')
def index():
    appling = Sapply.query.filter(and_(or_(Sapply.approver == current_user.id,
                                           Sapply.approver.like(current_user.id +"->%"),
                                           Sapply.approver.like("%:ok"+ current_user.id),
                                           Sapply.approver.like("%:ok"+ current_user.id +"->%")),
                                       Sapply.status != 0,
                                       Sapply.status != -1)).all()

    applied = Sapply.query.filter(Sapply.approver.like("%"+ current_user.id +":%")).all()

    smodel = get_smodel_by_id()
    return render_template('approve/index.html', appling=appling, applied=applied, smodel=smodel, config=app.config)


@mod.route('/<int:apply_id>/ratify')
@check_load_apply
def ratify(apply, **kvargs):
    apply.approver = apply.approver.replace(current_user.id, current_user.id+':ok')
    apply.status = 3

    db.session.add(apply)
    db.session.commit()

    if check_vm_apply(apply.id):
        if create_vm(apply.id, apply.days):
            apply.status = 6
        else:
            apply.status = 7

        db.session.add(apply)
        db.session.commit()

    return redirect(url_for('.index'))


@mod.route('/<int:apply_id>/deny')
@check_load_apply
def deny(apply, **kvargs):
    apply.approver = apply.approver.replace(current_user.id, current_user.id+':deny')
    apply.status = 2

    db.session.add(apply)
    db.session.commit()

    return redirect(url_for('.index'))
