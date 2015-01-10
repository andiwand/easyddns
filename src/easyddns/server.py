import base64
import socketserver
import http.server
import urllib.parse as urlparse

class Server(socketserver.TCPServer):
    def __init__(self, server_address, easyname, bind_and_activate=True):
        socketserver.TCPServer.__init__(self, server_address, Handler, bind_and_activate)
        self.__auth_users = []
        self.__auth_records = {}
        self.__easyname = easyname
        self.__domain_ids = {}
        self.__record_ids = {}
        self.__init_easyname()
    def __init_easyname(self):
        for domainid, domain in self.__easyname.domains():
            if not domainid or not domain: continue
            self.__domain_ids[domain] = domainid
            for recordid, record, record_type, _, _, _ in self.__easyname.dns_entries(domainid):
                if not recordid or not record or not record_type: continue
                if record_type not in ("A", "AAAA", "CNAME"): continue
                self.__record_ids[record] = recordid
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
        self.__easyname.dns_edit(domainid, recordid, None, None, content, None, None)

class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        http.server.BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.__username = None
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic")
        self.send_header("Content-type", "text/html")
        self.end_headers()
    def do_GET(self):
        auth = self.headers.get("Authorization")
        if auth == None:
            self.do_AUTHHEAD()
        elif auth.startswith("Basic "):
            auth = tuple(base64.b64decode(auth[6:]).decode("utf-8").split(":", 1))
            if self.server.auth_user(auth):
                self.__username = auth[0]
                self.do_HEAD()
                self.__handle_get()
            else:
                self.do_AUTHHEAD()
        else:
            self.do_AUTHHEAD()
    def __handle_get(self):
        path = self.path
        url = urlparse.urlparse(path)
        params = urlparse.parse_qs(url.query)
        if url.path == "/update":
            record = params.get("record", [None, ])[0]
            content = params.get("content", [None, ])[0]
            if record and content:
                if self.server.auth_record(self.__username, record):
                    self.__handle_update(record, content)
    def __handle_update(self, record, content):
        domainid = self.server.get_domainid(record)
        recordid = self.server.get_recordid(record)
        if not domainid or not recordid: return
        self.server.update(domainid, recordid, content)
        self.wfile.write(bytes("updated", "utf-8"))
