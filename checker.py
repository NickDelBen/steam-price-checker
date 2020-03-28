#!/chuff/guff/python3
# 0xMartian

import math
import pickle
from datetime import datetime, timedelta

import requests

class SteamManager:

    def __init__ (self, readFile=None, output=True):
        if readFile: self.loadFromFile(readFile)
        else: self.updatePrices(output=output)

    def needsUpdate (self): return datetime.now() - self.update > timedelta(days=1)
    def updatePrices (self, output=True):
        if output: print("Local Price Database Out of sync... Preforming Update")
        self.loadFromInternet(output=output)
    
    def saveToFile (self, fileOut): pickle.dump({"apps": self.apps, "update": self.update}, fileOut)
    def loadFromFile (self, fileIn, output=True): 
        loaded_data = pickle.load(fileIn)
        self.apps = loaded_data["apps"]
        self.update = loaded_data["update"]
        if output: print("Loaded {0} app prices\nLast updated {1}".format(len(self.apps), self.update))

    def loadFromInternet (self, page_size=800, output=True):
        self.apps = {}
        for retrieved_app in self.getAppList(): self.apps[str(retrieved_app["appid"])] = {"name": retrieved_app["name"]}
        keylist = [str(sorted_id) for sorted_id in sorted([int(appid) for appid in self.apps.keys()])]
        if output: print("Retrieveing Price Data for {0} Steam Apps:".format(len(keylist)))
        for offset in range(0, len(keylist), page_size):
            if output: print("    Page [{0}/{1}] Steam Apps [{2}-{3}/{4}]".format( int(math.ceil(offset/page_size))+1, 
                int(math.ceil(len(keylist)/page_size)), keylist[offset], keylist[min(len(keylist), offset+page_size)-1], keylist[-1]
            ))
            for appid, price_data in self.getAppPrices(keylist[offset:min(len(keylist), offset+page_size) - 1]).items():
                self.apps[str(appid)].update({"price": price_data})
        self.update = datetime.now()

    def getFreeApps (self): return self.findFreeApps(self.apps)

    @staticmethod
    def getAppList ():
        data = requests.get("http://api.steampowered.com/ISteamApps/GetAppList/v2").json()
        return data["applist"]["apps"]

    @staticmethod
    def parsePriceOverview (overview):
        price_fields = ["currency", "initial", "final", "discount_percent", "initial_formatted", "final_formatted"]
        result = {}
        for price_field in price_fields:
            if price_field in overview: result[price_field] = overview[price_field]
        return result

    @staticmethod
    def getAppPrices (appid_list):
        prices_url = "https://store.steampowered.com/api/appdetails?appids={0}&filters=price_overview".format(",".join(appid_list))
        data = requests.get(prices_url).json()
        results = {}
        for appid, app_data in data.items():
            results[appid] = None
            if app_data["success"] == False:
                continue
            if not "price_overview" in app_data["data"]:
                continue
            results[appid] = SteamManager.parsePriceOverview(app_data["data"]["price_overview"])
        return results

    @staticmethod
    def findFreeApps (app_list):
        results = {}
        for appid, app_data in app_list.items():
            if not "price" in app_data: continue
            if app_data["price"] is None: continue
            if not "initial" in app_data["price"]: continue
            if not "discount_percent" in app_data["price"]: continue
            if app_data["price"]["initial"] <= 0: continue
            if app_data["price"]["discount_percent"] < 100: continue
            results[appid] = app_data
        return results

def print_price_table (apps):
    def print_row (*args): print("|{0: <60.60}|{1: <15}|{2: <15}|{3: <15}|".format(*args))
    def print_divider (*args): print_row("-"*1024, "-"*15, "-"*15, "-"*15)
    print_divider()
    print_row("Game", "Steam App ID", "Old Price", "Current Price")
    print_divider()
    for row in sorted(apps.items(), key=lambda item:(item[1]["price"]["initial"], item[0]), reverse=True):
        print_row(row[1]["name"], row[0], row[1]["price"]["initial_formatted"], row[1]["price"]["final_formatted"])
    print_divider()        

if __name__ == "__main__":
    import sys
    import os
    data_file = sys.argv[1] if len(sys.argv) > 1 else "./steamappdata.dat"
    if os.path.isfile(data_file):
        with open(data_file, "rb") as fin: manager = SteamManager(readFile=fin)
    else: manager = SteamManager()
    if manager.needsUpdate(): manager.updatePrices()
    with open(data_file, "wb") as fout: manager.saveToFile(fout)
    print_price_table(manager.getFreeApps())
