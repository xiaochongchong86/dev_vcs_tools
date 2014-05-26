#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import commands
import traceback
import datetime
import time
import json

class ShellCmdError(Exception):
    def __init__(self, cmd, code, err):
        self.cmd = cmd
        self.code = code
        self.err = err

    def __str__(self):
        return 'Do shell:[%s] code:%d err:\n%s' % (self.cmd, self.code, self.err)


class PrivilegeError(Exception):
    def __init__(self, need_p, now_p):
        self.need_p = need_p
        self.now_p = now_p

    def __str__(self):
        return 'your privilege is not enough, need larger than %s.%s, but now is %s.%s' % (self.need_p[0],
                                                                                           self.need_p[1],
                                                                                           self.now_p[0],
                                                                                           self.now_p[1])


class OtherError(Exception):
    def __init__(self, err):
        self.err = err

    def __str__(self):
        return self.err



def traceback_wrapper_in(fun, *args, **kwds):
    try:
        res = fun(*args, **kwds)
        res = {'code': 0, 'res': res}

    except OtherError as e:
        res = {'code': 1, 'err': str(e)}

    except ShellCmdError as e:
        res = {'code': 2, 'err': str(e)}

    except PrivilegeError as e:
        res = {'code': 3, 'err': str(e)}

    except:
        traceback.print_exc()
        res = { 'code': 4, 'err': traceback.format_exc() }

    #print res
    return json.dumps(res, skipkeys=True)


def traceback_wrapper(fun, *args, **kwds):
    try:
        return traceback_wrapper_in(fun, *args, **kwds)

    except:
        traceback.print_exc()
        res = { 'code': 4, 'err': traceback.format_exc() }
        return json.dumps(res)
