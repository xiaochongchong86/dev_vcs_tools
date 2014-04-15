#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import commands
import traceback
import uuid
import datetime
import time

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
        #self.is_fetch = False
        self.fetch()
        self.clear_local()
        self.del_local_branch('tmp/*')
        self.heads = self.all_remote_branch_head()

    def do_cmd(self, cmd):
        #cmd = 'export LANG=en_US.utf8 && %s' % (cmd, )
        if isinstance(cmd, unicode):
            cmd = cmd.encode('utf-8')

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

    def get_heads(self):
        return self.heads

    # 清理当前
    def clear_local(self):
        cmd = 'git reset --hard'
        self.do_cmd_except(cmd)
        cmd = 'git clean -xdf'
        self.do_cmd_except(cmd)

    # do fetch, sync local repo
    def fetch(self):
        cmd = 'git fetch %s' % (self.rep, )
        self.do_cmd_except(cmd)

        cmd = 'git remote prune %s' % (self.rep, )
        self.do_cmd_except(cmd)

        #self.is_fetch = True

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

    def create_remote_branch(self, base, branch, is_forth_push = False):
        forth_push_argu = ''
        if is_forth_push:
            forth_push_argu = ' -f'

        cmd = 'git push%s %s %s:%s' % (forth_push_argu, self.rep, base, branch)
        return self.do_cmd_except(cmd)

    def checkout_remote_branch(self, base_br):
        br_id = uuid.uuid1()
        cmd = 'git checkout -b tmp/%s/%s %s/%s' % (br_id, base_br, self.rep, base_br)
        return  self.do_cmd_except(cmd)


    # del remote branch
    def del_remote_branch(self, branch):
        cmd = 'git push %s :%s' % (self.rep, branch)
        return self.do_cmd_except(cmd)


    def do_cmp_branch_list(self, base_brs, cmp_brs, merge_type):
        rv = {}

        merge_type_flag = ''
        if merge_type == 'no_merges':
            merge_type_flag = '--no-merges'
        elif  merge_type == 'merges':
            merge_type_flag = '--merges'

        for b_b in base_brs:
            rv[b_b] = {}
            for c_b in cmp_brs:
                cmd_argu = '%s/%s..%s/%s %s' %  (self.rep, b_b, self.rep, c_b, merge_type_flag)
                rv[b_b][c_b] = self.log_cmd_parse(cmd_argu)

        return rv

    def log_cmd_parse(self, cmd_argu):
        pretty = '--date=raw --pretty=format:"%h %ad %ar %an %s"'
        cmd = 'git log %s %s' % (cmd_argu, pretty)
        logs = self.do_cmd_except(cmd)
        logs = logs.splitlines()
        logs = [e.strip() for e in logs]
        logs = [e.split() for e in logs]
        logs = [(e[0], int(e[1]), ' '.join(e[3:])) for e in logs]

        return logs


    # tools

    def all_remote_branch_head(self):
        all_brs = self.remote_branch_list('*')
        all_brs = self.parse_remote_branch_list(all_brs)

        rv = {}
        for b in all_brs:
                cmd_argu = '%s/%s -1' % (self.rep, b)
                rv[b] = self.log_cmd_parse(cmd_argu)[0]


        return rv


    # check the merge state of pref branch and some other pref branch
    def cmp_pref_branch_pref_branch(self, pref0, pref1, merge_type):

        base_brs = self.remote_branch_list(pref0)
        cmp_brs = self.remote_branch_list(pref1)

        base_brs = self.parse_remote_branch_list(base_brs)
        cmp_brs = self.parse_remote_branch_list(cmp_brs)

        return self.do_cmp_branch_list(base_brs, cmp_brs, merge_type)

    def esc_message(self, msg):
        return msg.replace('\\','\\\\').replace("'","''")


    def recent_tag(self, num):
        cmd = 'git tag -l | head -%s' % (num, )
        tags = self.do_cmd_except(cmd)
        tags = tags.splitlines()
        tags = [e.strip() for e in tags]

        rv = []
        cmd_format = 'git show --quiet --date=local --pretty=format:"%%h %%ad %%ar %%an %%s" %s'
        for t in tags:
            cmd = cmd_format % (t, )
            rv.append(self.do_cmd_except(cmd))

        return rv

    def create_tag(self, tag, info):
        cmd = "git tag -a v%s -m '%s'" % (tag, self.esc_message(info))
        self.do_cmd_except(cmd)
        cmd = 'git push %s tag v%s' % (self.rep, tag)
        # del: git push origin  :refs/tags/*
        return self.do_cmd_except(cmd)

    def create_solid_branch(self, base, branch, is_forth_push = False):
        self.clear_local()
        self.checkout_remote_branch(base)
        return self.create_remote_branch('HEAD', branch, is_forth_push)


    def check_need_merge(self, merge_br_list):
        cmd = 'git branch --remote --list %s/* --merged' % (self.rep, )
        ml = self.do_cmd_except(cmd)
        ml = self.parse_remote_branch_list(ml)
        ml = {}.fromkeys(ml, 1)

        res = []
        for b in merge_br_list:
            if b not in ml:
                res.append(b)

        return res


    # merge branch
    def merge_branch(self, base_br, merge_br_list, merge_info, merge_tag, is_forth_push = False):
        self.clear_local()
        merge_tag = merge_tag.strip()

        self.checkout_remote_branch(base_br)

        merge_br_list = self.check_need_merge(merge_br_list)
        if len(merge_br_list) == 0:
            return {'merge': 'not need merge', 'push': 'not need push'}


        cmd = 'git merge --no-commit --no-ff'
        for b in merge_br_list:
            cmd = '%s %s/%s' % (cmd, self.rep, b)

        info = self.do_cmd_except(cmd)
        # 前面已经检查过，不用merge check_need_merge就应该返回了
        if info == 'Already up-to-date.':
            return {'merge': info, 'push': 'not need push'}

        
        cmd = 'git merge --abort'
        self.do_cmd_except(cmd)

        merge_log = '[merge] [base: %s] [list:' % (base_br, )
        for ml in merge_br_list:
            merge_log = '%s %s' % (merge_log, ml)
        merge_log = '%s] %s' % (merge_log, merge_info)
        merge_log = self.esc_message(merge_log)

        cmd = "git merge --no-ff"
        for b in merge_br_list:
            cmd = '%s %s/%s' % (cmd, self.rep, b)

        cmd = "%s -m '%s'" % (cmd, merge_log)


        merge_res = self.do_cmd_except(cmd)

        forth_push_argu = ''
        if is_forth_push:
            forth_push_argu = ' -f'
        cmd = 'git push%s %s HEAD:%s' % (forth_push_argu, self.rep, base_br)

        push_info = self.do_cmd_except(cmd)

        rv_info = {'merge': merge_res, 'push': push_info}

        if merge_tag != '':
            push_tag = self.create_tag(merge_tag, merge_info)
            rv_info['tag'] = push_tag

        return rv_info


