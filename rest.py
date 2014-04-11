#! /usr/bin/env python
# -*- coding: utf-8 -*-

import web
import sys, os
import json
import traceback
import DevVcsTool


urls = (
    '/git', 'test',
    '/git/stat/merge', 'MergeStat',
    '/git/branch/(.*)/(.*)', 'Branch',
    '/git/merge/(.*)', 'MergeBranch',
    '/git/mergecheck/(.*)', 'MergeCheck',
    '/git/branch/heads', 'BranchHeads',
)

app = web.application(urls, globals())

def traceback_wrapper(fun, *args, **kwds):
    try:
        res = fun(*args, **kwds)
    except:
        traceback.print_exc()
        res = { 'code': 2, 'err': traceback.format_exc() }


    return json.dumps(res)


class MergeStat:
    def GET(self):
        return traceback_wrapper(self.do_GET)

    def do_GET(self):
        return DevVcsTool.except_wrapper(DevVcsTool.all_merge_stat)


class Branch:
    def POST(self, tp, br):
        return traceback_wrapper(self.do_POST, tp, br)

    def do_POST(self, tp, br):
        #print tp, br
        post_argu = dict(web.input())

        if tp == 'dv':
            base = 'deploy'
            if 'base' in post_argu: base = post_argu['base']
            res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, base, 'dev/'+br)

        elif tp == 'qa':
            res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, 'develop', 'qa/'+br)

        elif tp == 'hf':
            res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, 'master', 'hotfix/'+br)

        elif tp == 'rl':
            res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, 'develop', 'release/version-'+br)


        elif tp == 'dp':
            res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, 'release/version-'+br, 'deploy', True)


        else:
            res = {'code': 1, 'err': 'err type: '+tp}

        return res


class MergeBranch:
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



class test:
    def GET(self):
        return DevVcsTool.tst_fetch()
        # return 'Hello World'


if __name__ == "__main__":
    app.run()
