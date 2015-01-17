import time
import base64
import socketserver
import http.server
import urllib.parse as urlparse

class Server(socketserver.TCPServer):
    def __init__(self, server_address, easyname, bind_and_activate=True, debug=True):
        self.__debug = debug
        self.debug("open tcp socket %s ..." % str(server_address))
        socketserver.TCPServer.__init__(self, server_address, Handler, bind_and_activate)
        self.__auth_users = []
        self.__auth_records = {}
        self.__easyname = easyname
        self.__domain_ids = {}
        self.__record_ids = {}
        self.__init_easyname()
    def __init_easyname(self):
        self.debug("init easyname ...")
        for domainid, domain in self.__easyname.domains():
            if not domainid or not domain: continue
            self.debug("found domain %s with id %s" % (domain, domainid))
            self.__domain_ids[domain] = domainid
            for recordid, record, record_type, _, _, _ in self.__easyname.dns_entries(domainid):
                self.debug("found record %s with id %s" % (record, recordid))
                if not recordid or not record or not record_type: continue
                if record_type not in ("A", "AAAA", "CNAME"): continue
                self.debug("stored record")
                self.__record_ids[record] = recordid
        self.debug("init done.")
    def debug(self, msg):
        if not self.__debug: return
        timestamp = time.strftime("%x %X")
        print(timestamp + "  " + msg)
    def get_domainid(self, record):
        for domain, domainid in self.__domain_ids.items():
            if record.endswith(domain): return domainid
    def get_recordid(self, record):
        return self.__record_ids.get(record, None)
    def add_user(self, username, password):
        self.__auth_users.append((username, password))
    def add_record(self, username, record):
        record_set = self.__auth_records.setdefault(username, set())
        record_set.add(record)
    def auth_user(self, auth):
        return auth in self.__auth_users
    def auth_record(self, username, record):
        return record in self.__auth_records.get(username, set())
    def update(self, domainid, recordid, content):
        self.debug("update record (domain id = %s, record id = %s) with %s" % (domainid, recordid, content))
        self.__easyname.dns_edit(domainid, recordid, None, None, content, None, None)

class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        http.server.BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.__username = None
    def do_HEAD(self, status=200, msg=None):
        self.server.debug("send head %s" % str(status))
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if msg:
            self.server.debug(msg)
            self.wfile.write(bytes(msg, "utf-8"))
    def do_ERROR(self, status, msg=None):
        self.do_HEAD(status)
    def do_AUTHHEAD(self):
        self.server.debug("send auth head")
        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic")
        self.send_header("Content-type", "text/html")
        self.end_headers()
    def do_GET(self):
        self.server.debug("handle get " + self.path)
        auth = self.headers.get("Authorization")
        if auth == None:
            self.server.debug("not auth header")
            self.do_AUTHHEAD()
        elif auth.startswith("Basic "):
            auth = tuple(base64.b64decode(auth[6:]).decode("utf-8").split(":", 1))
            if self.server.auth_user(auth):
                self.server.debug("authenticated")
                self.__username = auth[0]
                self.__handle_get()
            else:
                self.do_ERROR(401, "unauthorized user request")
        else:
            self.do_ERROR(401, "invalid authentication")
    def __handle_get(self):
        path = self.path
        url = urlparse.urlparse(path)
        params = urlparse.parse_qs(url.query)
        if url.path == "/update":
            record = params.get("record", [None, ])[0]
            content = params.get("content", [None, ])[0]
            if record and content:
                if self.server.auth_record(self.__username, record):
                    self.server.debug("authorized record update request")
                    self.__handle_update(record, content)
                else:
                    self.do_ERROR(401, "unauthorized record update request")
            else:
                self.do_ERROR(400, "invalid update arguments")
        else:
            self.do_ERROR(400, "invalid path")
    def __handle_update(self, record, content):
        self.server.debug("handle update (record = %s, content = %s)" % (record, content))
        domainid = self.server.get_domainid(record)
        recordid = self.server.get_recordid(record)
        if not domainid or not recordid:
            self.do_ERROR(400, "invalid update arguments")
        else:
            try:
                self.server.update(domainid, recordid, content)
                self.do_HEAD(msg="updated")
            except:
                self.do_ERROR(500, "update failed")
