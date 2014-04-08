#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import commands
import traceback
import uuid

class ShellCmdError(Exception):
    def __init__(self, cmd, code, err):
        self.cmd = cmd
        self.code = code
        self.err = err

    def __str__(self):
        return 'Do shell:[%s] code:%d err:\n%s' % (self.cmd, self.code, self.err)

    def info(self):
        return {'cmd': self.cmd, 'code': self.code, 'err': self.err }



class DevVcsTool:
    ERR_CODE_OK = 0
    ERR_CODE_REMOTE_BRANCH_LIST = 1

    def __init__(self, rep = 'origin'):
        self.rep = rep

    def do_cmd(self, cmd):
        print cmd
        # commands.getstatusoutput(cmd)
        # Execute the string cmd in a shell with os.popen() and return a 2-tuple (status, output).
        # cmd is actually run as { cmd ; } 2>&1, so that the  returned output will contain output or error messages.
        # A trailing newline is stripped from the output. The exit status for the command can be interpreted according
        # to the rules for the C function wait().
        return commands.getstatusoutput(cmd)
        #print info[1]

    def do_cmd_except(self, cmd):
        res = self.do_cmd(cmd)
        if res[0] != 0:
            raise ShellCmdError(cmd, res[0], res[1])
        #print res[1]
        return res[1]


    # do fetch, sync local repo
    def fetch(self):
        cmd = 'git fetch %s' % (self.rep, )
        self.do_cmd_except(cmd)

        cmd = 'git remote prune %s' % (self.rep, )
        self.do_cmd_except(cmd)

    # get remote branchs for the begin of 'pref'
    def remote_branch_list(self, pref):
        #cmd = 'git ls-remote --heads %s %s' % (self.rep, pref)
        cmd = 'git branch --remote --list %s/%s' % (self.rep, pref)
        return self.do_cmd_except(cmd)


    def parse_remote_branch_list(self, branch_list):
        brs = branch_list.splitlines()
        filt_head = '%s/HEAD ->' % (self.rep, )
        brs = [e.strip()[len(self.rep)+1:] for e in brs if filt_head not in e]
        return brs

    def parse_local_branch_list(self, branch_list):
        brs = branch_list.splitlines()
        brs = [e.strip() for e in brs]
        return brs


    def del_local_branch(self, pref):
        cmd = 'git branch --list %s' % (pref, )
        brs = self.do_cmd_except(cmd)
        brs = self.parse_local_branch_list(brs)
        for b in brs:
            #print b
            if b[0] == '*': continue

            cmd = 'git branch -D %s' % (b, )
            self.do_cmd_except(cmd)



    # tools, must call self.fetch

    # check the merge state of pref branch and some other pref branch
    def cmp_pref_branch_pref_branch(self, pref0, pref1, need_fetch):
        if need_fetch: self.fetch()

        base_brs = self.remote_branch_list(pref0)
        cmp_brs = self.remote_branch_list(pref1)

        base_brs = self.parse_remote_branch_list(base_brs)
        cmp_brs = self.parse_remote_branch_list(cmp_brs)

        rv = {}

        cmd_format = 'git log %s/%s..%s/%s --no-merges --pretty=format:"%%h %%ar %%an %%s"'
        for b_b in base_brs:
            rv[b_b] = {}
            for c_b in cmp_brs:
                cmd = cmd_format % (self.rep, b_b, self.rep, c_b)
                rv[b_b][c_b] = self.do_cmd_except(cmd)

        return rv

    # del remote branch
    def del_remote_branch(self, branch):
        cmd = 'git push %s :%s' % (self.rep, branch)
        return self.do_cmd_except(cmd)

    # merge branch
    def merge_branch(self, base_br, merge_br_list, is_forth_push = False):
        #self.fetch()
        self.del_local_branch('tmp/*')

        br_id = uuid.uuid1()
        #print br_id
        cmd = 'git checkout -b tmp/%s/%s %s/%s' % (br_id, base_br, self.rep, base_br)
        #print cmd
        self.do_cmd_except(cmd)
        cmd = 'git merge --no-commit --no-ff'
        for b in merge_br_list:
            cmd = '%s %s/%s' % (cmd, self.rep, b)

        info = self.do_cmd_except(cmd)
        if info == 'Already up-to-date.':
            return {'merge': info, }

        
        cmd = 'git merge --abort'
        self.do_cmd_except(cmd)
        cmd = 'git merge --no-ff'
        for b in merge_br_list:
            cmd = '%s %s/%s' % (cmd, self.rep, b)

        merge_info = self.do_cmd_except(cmd)

        forth_push_argu = ''
        if is_forth_push:
            forth_push_argu = ' -f'
        cmd = 'git push%s %s HEAD:%s' % (forth_push_argu, self.rep, base_br)

        push_info = self.do_cmd_except(cmd)
        return {'merge': merge_info, 'push': push_info}


