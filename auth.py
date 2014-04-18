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

PRG_GUEST = 0
PRG_BRANCH_CREATE_USER = 1
PRG_BRANCH_CREATE_ANY = 2
PRG_BRANCH_QA = 3
PRG_BRANCH_DEVELOP = 4
PRG_BRANCH_MASTER = 5

PRG_ROOT = 100

class AuthGit:



    USER_LIST = userlist.USER_LIST


    def login(self, u, p):
        user = self.USER_LIST.get(u, None)
        if user == None:
            return False

        passwd = hashlib.sha1(user[0]).hexdigest()
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

        passwd = hashlib.sha1(user[0]).hexdigest()
        if passwd != p:
            self.clear_cookie()


            return False


        return True


    def privilege(self):
        #print web.cookies().get('user')
        #print web.cookies().get('passwd')

        user = self.USER_LIST.get(web.cookies().get('user'), None)

        if user == None:
            return 0

        passwd = hashlib.sha1(user[0]).hexdigest()
        #print passwd
        if passwd == web.cookies().get('passwd'):
            return user[1]
        else:
            return 0

def login(u, p):
    au = AuthGit()
    return au.login(u, p)

def pricheck(u, p):
    au = AuthGit()
    return au.pricheck(u, p)


def privilege(need_pri):
    au = AuthGit()
    p = au.privilege()
    return p >= need_pri, p


if __name__ == "__main__":
    print 'test'
