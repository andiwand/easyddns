import argparse
import json
from selenium import webdriver
from easyname.bot import EasynameBot

from easyddns.server import Server

EXAMPLE_CONFIG = """
{
    "port": "65500",
    "phantomjs": "/path/to/phantomjs or empty if it's in the PATH",
    "easyname": {
        "username": "...",
        "password": "..."
    },
    "users": [
        {
            "username": "user1",
            "password": "...",
            "permissions": [
                "record1.to.update",
                "record2.to.update"
            ]
        },
        {
            "username": "user2",
            "password": "...",
            "permissions": [
                "record1.to.update",
                "record2.to.update"
            ]
        }
    ]
}
""".strip().encode("utf-8")

class easymanager:
    def __init__(self, config_path):
        file = open(config_path)
        self.__settings = json.load(file)
    def create_easyname(self):
        phantomjs = self.__settings.get("phantomjs", None)
        if not phantomjs: phantomjs = "phantomjs"
        driver = webdriver.PhantomJS(phantomjs)
        easyname = EasynameBot(driver)
        easyname.auth(self.__settings["easyname"]["username"], self.__settings["easyname"]["password"])
        return easyname
    def create_server(self):
        server = Server(("", int(self.__settings["port"])), self.create_easyname)
        for user in self.__settings["users"]:
            server.add_user(user["username"], user["password"])
            for permission in user["permissions"]:
                server.add_record(user["username"], permission)
        return server

def main():
    parser = argparse.ArgumentParser(description="easyname ddns proxy server")
    parser.add_argument("config", help="path to the config file")
    parser.add_argument("-c", dest="create", action="store_const", const=True, help="create sample config")
    args = parser.parse_args()
    
    if args.create:
        file = open(args.config, "wb")
        file.write(EXAMPLE_CONFIG)
        file.close()
    else:
        manager = easymanager(args.config)
        server = manager.create_server()
        server.serve_forever()

if __name__ == "__main__":
    main()
