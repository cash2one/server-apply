# -*- coding: utf-8 -*-

from flask import flash, json, url_for
from flask.ext.login import current_user

import urllib, hashlib
import urllib2, re
import smtplib, mimetypes
import socket

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.Header import Header
from email.mime.image import MIMEImage
from xml.dom import minidom
from time import localtime, strftime

from sa import app, db
from sa.models import Stype, Smodel, Sapply, Approver, ZeusItem, ZeusIP, ZeusNetwork, ZeusUser, Server, Sapply, UserDB


def get_user_by_username():
    ret = {}

    for u in UserDB.query.all():
        ret[u.username] = u
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(u.email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'s':str(80)})
        ret[u.username].gravatar_url = gravatar_url

    return ret


def get_zeususer_by_username():
    ret = {}
    for u in ZeusUser.query.all():
        ret[u.user_name] = u
    return ret


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


def get_apply_by_id():
    ret = {}
    apply = Sapply.query.all()

    for a in apply:
        ret[a.id] = a

    return ret


def vm_to_zeus(xml, apply):
    user_dict = get_user_by_username()
    zeususer_dict = get_zeususer_by_username()

    xmldoc = minidom.parseString(xml)
    id = xmldoc.getElementsByTagName('ID')[0].firstChild.nodeValue
    ip = xmldoc.getElementsByTagName('IP')[0].firstChild.nodeValue
    name = xmldoc.getElementsByTagName('NAME')[0].firstChild.nodeValue

    if apply.applier not in zeususer_dict:
        zeususer = ZeusUser(apply.applier, user_dict[apply.applier].email, user_dict[apply.applier].chinese_name, 0, 1, 1, 0)
        db.session.add(zeususer)
        db.session.commit()
    zeususer_dict = get_zeususer_by_username()

    zeusitem = ZeusItem(6, 1, 23, '00-00-00-000', name, 1, 21, 2, zeususer_dict[apply.applier].id, zeususer_dict[apply.applier].id, apply.name)
    db.session.add(zeusitem)
    db.session.commit()

    zeusnetwork = ZeusNetwork(zeusitem.id, '', ip, 0, 0, 'eth0', 1)
    db.session.add(zeusnetwork)
    db.session.commit()

    return zeusitem.id


def check_apply_status(apply_id):
    ret = True
    mail_flag = False

    apply = Sapply.query.get(apply_id)
    user_dict = get_user_by_username()
    smodel_dict = get_smodel_by_id()

    for i in apply.approver.split('->'):
        if i=='': continue
        if not re.search(':', i) and not mail_flag:
            mail_flag = True
            mail_title = "您有新的申请需要审批"
            mail_content = u"简述：%s<br/>\n型号：%s -- %s<br/>\n数量：%d<br/>\n申请时间：%s<br/>\n申请人：%s<br/>\n审批入口：<a href=\"%s%s\">%s%s</a>" % (
                           apply.name, smodel_dict[apply.s_id].stype_name, smodel_dict[apply.s_id].name,
                           apply.s_num, apply.apply_date, user_dict[apply.applier].chinese_name,
                           app.config['HOST'], url_for('apply.detail', apply_id=apply.id),
                           app.config['HOST'], url_for('apply.detail', apply_id=apply.id))
            send_mail(user_dict[i].email, mail_title, mail_content)

        if not re.search(':ok', i): ret = False

    if ret:
        apply.status = 3
        db.session.add(apply)
        db.session.commit()

    return ret


def create_vm(apply_id, days):
    ret = True
    smodel = get_smodel_by_id()
    user_dict = get_user_by_username() 

    apply = Sapply.query.get(apply_id)
    server_cnt = Server.query.filter(Server.apply_id==apply.id).count()

    params = smodel[apply.s_id].template
    if smodel[apply.s_id].if_t:
        params = params.replace("ssh_pub_key_here", user_dict[apply.applier].ssh_pubkey)
    req = urllib2.Request("%s/compute" % app.config['APC_URL'], params)
    req.add_header('Authorization', app.config['APC_AUTH'])

    for n in range(1, apply.s_num + 1 - server_cnt):
        try:
            result = urllib2.urlopen(req).read()
        except:
            ret = False
            return ret

        xmldoc = minidom.parseString(result)
        vm_id = xmldoc.getElementsByTagName('ID')[0].firstChild.nodeValue
        zeus_id = vm_to_zeus(result, apply)

        server = Server(apply_id, zeus_id, vm_id, smodel[apply.s_id].if_t, 
                        days, strftime("%Y-%m-%d %H:%M:%S", localtime()), apply.applier, 0)
        db.session.add(server)
        db.session.commit()

    if ret:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((app.config['DNS_SERVER'], 9991))
            sock.send('COMMAND 10')
            sock.close()
        except:
            flash(u'重载DNS失败，请联系管理员！', 'error')
        subject = "您的机器已经创建完毕，请验收"
        content = "%s%s" % (app.config['HOST'], url_for('apply.detail', apply_id=apply.id))
        send_mail(user_dict[apply.applier].email, subject, content)

    return ret


def delete_vm(vm_id):
    try:
        req = urllib2.Request("%s/compute/%d" % (app.config['APC_URL'], vm_id))
        req.add_header('Authorization', app.config['APC_AUTH'])
        req.get_method = lambda: 'DELETE'
        urllib2.urlopen(req)
        return True
    except:
        return False


def delete_zeus_item(zeus_id):
    try:
        ZeusItem.query.filter(ZeusItem.id==zeus_id).delete()
        ZeusNetwork.query.filter(ZeusNetwork.item_id==zeus_id).delete()
        return True
    except:
        return False


def send_mail(receiver, subject, content):
    msg = MIMEMultipart()
    msg['From'] = "%s<%s>" % (Header('服务器申请系统','utf-8'), app.config['SENDER'])
    msg['To'] = receiver
    msg['Subject'] = Header(subject, charset='UTF-8')

    txt = MIMEText(content, _subtype='html',  _charset='UTF-8')
    msg.attach(txt)

    try:
        smtpObj = smtplib.SMTP(app.config['SMTP_HOST'], app.config['SMTP_PORT'])
        smtpObj.sendmail(app.config['SENDER'], receiver, msg.as_string())
        smtpObj.quit()
        return True
    except:
        return False