# =======================================

def except_wrapper(fun, *args, **kwds):
    try:
        res = fun(*args, **kwds)
        return {'code': 0, 'res': res}
    except ShellCmdError as e:
        return e.info()

def all_remote_branch_head():
    dvt = DevVcsTool('origin')
    return dvt.all_remote_branch_head()


def merge_branch(base_br, merge_br_list, merge_info, merge_tag):
    dvt = DevVcsTool('origin')
    res = dvt.merge_branch(base_br, merge_br_list, merge_info, merge_tag)
    return {base_br: res}

def merge_hotfix_branch(merge_br_list, merge_info, merge_tag):
    dvt = DevVcsTool('origin')

    res0 = dvt.merge_branch('master', merge_br_list, merge_info, merge_tag)
    res1 = dvt.merge_branch('develop', merge_br_list, merge_info, '')

    return {'master': res0, 'develop': res1}


def create_solid_branch(base, branch, is_forth_push = False):
    dvt = DevVcsTool('origin')
    return dvt.create_solid_branch(base, branch, is_forth_push)



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


def check_merge_branch(base_br, merge_list):
    dvt = DevVcsTool('origin')

    base_br = base_br.split(',')
    base_br = [e.strip() for e in base_br]


    res = dvt.do_cmp_branch_list(base_br, merge_list, '')
    '''
    res = {}
    for br in merge_list:
        tmp = dvt.cmp_pref_branch_pref_branch(base_br, br, '')
        for e in tmp:
            res.setdefault(e, {})
            for ee in tmp[e]:
                res[e].setdefault(ee, {})
                res[e][ee] = tmp[e][ee]
                '''

    return {'stat': res, 'heads': dvt.get_heads()}



