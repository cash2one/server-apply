# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, redirect, url_for
from flask.ext.login import login_required

import urllib2, simplejson as json

from xml.dom import minidom
from time import localtime, strftime, strptime, mktime
from sqlalchemy import and_

from sa import app, db
from sa.models import Server, ZeusItem, ZeusIP
from sa.getter import *
from sa.views import *

mod = Blueprint('server', __name__,  url_prefix='/server')


@mod.route('/my')
@login_required
def my():
    server = Server.query.filter(Server.applier==current_user.id)
    apply = get_apply_by_id()
    smodel = get_smodel_by_id()
    return render_template('server/my.html', server=server, apply=apply, smodel=smodel)


@mod.route('/check_expired')
def check_expired():
    ret = "ok"
    server_t = Server.query.filter(Server.if_t==1).all()

    for st in server_t:
        create_time = "%s" % st.create_time
        if st.days*86400  - (mktime(localtime()) - mktime(strptime(create_time, "%Y-%m-%d %H:%M:%S"))) < 0:
            delete_vm(st.vm_id)
            delete_zeus_item(st.zeus_id)

    return ret


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

        req = urllib2.Request("%s/%d" % (app.config['APC_URL'], server.vm_id))
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
    
    return json.dumps(ret)


@mod.route('/<int:server_id>/renew')
@login_required
@check_load_server
def renew(server, **kvargs):
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
        db.session.add(server)
        db.session.commit()
        flash(u'续期成功', 'success')

    return redirect(url_for('.my'))


@mod.route('/<int:server_id>/delete')
@login_required
@check_load_server
def delete(server, **kvargs):
    if server.if_t:
        delete_vm(server.vm_id)
        delete_zeus_item(server.zeus_id)
        db.session.delete(server)
        db.session.commit()

    return redirect(request.headers.get('Referer'))
