#! /usr/bin/env python
# -*- coding: utf-8 -*-

import web
import sys, os
import json
import traceback
import hashlib

import userlist

# privilege
# 0: 没有登陆
# 1: dev|hotfix/user/* 创建分支 dev|hotfix/user/* 删除分支权限
# 2: dev|hotfix/* 创建分支 dev|hotfix/* 删除分支权限
# 3: qa/*分支创建权限， qa/* 分支合并权限
# 4: develop 分支合并权限 
# 5: hotfix, master 合并，打tag权限

# 创建分支权限
# 没有登陆
PRG_BR_CR_GUEST = 0
# dev|hotfix/user/* 创建分支 dev|hotfix/user/* 删除分支权限
PRG_BR_CR_USER = 1
# dev|hotfix/* 创建分支 dev|hotfix/* 删除分支权限
PRG_BR_CR_ANY = 2
# qa/*分支创建权限
PRG_BR_CR_QA = 3
# admin
PRG_BR_CR_ROOT = 100

# 合并分支权限
# 没有登陆
PRG_BR_MG_GUEST = 0
# qa/* 分支合并权限
PRG_BR_MG_QA = 1
# develop 分支合并权限
PRG_BR_MG_DEVELOP = 2
# hotfix, master 合并，打tag权限
PRG_BR_MG_MASTER = 3
# admin
PRG_BR_MG_ROOT = 100

PRG_GUEST = [PRG_BR_CR_GUEST, PRG_BR_MG_GUEST]

class AuthGit:

    # eg
    #USER_LIST = {
    #  user: (passwd, 创建分支权限, 合并分支权限)
    #    }

    USER_LIST = userlist.USER_LIST


    def login(self, u, p):
        user = self.USER_LIST.get(u, None)
        if user == None:
            return False

        passwd = user[0]
        if passwd != hashlib.sha1(p).hexdigest():
            return False


        web.setcookie('user', u, 3600*7)
        web.setcookie('passwd', passwd, 3600*7)

        return True

    def clear_cookie(self):
        web.setcookie('user', '', -1)
        web.setcookie('passwd', '', -1)


    def pricheck(self, u, p):
        user = self.USER_LIST.get(u, None)
        if user == None:
            self.clear_cookie()
            return False

        passwd = user[0]
        if passwd != p:
            self.clear_cookie()


            return False


        return True


    def privilege(self):
        #print web.cookies().get('user')
        #print web.cookies().get('passwd')

        user = self.USER_LIST.get(web.cookies().get('user'), None)

        if user == None:
            return PRG_GUEST

        passwd = user[0]
        #print passwd
        if passwd == web.cookies().get('passwd'):
            return user[1:]
        else:
            return PRG_GUEST

def login(u, p):
    au = AuthGit()
    return au.login(u, p)

def pricheck(u, p):
    au = AuthGit()
    return au.pricheck(u, p)


def privilege(need_pri):
    au = AuthGit()
    p = au.privilege()
    return p[0] >= need_pri[0] and p[1] >= need_pri[1], p


if __name__ == "__main__":
    print 'test'