# =======================================
def merge_stat(base_br, cmp_br, need_fetch):
    try:
        dvt = DevVcsTool('origin')
        return dvt.cmp_pref_branch_pref_branch(base_br, cmp_br, need_fetch)


    except ShellCmdError as e:
        return e.info()
        #traceback.print_exc()


def collect_stat(dev_stat, base_stat, res_cmp):
    for e in res_cmp:
        base_stat[e] = []
        for b in res_cmp[e]:
            if b not in dev_stat: dev_stat[b] = []

            if len(res_cmp[e][b]) == 0:
                base_stat[e].append(b)
                dev_stat[b].append(e)


def collect_nomerge_stat(res_cmp):
    base_stat = {}
    for e in res_cmp:
        base_stat[e] = {}
        for b in res_cmp[e]:
            if len(res_cmp[e][b]) > 0:
                base_stat[e][b] = res_cmp[e][b]

    return base_stat


def all_merge_stat():
    # 检查当前状态所有的dev分支所处的发布状态
    # 以及，qa/* develop 已经合并的dev分支
    res_qa = merge_stat('qa/*', 'dev/*', False)
    res_develop = merge_stat('develop', 'dev/*', False)
    res_deploy = merge_stat('deploy', 'dev/*', False)
    res_master = merge_stat('master', 'dev/*', False)

    # 检查develop的功能有多少没有进入deploy
    res_nomerge_dev = merge_stat('deploy', 'develop', False)

    # 检查deploy的功能有多少没有进入master
    res_nomerge_dep = merge_stat('master', 'deploy', False)


    dev_stat = {}
    cmp_qa = {}
    cmp_dev = {}

    collect_stat(dev_stat, cmp_qa, res_qa)
    collect_stat(dev_stat, cmp_dev, res_develop)

    cmp_tmp = {}
    collect_stat(dev_stat, cmp_tmp, res_deploy)
    cmp_tmp = {}
    collect_stat(dev_stat, cmp_tmp, res_master)

    #print cmp_dev
    #print dev_stat

    ###############
    nomerge_dev_stat = collect_nomerge_stat(res_nomerge_dev)
    nomerge_dep_stat = collect_nomerge_stat(res_nomerge_dep)
    #print dev_stat

    #print nomerge_dev_stat
    #print nomerge_dep_stat
    return  {'dev_stat': dev_stat,
             'cmp_qa': cmp_qa,
             'cmp_dev': cmp_dev,
             'nomerge_dev_stat': nomerge_dev_stat,
             'nomerge_dep_stat': nomerge_dep_stat,
             }



# =======================================
def tst_del_remote_br():
    try:
        dvt = DevVcsTool('origin')
        res = dvt.del_remote_branch('devtool/test')
        print res

    except ShellCmdError as e:
        print e



def tst2():
    try:
        dvt = DevVcsTool('origin')
        res = dvt.merge_branch('devtool/test', ['master', 'dev/congming_test'])
        for r in res:
            print r
            print res[r]

    except ShellCmdError as e:
        print e



def tst_fetch():
    try:
        dvt = DevVcsTool('origind')
        res = dvt.fetch()
        return res

    except ShellCmdError as e:
        return e


def tst():
    try:
        dvt = DevVcsTool('origin')
        #res = dvt.cmp_pref_branch_pref_branch('qa/*', 'dev/feature/*')
        res = dvt.cmp_pref_branch_pref_branch('*', '*')
        #res = dvt.remote_branch_list('dev/*')
        #res = dvt.fetch()
        for i in res:
            print "==========%s==========" % (i, )
            for j in res[i]:
                print "--------%s----------" % (j, )
                print res[i][j]

    except ShellCmdError as e:
        print e
        #traceback.print_exc()


if __name__ == "__main__":
    #tst()
    #tst2()
    #tst_del_remote_br()
    all_merge_stat()

