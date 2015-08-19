#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# python-lb module
#
# Michael Evdokimov, 2012, Moscow, Network solutions.
# Edited by Andrey Madiev, 2015.
#

import sys
import socket
import threading
import weakref
import simplejson as json

max_timeout = 600


class RunningFlag:
    pass


def hdl(client):
    p = client()
    if p is None:
        return
    queue = p.queue
    f = p.f
    messages = p.messages
    msg_queue = p.msg_queue
    msg_event = p.msg_event
    del p
    while True:
        try:
            line = f.readline().strip()
        except:
            break
        if line == '':
            break
        resp = json.loads(line)
        if 'method' not in resp and 'id' in resp:
            num = resp['id']
            queue[num]['resp'] = resp
            queue[num]['event'].set()
        elif 'method' in resp and resp['method'] == 'notify':
            msg = resp['params']['message']
            params = resp['params']['params']
            if msg in messages:
                func = messages[msg]
                msg_queue += [(func, msg, params)]
                msg_event.set()
        else:
            raise "Unknown line: '" + line + "'"


def hdl_msg(client):
    p = client()
    if p is None:
        return
    msg_queue = p.msg_queue
    msg_event = p.msg_event
    msg_empty = p.msg_empty
    running = weakref.ref(p.running)
    del p
    while True:
        msg_event.wait(max_timeout)
        msg_event.clear()
        if running() is None:
            break
        while len(msg_queue):
            msg = msg_queue[0]
            msg[0](msg[1], msg[2])
            del msg_queue[0]
        msg_empty.set()


class Client:
    def __init__(self, host, port):
        self.running = RunningFlag()
        self.host = host
        self.port = port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.idx = 0
            self.f = self.sock.makefile('w+', 0)
        except socket.error, detail:
            print('Error while connected to socket: %s' % detail)
            sys.exit(1)
        self.queue = {}
        self.messages = {}
        self.msg_queue = []
        self.msg_event = threading.Event()
        self.msg_empty = threading.Event()
        self.th = threading.Thread(target=hdl, args=(weakref.ref(self), ))
        self.th.setDaemon(True)
        self.th.start()
        self.th2 = threading.Thread(target=hdl_msg, args=(weakref.ref(self), ))
        self.th2.setDaemon(True)
        self.th2.start()

    def __del__(self):
        del self.running
        self.f._sock.shutdown(socket.SHUT_RDWR)
        self.th.join()
        self.msg_event.set()
        self.th2.join()

    def __getattr__(self, name):
        def func(*args, **kw):
            if len(args) != 1:
                return self.run(name, kw)
            else:
                return self.run(name, args[0])

        return func

    def run(self, method, params):
        self.idx += 1
        now_idx = self.idx
        cmd = {"id": now_idx, "method": str(method), "params": params}
        self.queue[now_idx] = {'cmd': cmd, 'sent': True, 'event': threading.Event()}
        self.f.write(json.dumps(cmd) + '\n')
        self.f.flush()
        self.queue[now_idx]["event"].wait(max_timeout)
        resp = None
        if "resp" in self.queue[now_idx]:
            resp = self.queue[now_idx]["resp"]
        else:
            raise RuntimeError("Lost connection to LBcore")
        del self.queue[now_idx]
        if 'id' not in resp or str(resp['id']) != str(now_idx):
            raise RuntimeError('Incorrect "id" = %u field in response. Must be %u' % (resp['id'], now_idx))
        if 'result' in resp:
            return resp['result']
        if 'error' in resp:
            raise RuntimeError(resp['error']['message'])
        raise RuntimeError('Internal error')

    def subscribe(self, msg, func):
        self.messages[msg] = func
        self.run("system_subscribe", {"message": msg})

    def unsubscribe(self, msg):
        self.run("system_unsubscribe", {"message": msg})
        del self.messages[msg]

    def wait_for_messages(self):
        self.run("system_check_messages", None)
        self.msg_empty.clear()
        if not self.msg_queue:
            return True
        self.msg_empty.wait(max_timeout)
        return self.msg_queue == []

