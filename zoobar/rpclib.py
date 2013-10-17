import os
import sys
import socket
import stat
import errno
import json
from debug import *

_allowed_exceptions = {
        'ValueError' : ValueError,
        'AttributeError' : AttributeError,
        'TypeError' : TypeError,
        'KeyError' : KeyError,
        'IndexError' : IndexError
        }

def parse_req(req):
    req_dict = json.loads(req)
    return (req_dict['method'], req_dict['kwargs'])

def format_req(method, kwargs):
    req_dict = { "method" : method, "kwargs" : kwargs }
    return json.dumps(req_dict)

def parse_resp(resp):
    resp = json.loads(resp)
    status = resp.get("status")

    if status == "success":
        return resp.get("result")
    elif status == "exception":
        try:
            exception_type = resp['exception_type']
            message = resp.get('message', "")
        except KeyError:
            raise Exception("Rpc protocol error (1)")

        e_class = _allowed_exceptions.get(exception_type, Exception)
        log(resp.get('stack_trace'))
        raise e_class(message)
    else:
        raise Exception("Rpc protocol error (2)")

def format_resp(resp):
    return json.dumps(resp)

def buffered_readlines(sock):
    buf = ''
    while True:
        while '\n' in buf:
            (line, nl, buf) = buf.partition('\n')
            log("Line: %s" % (line,))
            yield line
        try:
            newdata = sock.recv(4096)
            if newdata == '':
                break
            buf += newdata
        except IOError, e:
            if e.errno == errno.ECONNRESET:
                break

class RpcServer(object):
    def run_sock(self, sock):
        lines = buffered_readlines(sock)
        for req in lines:
            log("req: %r" % (req,))
            (method, kwargs) = parse_req(req)
            m = self.__getattribute__('rpc_' + method)

            ret = {}
            try:
                ret_val = m(**kwargs)
            except Exception as e:
                ret["status"] = "exception"
                ret["exception_type"] = e.__class__.__name__
                ret["message"] = e.message
                ret["stack_trace"] = traceback.format_exc()
            else:
                ret["status"] = "success"
                ret["result"] = ret_val

            sock.sendall(format_resp(ret) + '\n')

    def run_sockpath_fork(self, sockpath):
        if os.path.exists(sockpath):
            s = os.stat(sockpath)
            if not stat.S_ISSOCK(s.st_mode):
                raise Exception('%s exists and is not a socket' % sockpath)
            os.unlink(sockpath)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(sockpath)

        # Allow anyone to connect.
        # For access control, use directory permissions.
        os.chmod(sockpath, 0777)

        server.listen(5)
        while True:
            conn, addr = server.accept()
            pid = os.fork()
            if pid == 0:
                # fork again to avoid zombies
                if os.fork() <= 0:
                    self.run_sock(conn)
                    sys.exit(0)
                else:
                    sys.exit(0)
            conn.close()
            os.waitpid(pid, 0)

class RpcClient(object):
    def __init__(self, sock):
        self.sock = sock
        self.lines = buffered_readlines(sock)

    def call(self, method, **kwargs):
        log("method: %r" % (method, ))
        log("kwargs: %r" % (kwargs, ))
        self.sock.sendall(format_req(method, kwargs) + '\n')
        return parse_resp(self.lines.next())

    def close(self):
        self.sock.close()

    ## __enter__ and __exit__ make it possible to use RpcClient()
    ## in a "with" statement, so that it's automatically closed.
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

def client_connect(pathname):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(pathname)
    return RpcClient(sock)

