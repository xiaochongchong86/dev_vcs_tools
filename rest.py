#! /usr/bin/env python
# -*- coding: utf-8 -*-

import web
import sys, os
import json
import traceback
import DevVcsTool
import auth


urls = (
    '/git', 'test',
    '/git/login', 'Login',
    '/git/pricheck', 'PriCheck',
    '/git/stat/merge', 'MergeStat',
    '/git/branch/(.*)', 'Branch',
    '/git/merge/(.*)', 'MergeBranch',
    '/git/mergecheck/(.*)', 'MergeCheck',
    '/git/branch/heads', 'BranchHeads',
)

app = web.application(urls, globals())


class PrivilegeError(Exception):
    def __init__(self, need_p, now_p):
        self.need_p = need_p
        self.now_p = now_p

    def __str__(self):
        return 'your privilege is not enough, need larger than %s.%s, but now is %s.%s' % (self.need_p[0],
                                                                                           self.need_p[1],
                                                                                           self.now_p[0],
                                                                                           self.now_p[1])


def privilege_check(cr = auth.PRG_BR_CR_GUEST, mg = auth.PRG_BR_MG_GUEST):
    need_p = [cr, mg]
    ep, now_p = auth.privilege(need_p)
    if not ep:
        raise PrivilegeError(need_p, now_p)


def traceback_wrapper(fun, *args, **kwds):
    try:
        res = fun(*args, **kwds)


    except PrivilegeError as e:
        res = {'code': 2, 'err': str(e)}

    except:
        traceback.print_exc()
        res = { 'code': 3, 'err': traceback.format_exc() }


    return json.dumps(res)


class MergeStat:
    def GET(self):
        return traceback_wrapper(self.do_GET)

    def do_GET(self):
        privilege_check()
        return DevVcsTool.except_wrapper(DevVcsTool.all_merge_stat)


class Branch:
    def check_create_prg(self, tp, br):
        user = web.cookies().get('user')
        if user == None:
            privilege_check(auth.PRG_BR_CR_ANY)

        user_br_path = user+'/'

        if tp == 'dv' or tp == 'hf':
            if user_br_path == br[:len(user_br_path)]:
                privilege_check(auth.PRG_BR_CR_USER)
            else:
                privilege_check(auth.PRG_BR_CR_ANY)

        elif tp == 'qa':
            privilege_check(auth.PRG_BR_CR_QA)

        else:
            privilege_check(auth.PRG_BR_CR_ROOT)

    def DELETE(self, tp):
        return traceback_wrapper(self.do_DELETE, tp)


    def do_DELETE(self, tp):
        #print tp, br
        usr_data = dict(web.input())

        print usr_data
        usr_data = dict(web.input())
        base_br = usr_data['base_br']
        br = usr_data['new_br']


        self.check_create_prg(tp, br)
        if tp == 'dv':
            res = DevVcsTool.except_wrapper(DevVcsTool.delete_solid_branch, 'dev/'+br)

        elif tp == 'qa':
            res = DevVcsTool.except_wrapper(DevVcsTool.delete_solid_branch, 'qa/'+br)

        elif tp == 'hf':
            res = DevVcsTool.except_wrapper(DevVcsTool.delete_solid_branch, 'hotfix/'+br)


        else:
            res = {'code': 1, 'err': 'err type: '+tp}

        return res


    def POST(self, tp):
        return traceback_wrapper(self.do_POST, tp)

    def do_POST(self, tp):
        #print tp, br
        usr_data = dict(web.input())
        if usr_data.get('m', '') == 'delete':
            return self.do_DELETE(tp)


        usr_data = dict(web.input())
        base_br = usr_data['base_br']
        br = usr_data['new_br']


        self.check_create_prg(tp, br)
        if tp == 'dv':
            res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, base_br, 'dev/'+br)

        elif tp == 'qa':
            res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, 'develop', 'qa/'+br)

        elif tp == 'hf':
            res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, 'master', 'hotfix/'+br)

        #elif tp == 'rl':
        #    res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, 'develop', 'release/version-'+br)


        #elif tp == 'dp':
        #    res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, 'release/version-'+br, 'develop', True)


        else:
            res = {'code': 1, 'err': 'err type: '+tp}

        return res


