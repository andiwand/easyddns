import argparse
import json
from selenium import webdriver
from easyname.bot import EasynameBot

from easyddns.server import Server

def load(path):
    file = open(path)
    settings = json.load(file)
    
    driver = webdriver.PhantomJS(settings.get("phantomjs", "phantomjs"))
    easyname = EasynameBot(driver)
    
    easyname.auth(settings["easyname"]["username"], settings["easyname"]["password"])
    server = Server(("", int(settings["port"])), easyname)
    for user in settings["users"]:
        server.add_user(user["username"], user["password"])
        for permission in user["permissions"]:
            server.add_record(user["username"], permission)
    return server

def main():
    parser = argparse.ArgumentParser(description="easyname ddns proxy server")
    parser.add_argument("settings", metavar="settings", help="path to the settings file")
    args = parser.parse_args()
    print(args)
    #server = load("settings.json")
    #print("loaded")
    #server.serve_forever()

if __name__ == "__main__":
    main()
