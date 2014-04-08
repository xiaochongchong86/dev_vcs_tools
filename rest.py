#! /usr/bin/env python
# -*- coding: utf-8 -*-

import web
import sys, os
import json
import DevVcsTool


urls = (
    '/git', 'test',
    '/git/stat/merge/qa', 'QaMergeStat',
    '/git/stat/merge/dev', 'DevMergeStat',
    '/git/stat/merge/deploy', 'DeployMergeStat',
    '/git/stat/merge/master', 'MasterMergeStat',
    '/git/stat/merge', 'MergeStat',
)

app = web.application(urls, globals())


class MergeStat:
    def GET(self):
        res = DevVcsTool.all_merge_stat()
        return json.dumps(res)


class QaMergeStat:
    def GET(self):
        res = DevVcsTool.merge_stat('qa/*', 'dev/*')
        return json.dumps(res)

class DevMergeStat:
    def GET(self):
        res = DevVcsTool.merge_stat('develop', 'dev/*')
        return json.dumps(res)

class DeployMergeStat:
    def GET(self):
        res = DevVcsTool.merge_stat('deploy/*', 'develop')
        return json.dumps(res)


class MasterMergeStat:
    def GET(self):
        res = DevVcsTool.merge_stat('master', 'deploy/*')
        return json.dumps(res)



class test:
    def GET(self):
        return DevVcsTool.tst_fetch()
        # return 'Hello World'


if __name__ == "__main__":
    app.run()
