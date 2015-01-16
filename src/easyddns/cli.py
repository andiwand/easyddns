import argparse
import json
from selenium import webdriver
from easyname.bot import EasynameBot

from easyddns.server import Server

EXAMPLE_SETTINGS = """
{
    "port": "65500",
    "phantomjs": "/path/to/phantomjs or empty if it's in the PATH",
    "easyname": {
        "username": "...",
        "password": "..."
    },
    "logfile": "/path/to/logfile or empty to disable"
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

def load(path):
    file = open(path)
    settings = json.load(file)
    
    logfile = settings.get("logfile", None)
    phantomjs = settings.get("phantomjs", None)
    if not phantomjs: phantomjs = "phantomjs"
    driver = webdriver.PhantomJS(phantomjs)
    easyname = EasynameBot(driver)
    
    easyname.auth(settings["easyname"]["username"], settings["easyname"]["password"])
    server = Server(("", int(settings["port"])), easyname, debug_out=open(logfile))
    for user in settings["users"]:
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
        file.write(EXAMPLE_SETTINGS)
        file.close()
    else:
        server = load(args.config)
        print("loaded")
        server.serve_forever()

if __name__ == "__main__":
    main()
