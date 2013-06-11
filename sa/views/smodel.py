# -*- coding: utf-8 -*-

from flask import Blueprint, url_for, render_template, redirect, request, flash
from flask.ext.wtf import Form, TextField, RadioField, TextAreaField, SelectField, required, length, regexp

import simplejson as json

from sa import db
from sa.models import Stype, Smodel, Approver
from sa.getter import get_smodel_by_id
from sa.views import *

mod = Blueprint('smodel', __name__,  url_prefix='/smodel')


@mod.route('/')
def index():
    stype = Stype.query.all()
    smodel = Smodel.query.all()
    return render_template('smodel/index.html', stype=stype, smodel=smodel)


@mod.route('/add', methods=['GET','POST'])
def add():
    form = SmodelForm()
    form.stype_id.choices = [(t.id, t.name) for t in Stype.query.all()]
    form.approver_id.choices = [(a.id, a.name) for a in Approver.query.all()]

    if not form.validate_on_submit():
        return render_template('smodel/add.html', form=form)

    try:
        smodel = Smodel(form.name.data, form.stype_id.data, form.cpucores.data, form.memsize.data,
                        form.disk.data, form.if_v.data, form.if_t.data, form.template.data, form.approver_id.data)
        db.session.add(smodel)
        db.session.commit()
    except:
        flash(u'添加失败', 'error')
        return render_template('smodel/add.html', form=form)

    flash(u'添加成功', 'success')
    return redirect(url_for('.index'))


@mod.route('/<int:smodel_id>/edit', methods=['GET','POST'])
@check_load_smodel
def edit(smodel, **kvargs):
    form = SmodelForm(obj=smodel)
    form.stype_id.choices = [(t.id, t.name) for t in Stype.query.all()]
    form.approver_id.choices = [(a.id, a.name) for a in Approver.query.all()]

    if not form.validate_on_submit():
        return render_template('smodel/edit.html', form=form, smodel=smodel)

    try:
        form.populate_obj(smodel)
        db.session.add(smodel)
        db.session.commit()
    except:
        flash(u'修改失败', 'error')
        return redirect(url_for('.edit', smodel_id=smodel.id))

    flash(u'修改成功', 'success')
    return redirect(url_for('.index'))


@mod.route('/<int:smodel_id>/delete', methods=['GET','POST'])
@check_load_smodel
def delete(smodel, **kvargs):
    form = SmodelForm(obj=smodel)
    stype = Stype.query.get(smodel.stype_id)

    if request.method != 'POST':
        return render_template('smodel/delete.html', form=form, smodel=smodel, stype=stype)

    try:
        db.session.delete(smodel)
        db.session.commit()
    except:
        flash(u'删除失败', 'error')
        return redirect(url_for('.delete', smodel_id=smodel.id))

    flash(u'删除成功', 'success')
    return redirect(url_for('.index'))    


@mod.route('/<int:smodel_id>/arrowup')
@check_load_smodel
def arrowup(smodel, **kvargs):
    flash(u'arrow up', 'info')
    return redirect(url_for('.index'))    


@mod.route('/<int:smodel_id>/arrowdown')
@check_load_smodel
def arrowdown(smodel, **kvargs):
    flash(u'arrow down', 'info')
    return redirect(url_for('.index'))    


@mod.route('/<int:smodel_id>/template')
@check_load_smodel
def template(smodel, **kvargs):
    return render_template('smodel/template.html', smodel=smodel)


@mod.route('/<int:smodel_id>/getinfo')
@check_load_smodel
def getinfo(smodel, **kvargs):
    ret = {}

    smodel_all = get_smodel_by_id()
    ret['if_t'] = smodel_all[smodel.id].if_t

    return json.dumps(ret)


class SmodelForm(Form):
    name = TextField(u'型号', validators=[required(), length(max=20)])
    stype_id = SelectField(u'所属栏目', coerce=int, validators=[required()])
    approver_id = SelectField(u'审核流程', coerce=int, validators=[required()])
    cpucores = TextField(u'CPU核数', validators=[required(), regexp(u'^[0-9]+$'), length(max=11)])
    memsize = TextField(u'内存/G', validators=[required(), regexp(u'^[0-9]+$'), length(max=11)])
    disk = TextField(u'磁盘', validators=[required(), length(max=128)])
    if_v = SelectField(u'机器类型', default='0', choices=[('1',u'虚拟机'),('0',u'物理机')], validators=[required()])
    template = TextAreaField(u'模板', validators=[])
