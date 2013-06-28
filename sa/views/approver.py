# -*- coding: utf-8 -*-

from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask.ext.login import login_required
from flask.ext.wtf import Form, TextField, Required, length

from sa import db
from sa.models import Approver
from sa.views import *

mod = Blueprint('approver', __name__,  url_prefix='/approver')


@mod.route('/')
@login_required
def index():
    approver = Approver.query.all()
    return render_template('approver/index.html', approver=approver) 


@mod.route('/add', methods=['GET','POST'])
@login_required
def add():
    form = ApproverForm()

    if not form.validate_on_submit():
        return render_template('approver/add.html', form=form)

    approver = Approver(form.name.data, form.value.data)

    try:
        db.session.add(approver)
        db.session.commit()
        flash(u'添加成功', 'success')
    except:
        flash(u'添加失败', 'error')
        return render_template('approver/add.html', form=form)

    return redirect(url_for('.index'))


@mod.route('/<int:approver_id>/edit', methods=['GET','POST'])
@login_required
@check_load_approver
def edit(approver, **kvargs):
    form = ApproverForm(obj=approver)

    if not form.validate_on_submit():
        return render_template('approver/edit.html', form=form, approver=approver)

    try:
        form.populate_obj(approver)
        db.session.add(approver)
        db.session.commit()
    except:
        flash(u'修改失败', 'error')
        return redirect(url_for('.edit', approver_id=approver.id))

    flash(u'修改成功', 'success')
    return redirect(url_for('approver.index'))


@mod.route('/<int:approver_id>/delete', methods=['GET','POST'])
@login_required
@check_load_approver
def delete(approver, **kvargs):
    form = ApproverForm(obj=approver)

    if request.method != 'POST':
        return render_template('approver/delete.html', form=form, approver=approver)

    try:
        db.session.delete(approver)
        db.session.commit()
    except:
        flash(u'删除失败', 'error')
        return redirect(url_for('.delete', approver_id=approver.id))

    flash(u'删除成功', 'success')
    return redirect(url_for('.index'))


class ApproverForm(Form):
    name = TextField(u'名称', validators=[Required(), length(max=32)])
    value = TextField(u'审核流程', validators=[length(max=128)])
