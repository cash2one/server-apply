from flask.ext.login import UserMixin, current_user

from sqlalchemy import *

from sa import app, db, db1


class User(UserMixin):
    def __init__(self, id, username, chinese_name, email, if_admin, if_approver, if_idc):
        self.id = id
        self.username = username
        self.chinese_name = chinese_name
        self.email = email
        self.if_admin = if_admin
        self.if_approver = if_approver
        self.if_idc = if_idc


class UserDB(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    chinese_name = Column(String)
    email = Column(String)
    if_admin = Column(Enum('yes','no'))
    if_approver = Column(Enum('yes','no'))
    if_idc = Column(Enum('yes','no'))
    ssh_pubkey = Column(Text)

    def __init__(self, username, chinese_name, email, if_admin, if_approver, if_idc, ssh_pubkey):
        self.username = username
        self.chinese_name = chinese_name
        self.email = email
        self.if_admin = if_admin
        self.if_approver = if_approver
        self.if_idc = if_idc
        self.ssh_pubkey = ssh_pubkey


class Stype(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    if_t = Column(Enum('yes','no'))

    def __init__(self, name, if_t):
        self.name = name
        self.if_t = if_t


class Smodel(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    stype_id = Column(Integer)
    cpucores = Column(Integer)
    memsize = Column(Integer)
    disk = Column(String)
    if_v = Column(Enum('yes','no'))
    template = Column(Text)
    approver_id = Column(Integer)

    def __init__(self, name, stype_id, cpucores, memsize, disk, if_v, template, approver_id):
        self.name = name
        self.stype_id = stype_id
        self.cpucores = cpucores
        self.memsize = memsize
        self.disk = disk
        self.if_v = if_v
        self.template = template
        self.approver_id = approver_id


class Sapply(db.Model):
    __tablename__ = 'apply'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    s_id = Column(Integer)
    s_num = Column(Integer)
    status = Column(String)
    applier = Column(String)
    approver = Column(String)
    apply_date = Column(DateTime)
    days = Column(Integer)

    def __init__(self, name, s_id, s_num, status, applier, approver, apply_date, days):
        self.name = name
        self.s_id = s_id
        self.s_num = s_num
        self.status = status
        self.applier = applier
        self.approver = approver
        self.apply_date = apply_date
        self.days = days


class Approver(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(String)

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Server(db.Model):
    id = Column(Integer, primary_key=True)
    apply_id = Column(Integer)
    zeus_id = Column(Integer)
    vm_id = Column(Integer)
    if_t = Column(Enum('yes','no'))
    days = Column(Integer)
    create_time = Column(DateTime)
    applier = Column(String)
    notify = Column(Integer)

    def __init__(self, apply_id, zeus_id, vm_id, if_t, days, create_time, applier, notify):
        self.apply_id = apply_id
        self.zeus_id = zeus_id
        self.vm_id = vm_id
        self.if_t = if_t
        self.days = days
        self.create_time = create_time
        self.applier = applier
        self.notify = notify


class Comment(db.Model):
    id = Column(Integer, primary_key=True)
    apply_id = Column(Integer)
    msg = Column(Text)
    comment_time = Column(DateTime)
    user = Column(String)

    def __init__(self, apply_id, msg, comment_time, user):
        self.apply_id = apply_id
        self.msg = msg
        self.comment_time = comment_time
        self.user = user


class ZeusItem(db.Model):
    __tablename__ = 'item'
    __bind_key__ = 'zeus'
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer)
    rackmountable = Column(Integer)
    agent_id = Column(Integer)
    servicetag = Column(String)
    label = Column(String)
    raid_id = Column(Integer)
    status_id = Column(Integer)
    location_id = Column(Integer)
    user_id = Column(Integer)
    owner_id = Column(Integer)
    application = Column(String)

    def __init__(self, type_id, rackmountable, agent_id, servicetag, label, raid_id, status_id, location_id, user_id, owner_id, application):
        self.type_id = type_id
        self.rackmountable = rackmountable
        self.agent_id = agent_id
        self.servicetag = servicetag
        self.label = label
        self.raid_id = raid_id
        self.status_id = status_id
        self.location_id = location_id
        self.user_id = user_id
        self.owner_id = owner_id
        self.application = application


class ZeusIP(db.Model):
    __tablename__ = 'ip'
    __bind_key__ = 'zeus'
    id = Column(Integer, primary_key=True)
    ip = Column(String)
    status = Column(Integer)
    updated = Column(Integer)
    subnet_id = Column(Integer)
    item_id = Column(Integer)

    def __init__(self, ip, status, updated, subnet_id, item_id):
        self.ip = ip
        self.status = status
        self.updated = updated
        self.subnet_id = subnet_id
        self.item_id = item_id


class ZeusNetwork(db.Model):
    __tablename__ = 'network'
    __bind_key__ = 'zeus'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)
    mac = Column(String)
    ipv4 = Column(String)
    switchid = Column(Integer)
    switch_port = Column(Integer)
    eth = Column(String)
    sshd = Column(Integer)

    def __init__(self, item_id, mac, ipv4, switchid, switch_port, eth, sshd):
        self.item_id = item_id
        self.mac = mac
        self.ipv4 = ipv4
        self.switchid = switchid
        self.switch_port = switch_port
        self.eth = eth
        self.sshd = sshd


class ZeusUser(db1.Model):
    __tablename__ = 'user'
    __bind_key__ = 'zeus'
    id = Column(Integer, primary_key=True)
    user_name = Column(String)

    def __init__(self, user_name):
        self.user_name = user_name
