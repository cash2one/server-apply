# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for
from flask.ext.login import login_required, current_user

import urllib2, simplejson as json

from xml.dom import minidom
from time import localtime, strftime, strptime, mktime, time
from sqlalchemy import and_

from sa import app, db
from sa.models import Server, ZeusItem, ZeusIP, Sapply
from sa.getter import *
from sa.views import *

mod = Blueprint('server', __name__,  url_prefix='/server')


@mod.route('/')
@login_required
@check_admin
def index():
    user_dict = get_user_by_username()
    server = Server.query.all()
    apply = get_apply_by_id()
    smodel = get_smodel_by_id()
    return render_template('server/my.html', server=server, apply=apply, smodel=smodel, user_dict=user_dict, showall=True)


@mod.route('/my')
@login_required
def my():
    server = Server.query.filter(Server.applier==current_user.id)
    apply = get_apply_by_id()
    smodel = get_smodel_by_id()
    return render_template('server/my.html', server=server, apply=apply, smodel=smodel, showall=False)


@mod.route('/check_expired')
def check_expired():
    user_dict = get_user_by_username()
    for s in Server.query.filter(Server.if_t==1):
        create_time = "%s" % s.create_time
        ts_left = s.days*86400  - (mktime(localtime()) - mktime(strptime(create_time, "%Y-%m-%d %H:%M:%S")))
        if ts_left <= 0:
            delete_vm(s.vm_id)
            delete_zeus_item(s.zeus_id)
            db.session.delete(s)
            db.session.commit()
        elif ts_left > 0 and ts_left <= 86400 and not s.notify:
            req = urllib2.Request("%s/compute/%d" % (app.config['APC_URL'], s.vm_id))
            req.add_header('Authorization', app.config['APC_AUTH'])
            result = urllib2.urlopen(req).read()
            xmldoc = minidom.parseString(result)
            ip = [i.firstChild.nodeValue for i in xmldoc.getElementsByTagName('IP')]
            zeusitem = ZeusItem.query.get(s.zeus_id)
            apply = Sapply.query.get(s.apply_id)

            subject = u"您的测试机%s将在1天后删除" % zeusitem.label
            content = u"机器名：%s<br/>\n用途：%s<br/>\nIP：%s<br/>\n链接：%s%s" % (
                        zeusitem.label, apply.name, ', '.join(ip), app.config['HOST'], url_for('server.my'))
            send_mail(user_dict[s.applier].email, subject, content)

            s.notify = 1
            db.session.add(s)
            db.session.commit()

    return strftime('%Y-%m-%d %H:%M:%S', localtime(time()))


@mod.route('/<int:server_id>/getinfo')
@login_required
@check_load_server
def getinfo(server, **kvargs):
    ret = {}
    ret['ip'] = []
    ret['create_time'] = "%s" % server.create_time
    ret['if_t'] = server.if_t

    zeusitem = ZeusItem.query.get(server.zeus_id)
    ret['name'] = zeusitem.label

    if server.vm_id == None: 
        ret['type'] = "物理机"
        ret['state'] = "--"
        ret['ip'] = [z.ip for z in ZeusIP.query.filter(ZeusIP.item_id==server.zeus_id).all()]
    else:
        ret['type'] = "虚拟机"

        req = urllib2.Request("%s/compute/%d" % (app.config['APC_URL'], server.vm_id))
        req.add_header('Authorization', app.config['APC_AUTH'])
        result = urllib2.urlopen(req).read()
        xmldoc = minidom.parseString(result)

        if ret['name']=='':
            ret['name'] = xmldoc.getElementsByTagName('NAME')[0].firstChild.nodeValue
        ret['state'] = xmldoc.getElementsByTagName('STATE')[0].firstChild.nodeValue
        ret['ip'] = [ip.firstChild.nodeValue for ip in xmldoc.getElementsByTagName('IP')]

        if server.if_t:
            daysleft_ts = server.days*86400  - (mktime(localtime()) - mktime(strptime(ret['create_time'], "%Y-%m-%d %H:%M:%S")))
            if daysleft_ts < 0:
                daysleft_day = 0
                daysleft_hour = 0
                daysleft_min = 0
            else:
                daysleft_day = int(daysleft_ts/86400)
                daysleft_hour = int((daysleft_ts%86400)/3600)
                daysleft_min = int(((daysleft_ts%86400)%3600)/60)
            ret['daysleft']  = "%s天%s小时%s分" % (daysleft_day, daysleft_hour, daysleft_min)
            if daysleft_ts <= 86400:
                ret['daysleft'] = "<font color=\"red\">%s</font>" % ret['daysleft']
    
    return json.dumps(ret)


@mod.route('/<int:server_id>/renew')
@login_required
@check_load_server
def renew(server, **kvargs):
    if server.applier!=current_user.username:
        abort(403)

    create_time = "%s" % server.create_time
    daysleft_ts = server.days*86400  - (mktime(localtime()) - mktime(strptime(create_time, "%Y-%m-%d %H:%M:%S")))

    try:
        renew_days = int(request.args.get('days'))
    except:
        return redirect(url_for('.my'))

    if daysleft_ts+86400*renew_days > 86400*30:
        flash(u'最大天数不可以超过30天', 'warning')
    else:
        server.days += renew_days
        server.notify = 0
        db.session.add(server)
        db.session.commit()
        flash(u'续期成功', 'success')

    return redirect(url_for('.my'))


@mod.route('/<int:server_id>/delete')
@login_required
@check_load_server
def delete(server, **kvargs):
    if server.applier!=current_user.username:
        abort(403)

    if server.if_t:
        delete_vm(server.vm_id)
        delete_zeus_item(server.zeus_id)
        db.session.delete(server)
        db.session.commit()

    return redirect(request.headers.get('Referer'))


@mod.route('/<int:server_id>/startvnc', methods=['POST'])
@login_required
@check_load_server
def startvnc(server, **kvargs):
    if server.applier!=current_user.username and not current_user.if_admin:
        abort(403)

    req = urllib2.Request("%s/ui/startvnc/%d" % (app.config['APC_URL'], server.vm_id))
    req.add_header('Authorization', app.config['APC_AUTH'])
    req.get_method = lambda: 'POST'
    result = urllib2.urlopen(req).read()

    return result
