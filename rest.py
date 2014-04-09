#! /usr/bin/env python
# -*- coding: utf-8 -*-

import web
import sys, os
import json
import DevVcsTool


urls = (
    '/git', 'test',
    '/git/stat/merge', 'MergeStat',
    '/git/branch/(.*)/(.*)', 'Branch',
    '/git/merge/(.*)', 'MergeBranch',
)

app = web.application(urls, globals())


class MergeStat:
    def GET(self):
        res = DevVcsTool.except_wrapper(DevVcsTool.all_merge_stat)
        return json.dumps(res)


class Branch:
    def POST(self, tp, br):
        if tp == 'dv':
            res = DevVcsTool.except_wrapper(DevVcsTool.create_solid_branch, 'develop', 'dev/'+br)

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

        return json.dumps(res)


class MergeBranch:
    def POST(self, tp):

        usr_data = dict(web.input())
        base_br = usr_data['base_br']
        merge_list = usr_data['merge_list']

        #print base_br, merge_list

        merge_list = merge_list.split(',')
        merge_list = [e.strip() for e in merge_list]

        if tp == 'dv':
            res = DevVcsTool.except_wrapper(DevVcsTool.merge_branch, 'develop', merge_list)

        elif tp == 'qa':
            res = DevVcsTool.except_wrapper(DevVcsTool.merge_branch, 'qa/'+base_br, merge_list)

        elif tp == 'hf':
            res = DevVcsTool.except_wrapper(DevVcsTool.merge_branch, 'hotfix/'+base_br, merge_list)

        else:
            res = {'code': 1, 'err': 'err type: '+tp}

        return json.dumps(res)



class test:
    def GET(self):
        return DevVcsTool.tst_fetch()
        # return 'Hello World'


if __name__ == "__main__":
    app.run()
