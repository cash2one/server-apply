# -*- coding: utf-8 -*-

from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask.ext.wtf import Form, TextField, SelectField, Required, length

from sa import db
from sa.models import Stype, Smodel
from sa.views import *

mod = Blueprint('stype', __name__,  url_prefix='/stype')


@mod.route('/add', methods=['GET', 'POST'])
def add():
    form = StypeForm()

    print form.validate_on_submit()

    if not form.validate_on_submit():
        return render_template('stype/add.html', form=form)

    try:
        stype = Stype(form.name.data, form.if_t.data)
        db.session.add(stype)
        db.session.commit()
        flash(u'添加成功', 'success')
    except:
        flash(u'添加失败', 'error')

    return redirect(url_for('smodel.index'))


@mod.route('/<int:stype_id>/edit', methods=['GET', 'POST'])
@check_load_stype
def edit(stype, **kvargs):
    form = StypeForm(obj=stype)

    if not form.validate_on_submit():
        return render_template('stype/edit.html', form=form, stype=stype)

    try:
        form.populate_obj(stype)
        db.session.add(stype)
        db.session.commit()
    except:
        flash(u'修改失败', 'error')
        return redirect(url_for('.edit', stype_id=stype.id))

    flash(u'修改成功', 'success')
    return redirect(url_for('smodel.index'))


@mod.route('/<int:stype_id>/delete', methods=['GET', 'POST'])
@check_load_stype
def delete(stype, **kvargs):
    form = StypeForm(obj=stype)

    if request.method != 'POST':
        return render_template('stype/delete.html', form=form, stype=stype)

    try:
        Smodel.query.filter_by(stype_id=stype.id).delete()
        db.session.delete(stype)
        db.session.commit()
    except:
        flash(u'删除失败', 'error')
        return redirect(url_for('stype.delete', stype_id=stype.id))

    flash(u'删除成功', 'success')
    return redirect(url_for('smodel.index'))


@mod.route('/<int:stype_id>/arrowup', methods=['GET', 'POST'])
@check_load_stype
def arrowup(stype, **kvargs):
    flash(u'arrow up', 'info')
    return redirect(url_for('smodel.index'))


@mod.route('/<int:stype_id>/arrowdown', methods=['GET', 'POST'])
@check_load_stype
def arrowdown(stype, **kvargs):
    flash(u'arrow down', 'info')
    return redirect(url_for('smodel.index'))


class StypeForm(Form):
    name = TextField(u'栏目名称', validators=[Required(), length(max=20)])
    if_t = SelectField(u'是否为测试机', default='0', choices=[('1',u'是'),('0',u'否')], validators=[Required()])
