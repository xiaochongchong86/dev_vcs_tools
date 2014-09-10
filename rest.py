#! /usr/bin/env python
# -*- coding: utf-8 -*-

import web
import sys, os
import json
import commands
import traceback
import DevVcsTool
import auth
from UsrException import *


urls = (
    '/git', 'test',
    '/git/login', 'Login',
    '/git/stage', 'DoStage',
    '/git/pricheck', 'PriCheck',
    '/git/stat/merge', 'MergeStat',
    '/git/branch/(.*)', 'Branch',
    '/git/merge/(.*)', 'MergeBranch',
    '/git/mergecheck/(.*)', 'MergeCheck',
    '/git/branch/heads', 'BranchHeads',
)

app = web.application(urls, globals())


def privilege_check(cr = auth.PRG_BR_CR_GUEST, mg = auth.PRG_BR_MG_GUEST):
    need_p = [cr, mg]
    ep, now_p = auth.privilege(need_p)
    if not ep:
        raise PrivilegeError(need_p, now_p)




class MergeStat:
    def GET(self):
        return traceback_wrapper(self.do_GET)

    def do_GET(self):
        privilege_check()
        return DevVcsTool.all_merge_stat()


class Branch:
    def check_create_prg(self, tp, br):
        user = web.cookies().get('user')
        if user == None:
            privilege_check(auth.PRG_BR_CR_ANY)

        user_br_path = user+'/'

        if tp == 'dv' or tp == 'hf' or tp == 'cqa':
            if user_br_path == br[:len(user_br_path)]:
                privilege_check(auth.PRG_BR_CR_USER)
            else:
                privilege_check(auth.PRG_BR_CR_ANY)

        elif tp == 'qa':
            privilege_check(auth.PRG_BR_CR_QA)

        elif tp == 'qapri':
            privilege_check(auth.PRG_BR_CR_QAPRI)


        else:
            privilege_check(auth.PRG_BR_CR_ROOT)


    #def DELETE(self, tp):
    #    return traceback_wrapper(self.do_DELETE, tp)


    def do_DELETE(self, tp):
        #print tp, br
        usr_data = dict(web.input())

        print usr_data
        usr_data = dict(web.input())
        base_br = usr_data['base_br']
        br = usr_data['new_br']


        self.check_create_prg(tp, br)
        if tp == 'dv':
            res = DevVcsTool.delete_solid_branch('dev/'+br)

        elif tp == 'qa':
            res = DevVcsTool.delete_solid_branch('qa/'+br)

        elif tp == 'qapri':
            res = DevVcsTool.delete_solid_branch('qapri/'+br)

        elif tp == 'cqa':
            res = DevVcsTool.delete_solid_branch('conflict/qa/'+br)


        elif tp == 'hf':
            res = DevVcsTool.delete_solid_branch('hotfix/'+br)


        else:
            raise OtherError('err type: '+tp)

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
            res = DevVcsTool.create_solid_branch(base_br, 'dev/'+br)

        elif tp == 'qa':
            res = DevVcsTool.create_solid_branch(base_br, 'qa/'+br)

        elif tp == 'qapri':
            res = DevVcsTool.create_solid_branch(base_br, 'qapri/'+br)

        elif tp == 'cqa':
            res = DevVcsTool.create_solid_branch(base_br, 'conflict/qa/'+br)


        elif tp == 'hf':
            res = DevVcsTool.create_solid_branch('master', 'hotfix/'+br)

        #elif tp == 'rl':
        #    res = traceback_wrapper(DevVcsTool.create_solid_branch, 'develop', 'release/version-'+br)


        #elif tp == 'dp':
        #    res = traceback_wrapper(DevVcsTool.create_solid_branch, 'release/version-'+br, 'develop', True)


        else:
            raise OtherError('err type: '+tp)

        return res

class DoStage:
    def POST(self):
        return traceback_wrapper(self.do_POST)


    def do_POST(self):
        privilege_check(auth.PRG_BR_CR_GUEST, auth.PRG_BR_MG_DEVELOP)
        cmd = 'ssh -T jump "sudo sh /root/scripts/stage_pulish.sh"'
        res = commands.getstatusoutput(cmd)
        print res
        if res[0] != 0:
            raise ShellCmdError(cmd, res[0], res[1])

        return unicode(res[1], 'utf-8', errors='ignore')


class MergeBranch:
    def check_create_prg(self, tp):

        if tp == 'qa':
            privilege_check(auth.PRG_BR_CR_GUEST, auth.PRG_BR_MG_QA)

        elif tp == 'qapri':
            privilege_check(auth.PRG_BR_CR_GUEST, auth.PRG_BR_MG_QAPRI)

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
            res = DevVcsTool.merge_branch('develop', merge_list, merge_info, '')

        elif tp == 'qa':
            res = DevVcsTool.merge_branch('qa/'+base_br, merge_list, merge_info, '')

        elif tp == 'qapri':
            res = DevVcsTool.merge_branch('qapri/'+base_br, merge_list, merge_info, '')


        elif tp == 'hf':
            merge_br = 'hotfix/'+usr_data['merge_list']
            res = DevVcsTool.merge_hotfix_branch([merge_br, ], merge_info, merge_tag)

        elif tp == 'ms':
            merge_br = 'release/version-'+usr_data['merge_list']
            res = DevVcsTool.merge_branch('master', [merge_br, ], merge_info, merge_tag)

        elif tp == 'ms2':
            res = DevVcsTool.merge_branch('master', ['develop', ], merge_info, merge_tag)


        else:
            raise OtherError('err type: '+tp)

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
            res = DevVcsTool.check_merge_branch('develop', merge_list)

        elif tp == 'qa':
            res = DevVcsTool.check_merge_branch('qa/'+base_br, merge_list)

        elif tp == 'qapri':
            res = DevVcsTool.check_merge_branch('qapri/'+base_br, merge_list)


        elif tp == 'hf':
            merge_br = 'hotfix/'+usr_data['merge_list']
            res = DevVcsTool.check_merge_branch(base_br, [merge_br, ])

        elif tp == 'ms':
            merge_br = 'release/version-'+usr_data['merge_list']
            res = DevVcsTool.check_merge_branch('master', [merge_br, ])

        elif tp == 'ms2':
            res = DevVcsTool.check_merge_branch('master', ['develop', ])


        else:
            raise OtherError('err type: '+tp)

        return res

class Login:
    def POST(self):
        return traceback_wrapper(self.do_POST)


    def do_POST(self):
        usr_data = dict(web.input())
        user = usr_data['user']
        passwd = usr_data['passwd']

        if auth.login(user, passwd):
            return 'ok'

        else:
            raise OtherError('err passwd')


class PriCheck:
    def POST(self):
        return traceback_wrapper(self.do_POST)


    def do_POST(self):
        user = web.cookies().get('user')
        passwd = web.cookies().get('passwd')


        if auth.pricheck(user, passwd):
            return  user

        else:
            raise OtherError('invalid token')



class test:
    def GET(self):
        return DevVcsTool.tst_fetch()
        # return 'Hello World'


if __name__ == "__main__":
    app.run()
