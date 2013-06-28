# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for
from flask.ext.login import current_user, login_required
from sqlalchemy import or_, and_, desc

from sa import app
from sa import db
from sa.getter import *
from sa.models import Sapply
from sa.views import *

mod = Blueprint('idc', __name__,  url_prefix='/idc')


@mod.route('/')
@login_required
@check_idc
def index():
    user_dict = get_user_by_username()
    smodel_dict = get_smodel_by_id()

    apply = Sapply.query.filter(or_(Sapply.status==3, Sapply.status==4, Sapply.status==6)).order_by(desc(Sapply.id)).all()

    return render_template('idc/index.html', apply=apply, smodel_dict=smodel_dict, user_dict=user_dict)
