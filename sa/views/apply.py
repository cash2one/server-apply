# -*- coding: utf-8 -*-

from flask import Blueprint, flash, url_for, render_template, redirect, request
from flask.ext.login import current_user, login_required
from flask.ext.wtf import Form, TextField, TextAreaField, SelectField, required, length, regexp
from sqlalchemy import desc, or_, and_
from time import localtime, strftime

import urllib2

from sa import app
from sa import db
from sa.getter import *
from sa.models import Stype, Smodel, Sapply, Server, Comment, ZeusItem
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
@login_required
def index():
    smodel_arr = get_smodel_by_id()
    server_arr = get_server_by_apply_id()
    apply = Sapply.query.filter_by(applier=current_user.id).order_by(desc(Sapply.id))
    return render_template('apply/index.html', apply=apply, smodel=smodel_arr, server=server_arr, config=app.config)


@mod.route('/new/smodel/<int:smodel_id>', methods=['GET','POST'])
@login_required
def new(smodel_id, **kvargs):
    form = SapplyForm()
    form.s_id.choices = gen_smodel()

    if request.method != 'POST':
        form.s_id.default = smodel_id
        form.process()

    addition = {}
    addition['smodel_id'] = smodel_id
    addition['referer'] = request.headers.get('Referer') if(request.headers.get('Referer')!=None) else url_for('.index')

    if not form.validate_on_submit():
        return render_template('apply/new.html', form=form, addition=addition)

    smodel = get_smodel_by_id()
    if not smodel[form.s_id.data].if_t:
        form.days.data = -1
    if smodel[form.s_id.data].if_t and form.days.data == '':
        form.days.data = 7
    if form.days.data != '':
        if int(form.days.data) > 30:
            flash(u'最大天数不能超过30天', 'error')
            return render_template('apply/new.html', form=form, addition=addition)

    try:
        sapply = Sapply(form.name.data, form.s_id.data, form.s_num.data, 1,
                        current_user.id, smodel[form.s_id.data].approver_value,
                        strftime("%Y-%m-%d %H:%M:%S", localtime()), form.days.data)
        db.session.add(sapply)
        db.session.commit()
    except:
        flash(u'申请失败', 'error')
        return render_template('apply/new.html', form=form, addition=addition)

    if form.desc.data != "":
        comment = Comment(sapply.id, form.desc.data.replace('\n', '<br/>\n').replace('<', "&lt;").replace('>', "&gt;"),
                          strftime("%Y-%m-%d %H:%M:%S", localtime()), current_user.username)
        db.session.add(comment)
        db.session.commit()

    if check_apply_status(sapply.id):
        if smodel[form.s_id.data].if_v:
            if create_vm(sapply.id, sapply.days):
                sapply.status = 6
            else:
                sapply.status = 7

            db.session.add(sapply)
            db.session.commit()

            flash(u'创建成功，请验收！', 'success')
            return redirect(url_for('.index'))
        else:
            idc_email = [u.email for u in UserDB.query.filter(UserDB.if_idc==1)]
            subject = "您有新的物理机申请需要处理"
            content = "%s%s" % (app.config['HOST'], url_for('apply.detail', apply_id=sapply.id))
            send_mail(idc_email, subject, content)
            

    flash(u'申请提交成功!', 'info')
    return redirect(url_for('.index'))


@mod.route('/<int:apply_id>')
@login_required
@check_load_apply
def detail(apply, **kvargs):
    smodel_dict = get_smodel_by_id()
    user_dict = get_user_by_username()
    server = Server.query.filter(Server.apply_id==apply.id).all()
    comment = Comment.query.filter(Comment.apply_id==apply.id).all()
    flow_arr = []

    for i in apply.approver.split('->'):
      if i!='':
        tmp = {}
        tmp['username'] = i.split(':')[0]
        try:
            tmp['status'] = i.split(':')[1]
        except:
            tmp['status'] = u'undefined'
        flow_arr.append(tmp)

    deny_flag = False
    undefined_flag = False
    flow_arr_show = []

    for f in flow_arr:
        tmp = {}
        tmp['username'] = f['username']

        if deny_flag:
            tmp['status'] = u"空"
            tmp['class'] = ""

        if undefined_flag:
            tmp['status'] = u"待审核"
            tmp['class'] = "label-info"

        if f['status']=="ok":
            tmp['status'] = u"已批准"
            tmp['class'] = "label-success"

        if f['status']=="deny":
            deny_flag = True
            tmp['status'] = u"驳回"
            tmp['class'] = "label-important"

        if f['status']=="undefined" and not deny_flag and not undefined_flag:
            undefined_flag = True
            tmp['status'] = u"审核中"
            tmp['class'] = "label-info"

        flow_arr_show.append(tmp)

    return render_template('apply/detail.html', apply=apply, smodel_dict=smodel_dict, user_dict=user_dict,
                            flow_arr=flow_arr_show, server=server, comment=comment, config=app.config)


