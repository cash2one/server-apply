# -*- coding: utf8 -*-

from os.path import dirname,abspath

# Base config
ROOT_DIR = dirname(abspath(__file__))
DEBUG = True
HOST = "http://gywang.d.corp.anjuke.com"
DNS_SERVER = "192.168.1.100"
PRODUCTION_CONFIG = '%s/config_production.py' % ROOT_DIR


# Auth info
AUTH_URL = 'https://auth.corp.anjuke.com'
AUTH_ID = 'apc_dev'
AUTH_SECRET = 'a6f261de'
REQUEST_TOKEN_URL = AUTH_URL + '/authorize.php?client_id=' + AUTH_ID + '&response_type=code'
ACCESS_TOKEN_URL = AUTH_URL + '/token.php?client_id=' + AUTH_ID + '&client_secret=' + AUTH_SECRET + '&grant_type=authorization_code&code=%s'
RESOURCE_URL = AUTH_URL + '/resource.php'
LOGOUT_URL = AUTH_URL + '/logout.php?client_id=' + AUTH_ID + '&client_secret=' + AUTH_SECRET
SECRET_KEY = "g\xf3\xc3\x9a\x8e\x96jU\xb9;\xc6\xcb\x90\xc4\xf8T\xf4\x93o\x05\x99/g\xe0"


# DB
SQLALCHEMY_DATABASE_URI = 'mysql+oursql://caixh:caixh123@192.168.1.103/sapply'
SQLALCHEMY_BINDS = {
    'zeus': 'mysql+oursql://caixh:caixh123@192.168.1.103/zeus',
}
SQLALCHEMY_POOL_RECYCLE = 7200


# SMTP Server
SMTP_HOST = 'xapp10-048.i.ajkdns.com'
SMTP_PORT = 25
SENDER = 'noreply@dm.anjuke.com'


# APC config
APC_URL = "http://apc10-001.i.ajkdns.com:4567"
APC_AUTH = "Basic b25lYWRtaW46NWJhYTYxZTRjOWI5M2YzZjA2ODIyNTBiNmNmODMzMWI3ZWU2OGZkOA=="


# Apply status
APPLY_STATUS = {
    1:{'name':u'审核中',    'class':u'label-info'},
    2:{'name':u'被驳回',    'class':u'label-important'},
    3:{'name':u'准备中',    'class':u'label-info'},
    4:{'name':u'确认交付',  'class':u'label-success'},
    5:{'name':u'已取消',    'class':u''},
    6:{'name':u'等待验收',  'class':u'label-info'},
    7:{'name':u'创建失败',  'class':u'label-important'}
}
