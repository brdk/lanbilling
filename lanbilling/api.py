import logging
from lanbilling import lb
from lanbilling.exceptions import LBAPIError


class LANBilling(object):
    instance = None

    def __new__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(LANBilling, cls).__new__(cls)
        return cls.instance

    def __init__(self, manager='admin', password='', host='127.0.0.1', port=1502):
        self.manager = manager
        self.host = host
        self.port = int(port)

        self.logger = logging.getLogger(__name__)

        try:
            self.lbapi = lb.Client(host, int(port))
            self.lbapi.Login(login=manager, password=password)
        except Exception as e:
            self.logger.debug(e)
            raise LBAPIError(e)

    def __repr__(self):
        return "LANBilling(manager={manager!r}, host={host!r}, port={port!r})".format(**self.__dict__)

    def __str__(self):
        return "Connected to {host}:{port} as {manager}".format(**self.__dict__)

    def __getattr__(self, method):
        return LBAPIMethod(self, method)

    def __call__(self, method, *args, **kwargs):
        params = {}

        try:
            if args and len(args) == 1 and type(args[0]) is dict:
                params.update(args[0])
            if kwargs:
                params.update(kwargs)
            return self.lbapi.run(method, params)
        except RuntimeError, e:
            raise LBAPIError(e)

    def help(self, method_name=None):
        methods = self.lbapi.system_get_functors(None)
        if method_name is None:
            print 'Available methods:'
            print '\n'.join(method['name'] for method in methods)
            return
        for method in methods:
            if method['name'] == method_name:
                func = getattr(self.lbapi, method_name)
                func.__name__ = method['name']
                func.__doc__ = '\n\n'
                if 'descr' in method:
                    func.__doc__ += "{descr}\n\n".format(**method)
                if 'input' in method:
                    func.__doc__ += "Input: {input}\n\n".format(**method)
                if 'output' in method:
                    func.__doc__ += "Output: {output}\n\n".format(**method)
                if 'output2' in method:
                    func.__doc__ += "Output: {output2}\n\n".format(**method)
                func.__doc__ += '\n'
                return help(func)
        else:
            print("Method {method_name} not found".format(method_name=method_name))
            return


class LBAPIMethod(object):
    __slots__ = ['_lb_session', '_method_name']

    def __init__(self, lb_session, method_name):
        self._lb_session = lb_session
        self._method_name = method_name

    def __call__(self, *args, **kwargs):
        return self._lb_session(self._method_name, *args, **kwargs)