@mod.route('/<int:apply_id>/comment', methods=['GET','POST'])
@login_required
@check_load_apply
def comment(apply, **kvargs):
    if request.method != 'POST' or request.form['msg']=="":
        return redirect(url_for('.detail', apply_id=apply.id))

    comment = Comment(apply.id, request.form['msg'].replace('\n', '<br/>\n').replace('<', "&lt;").replace('>', "&gt;"),
                      strftime("%Y-%m-%d %H:%M:%S", localtime()), current_user.username)
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('.detail', apply_id=apply.id))


@mod.route('/<int:apply_id>/recreate_server')
@login_required
@check_admin
@check_load_apply
def recreate_server(apply, **kvargs):
    if create_vm(apply.id, apply.days):
        apply.status = 6
        flash(u'创建成功', 'success')
    else:
        apply.status = 7
        flash(u'创建失败', 'error')
    db.session.add(apply)
    db.session.commit()

    return redirect(url_for('.detail', apply_id=apply.id))
    


@mod.route('/<int:apply_id>/attach_server', methods=['POST'])
@login_required
@check_idc
@check_load_apply
def attach_server(apply, **kvargs):
    zeusitem = ZeusItem.query.filter(ZeusItem.label==request.form['hostname'])
    if zeusitem.count()!=1:
        flash(u'没有找到该资产信息', 'error')
    else:
        server = Server(apply.id, zeusitem[0].id, None, 0, -1, strftime("%Y-%m-%d %H:%M:%S", localtime()), apply.applier, None)
        db.session.add(server)
        db.session.commit()
    return redirect(url_for('.detail', apply_id=apply.id))


@mod.route('/<int:apply_id>/detach_server/<int:server_id>', methods=['GET'])
@login_required
@check_idc
@check_load_apply
@check_load_server
def detach_server(apply, server, **kvargs):
    db.session.delete(server)
    db.session.commit()
    return redirect(url_for('.detail', apply_id=apply.id))


@mod.route('/<int:apply_id>/server_ready')
@login_required
@check_idc
@check_load_apply
def server_ready(apply, **kvargs):
    user_dict = get_user_by_username()

    subject = "您的机器已经准备完毕，请验收"
    content = "%s%s" % (app.config['HOST'], url_for('apply.detail', apply_id=apply.id))
    send_mail(user_dict[apply.applier].email, subject, content)

    apply.status = 6
    db.session.add(apply)
    db.session.commit()

    return redirect(url_for('.detail', apply_id=apply.id))


@mod.route('/<int:apply_id>/ack')
@login_required
@check_load_apply
def ack(apply, **kvargs):
    apply.status = 4

    db.session.add(apply)
    db.session.commit()

    return redirect(url_for('.detail', apply_id=apply.id))


@mod.route('/<int:apply_id>/cancle')
@login_required
@check_load_apply
def cancle(apply, **kvargs):
    apply.status = 5

    for s in Server.query.filter(Server.apply_id == apply.id):
        if s.vm_id == None: continue
        delete_vm(s.vm_id)
        delete_zeus_item(s.zeus_id)

    Server.query.filter(Server.apply_id == apply.id).delete()

    db.session.add(apply)
    db.session.commit()

    return redirect(url_for('.detail', apply_id=apply.id))


@mod.route('/<int:apply_id>/delete')
@login_required
@check_admin
@check_load_apply
def delete(apply, **kvargs):
    for s in Server.query.filter(Server.apply_id == apply.id):
        if s.vm_id == None: continue
        delete_vm(s.vm_id)
        delete_zeus_item(s.zeus_id)

    Server.query.filter(Server.apply_id==apply.id).delete()
    Comment.query.filter(Comment.apply_id==apply.id).delete()

    db.session.delete(apply)
    db.session.commit()

    return redirect(url_for('index'))


class SapplyForm(Form):
    name = TextField(u'简述', validators=[required(), length(max=64)])
    s_id = SelectField(u'机器型号', coerce=int, validators=[required()])
    s_num = TextField(u'数量', validators=[required(), regexp(u'^[0-9]+$'), length(max=11)])
    status = TextField(u'状态', validators=[])
    days = TextField(u'天数', validators=[regexp(u'^[0-9]*$')])
    desc = TextAreaField(u'描述', validators=[])
