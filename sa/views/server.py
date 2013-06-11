# -*- coding: utf-8 -*-

from flask import Blueprint, json

import urllib2, simplejson as json

from xml.dom import minidom
from time import localtime, strftime, strptime, mktime

from sa import app
from sa.models import app
from sa.views import *

mod = Blueprint('server', __name__,  url_prefix='/server')


@mod.route('/<int:server_id>/getinfo')
@check_load_server
def getinfo(server, **kvargs):
    ret = {}
    ret['ip'] = []
    ret['create_time'] = "%s" % server.create_time
    ret['if_t'] = server.if_t

    if server.vm_id == None: 
        ret['type'] = "物理机"
    else:
        ret['type'] = "虚拟机"

        req = urllib2.Request("%s/%d" % (app.config['APC_URL'], server.vm_id))
        req.add_header('Authorization', app.config['APC_AUTH'])
        result = urllib2.urlopen(req).read()
        xmldoc = minidom.parseString(result)

        ret['name'] = xmldoc.getElementsByTagName('NAME')[0].firstChild.nodeValue
        ret['state'] = xmldoc.getElementsByTagName('STATE')[0].firstChild.nodeValue

        for ip in xmldoc.getElementsByTagName('IP'):
            ret['ip'].append(ip.firstChild.nodeValue)

        if server.if_t:
            daysused = int((mktime(localtime()) - mktime(strptime(ret['create_time'], "%Y-%m-%d %H:%M:%S")))/86400)
            ret['daysleft']  = server.days - daysused

    return json.dumps(ret)
