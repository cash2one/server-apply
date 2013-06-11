# -*- coding: utf-8 -*-

from flask import flash

from functools import wraps

from sa.models import Stype, Smodel, Sapply, Approver, Server

#
# Check and load data by id
#
def check_load_stype(func):
    @wraps(func)
    def wrapper(**kvargs):
        stype = Stype.query.get_or_404(kvargs['stype_id'])
        return func(stype=stype, **kvargs)
    return wrapper

def check_load_smodel(func):
    @wraps(func)
    def wrapper(**kvargs):
        smodel = Smodel.query.get_or_404(kvargs['smodel_id'])
        return func(smodel=smodel, **kvargs)
    return wrapper

def check_load_approver(func):
    @wraps(func)
    def wrapper(**kvargs):
        approver = Approver.query.get_or_404(kvargs['approver_id'])
        return func(approver=approver, **kvargs)
    return wrapper

def check_load_apply(func):
    @wraps(func)
    def wrapper(**kvargs):
        apply = Sapply.query.get_or_404(kvargs['apply_id'])
        return func(apply=apply, **kvargs)
    return wrapper

def check_load_server(func):
    @wraps(func)
    def wrapper(**kvargs):
        server = Server.query.get_or_404(kvargs['server_id'])
        return func(server=server, **kvargs)
    return wrapper


#
# Check user authority
#
def check_admin(func):
    @wraps(func)
    def wrapper(**kvargs):
        if not current_user.if_admin: return '403'
    return wrapper