class MergeBranch:
    def check_create_prg(self, tp):

        if tp == 'qa':
            privilege_check(auth.PRG_BR_CR_GUEST, auth.PRG_BR_MG_QA)

        elif tp == 'dv':
            privilege_check(auth.PRG_BR_CR_GUEST, auth.PRG_BR_MG_DEVELOP)

        elif tp == 'hf' or tp == 'ms' or tp == 'ms2':
            privilege_check(auth.PRG_BR_CR_GUEST, auth.PRG_BR_MG_MASTER)

        else:
            privilege_check(auth.PRG_BR_CR_GUEST, auth.PRG_BR_MG_ROOT)


    def POST(self, tp):
        return traceback_wrapper(self.do_POST, tp)


    def do_POST(self, tp):

        usr_data = dict(web.input())
        base_br = usr_data['base_br']
        merge_list = usr_data['merge_list']
        merge_info = usr_data.get('merge_info', '')
        merge_tag = usr_data.get('merge_tag', '')
        #print usr_data


        merge_list = merge_list.split(',')
        merge_list = [e.strip() for e in merge_list]


        self.check_create_prg(tp)

        if tp == 'dv':
            res = DevVcsTool.except_wrapper(DevVcsTool.merge_branch, 'develop', merge_list, merge_info, '')

        elif tp == 'qa':
            res = DevVcsTool.except_wrapper(DevVcsTool.merge_branch, 'qa/'+base_br, merge_list, merge_info, '')


        elif tp == 'hf':
            merge_br = 'hotfix/'+usr_data['merge_list']
            res = DevVcsTool.except_wrapper(DevVcsTool.merge_hotfix_branch, [merge_br, ], merge_info, merge_tag)

        elif tp == 'ms':
            merge_br = 'release/version-'+usr_data['merge_list']
            res = DevVcsTool.except_wrapper(DevVcsTool.merge_branch, 'master', [merge_br, ], merge_info, merge_tag)

        elif tp == 'ms2':
            res = DevVcsTool.except_wrapper(DevVcsTool.merge_branch, 'master', ['develop', ], merge_info, merge_tag)


        else:
            res = {'code': 1, 'err': 'err type: '+tp}

        return res



class MergeCheck:
    def POST(self, tp):
        return traceback_wrapper(self.do_POST, tp)

    def do_POST(self, tp):

        usr_data = dict(web.input())
        #print usr_data
        privilege_check()

        base_br = usr_data['base_br']
        merge_list = usr_data['merge_list']


        merge_list = merge_list.split(',')
        merge_list = [e.strip() for e in merge_list]


        if tp == 'dv':
            res = DevVcsTool.except_wrapper(DevVcsTool.check_merge_branch, 'develop', merge_list)

        elif tp == 'qa':
            res = DevVcsTool.except_wrapper(DevVcsTool.check_merge_branch, 'qa/'+base_br, merge_list)

        elif tp == 'hf':
            merge_br = 'hotfix/'+usr_data['merge_list']
            res = DevVcsTool.except_wrapper(DevVcsTool.check_merge_branch, base_br, [merge_br, ])

        elif tp == 'ms':
            merge_br = 'release/version-'+usr_data['merge_list']
            res = DevVcsTool.except_wrapper(DevVcsTool.check_merge_branch, 'master', [merge_br, ])

        elif tp == 'ms2':
            res = DevVcsTool.except_wrapper(DevVcsTool.check_merge_branch, 'master', ['develop', ])


        else:
            res = {'code': 1, 'err': 'err type: '+tp}

        return res

class Login:
    def POST(self):
        return traceback_wrapper(self.do_POST)


    def do_POST(self):
        usr_data = dict(web.input())
        user = usr_data['user']
        passwd = usr_data['passwd']

        if auth.login(user, passwd):
            return  {'code': 0, 'res': 'ok'}

        else:
            return  {'code': 1, 'err': 'err passwd'}


class PriCheck:
    def POST(self):
        return traceback_wrapper(self.do_POST)


    def do_POST(self):
        user = web.cookies().get('user')
        passwd = web.cookies().get('passwd')


        if auth.pricheck(user, passwd):
            return  {'code': 0, 'res': user}

        else:
            return  {'code': 1, 'err': 'invalid token'}



class test:
    def GET(self):
        return DevVcsTool.tst_fetch()
        # return 'Hello World'


if __name__ == "__main__":
    app.run()
