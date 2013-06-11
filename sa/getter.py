# -*- coding: utf-8 -*-

from flask import flash, json
from flask.ext.login import current_user

import urllib2, re
from xml.dom import minidom
from time import localtime, strftime

from sa import app
from sa import db
from sa.models import Stype, Smodel, Sapply, Approver, ZeusItem, Server


def get_stype_by_id():
    ret = {}
    stype = Stype.query.all()

    for t in stype:
        ret[t.id] = t

    return ret


def get_approver_by_id():
    ret = {}
    approver = Approver.query.all()

    for a in approver:
        ret[a.id] = a

    return ret


def get_smodel_by_id():
    ret = {}
    stype = get_stype_by_id()
    approver = get_approver_by_id()
    smodel = Smodel.query.all()

    for m in smodel:
      ret[m.id] = m
      ret[m.id].stype_name = stype[m.stype_id].name
      ret[m.id].if_t = stype[m.stype_id].if_t
      try:
        ret[m.id].approver_value = approver[m.approver_id].value
      except:
        ret[m.id].approver_value = None

    return ret


def get_server_by_apply_id():
    ret = {}
    server = Server.query.all()

    for s in server:
        if ret.has_key(s.apply_id):
            ret[s.apply_id].append(s)
        else:
            ret[s.apply_id] = [s]

    return ret


def vm_to_zeus(xml):
    ret = True

    xmldoc = minidom.parseString(xml)
    id = xmldoc.getElementsByTagName('ID')[0].firstChild.nodeValue
    ip = xmldoc.getElementsByTagName('IP')[0].firstChild.nodeValue

    zeusitem = ZeusItem(6, 1, 23, '00-00-00-000', 1)
    db.session.add(zeusitem)
    db.session.commit()

    return zeusitem.id


def check_vm_apply(apply_id):
    ret = True

    apply = Sapply.query.get(apply_id)

    for i in apply.approver.split('->'):
        if i!='':
            if not re.search(':ok', i): ret = False

    if ret:
        apply.status = 3
        db.session.add(apply)
        db.session.commit()

    return ret


def create_vm(apply_id, days):
    ret = True

    apply = Sapply.query.get(apply_id)
    smodel = get_smodel_by_id() 

    params = smodel[apply.s_id].template
    req = urllib2.Request(app.config['APC_URL'], params)
    req.add_header('Authorization', app.config['APC_AUTH'])

    for n in range(1, apply.s_num + 1):
        try:
            result = urllib2.urlopen(req).read()
        except:
            flash(u'创建虚拟机失败', 'error')
            ret = False
            return ret

        xmldoc = minidom.parseString(result)
        vm_id = xmldoc.getElementsByTagName('ID')[0].firstChild.nodeValue
        zeus_id = vm_to_zeus(result)

        server = Server(apply_id, zeus_id, vm_id, smodel[apply.s_id].if_t, 
                        days, strftime("%Y-%m-%d %H:%M", localtime()), current_user.id)
        db.session.add(server)
        db.session.commit()

    return ret


def delete_vm(vm_id):
    ret = {}

    return ret