def all_merge_stat():
    # 检查当前状态所有的dev分支所处的发布状态
    # 以及，qa/* develop 已经合并的dev分支

    dvt = DevVcsTool('origin')

    res_qa = dvt.cmp_pref_branch_pref_branch('qa/*', 'dev/*', '')
    res_develop = dvt.cmp_pref_branch_pref_branch('develop', 'dev/*', '')
    res_release = dvt.cmp_pref_branch_pref_branch('release/*', 'dev/*', '')
    res_master = dvt.cmp_pref_branch_pref_branch('master', 'dev/*', '')

    # 检查develop的功能有多少没有进入release
    res_nomerge_dev = dvt.cmp_pref_branch_pref_branch('release/*', 'develop', '')

    # 检查release的功能有多少没有进入master
    res_nomerge_dep = dvt.cmp_pref_branch_pref_branch('master', 'release/*', '')

    # 检查develop的功能有多少没有进入master
    res_nomerge_master_dev = dvt.cmp_pref_branch_pref_branch('master', 'develop', '')


    # /dev/* 下的分支合并情况
    dev_stat = {}
    # /dev/* 和 /qa/* 对比
    cmp_qa = {}
    # /dev/* 和 /develop 对比
    cmp_dev = {}

    collect_stat(dev_stat, cmp_qa, res_qa)
    collect_stat(dev_stat, cmp_dev, res_develop)

    cmp_tmp = {}
    collect_stat(dev_stat, cmp_tmp, res_release)
    cmp_tmp = {}
    collect_stat(dev_stat, cmp_tmp, res_master)

    # 可以删除的分支提示

    # 已经合并到develop的分支 使用cmp_dev就好了
    # 非常老的没有提交的分支
    very_old_branch = []
    all_heads = dvt.get_heads()
    keys = all_heads.keys()
    keys.sort()
    for e in keys:
        b = all_heads[e]
        st = datetime.datetime.fromtimestamp(b[1])
        cpst = datetime.datetime.now() - datetime.timedelta(days=7)
        if e not in cmp_dev['develop'] and len(e) > 4 and e[0:4] == 'dev/' and cpst > st:
            very_old_branch.append(e)

    
    #print len(very_old_branch)

    #print cmp_dev
    #print dev_stat

    ###############
    nomerge_dev_stat = collect_nomerge_stat(res_nomerge_dev)
    nomerge_dep_stat = collect_nomerge_stat(res_nomerge_dep)
    nomerge_master_dev_stat = collect_nomerge_stat(res_nomerge_master_dev)
    #print dev_stat
    #print nomerge_dev_stat
    #print nomerge_dep_stat
    return  {'dev_stat': dev_stat,
             'cmp_qa': cmp_qa,
             'cmp_dev': cmp_dev,
             'nomerge_dev_stat': nomerge_dev_stat,
             'nomerge_dep_stat': nomerge_dep_stat,
             'nomerge_master_dev_stat': nomerge_master_dev_stat,
             'heads': all_heads,
             'tags': dvt.recent_tag(10),
             'old_branch': very_old_branch,
             }


# =======================================
def tst_create_tag():
    try:
        dvt = DevVcsTool('origin')
        res = dvt.create_tag('tst', 'adadf--2321asd #ad')
        print res

    except ShellCmdError as e:
        print e


def tst_del_remote_br():
    try:
        dvt = DevVcsTool('origin')
        res = dvt.del_remote_branch('devtool/test')
        print res

    except ShellCmdError as e:
        print e


def tst_all_remote_branch_head():
    try:
        dvt = DevVcsTool('origin')
        res = dvt.all_remote_branch_head()
        print res

    except ShellCmdError as e:
        print e


def tst_check_merge_branch():
    try:
        #res = check_merge_branch('master', ['master', 'develop', 'deploy', 'dev/feature/ordertrends', 'dev/congming_test'])
        #res = check_merge_branch('master', ['master', 'develop'])
        res = check_merge_branch('qa/ttt', ['dev/sms_ret_non_object', 'develop', 'deploy', 'master'])
        
        print res['stat']

    except ShellCmdError as e:
        print e


def tst_check_need_merge():
    try:
        dvt = DevVcsTool('origin')
        res = dvt.check_need_merge(['master', 'develop', 'deploy', 'dev/feature/ordertrends', 'dev/congming_test'])
        print res

    except ShellCmdError as e:
        print e




def tst2():
    try:
        dvt = DevVcsTool('origin')
        res = dvt.merge_branch('devtool/test2', ['master', 'dev/congming_test'], "客户端版本升级配置修改T]]啦啦拉阿打发散的份额\\TT\\TT$33&*QQQQQQ#)(*#T'\"TT", '')
        #res = dvt.merge_branch('devtool/test2', ['master', 'dev/congming_test'], "TTTTTTTTTTTT", True)
        for r in res:
            print r
            print res[r]

    except ShellCmdError as e:
        print e


def tst_clear_local():
    try:
        dvt = DevVcsTool('origind')
        res = dvt.clear_local()
        return res

    except ShellCmdError as e:
        return e


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
    #print tst2()
    except_wrapper(all_merge_stat)
    #print tst_check_merge_branch()
    #print tst_create_tag()
    #print tst_all_remote_branch_head()
    #print tst_check_need_merge()
    #tst_del_remote_br()
    #print all_merge_stat_execpt()
    #print except_wrapper(create_solid_branch, 'develop', 'dev/ttt', True)
    #print tst_clear_local()


