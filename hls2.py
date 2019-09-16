import requests
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import pprint
import time


class GameLinkScraper(object):
    def __init__(self, team):
        super().__init__()
        self.team = team
        self.sub_reddit_url = "https://www.reddit.com/r/nflstreams/.json"
        self.game_json = self.fetch_game()
        if self.game_json != 'None':
            self.links = self.fetch_links()
        else:
            self.links = []
            return

    def fetch_game(self):
        while True:
            req = requests.get(self.sub_reddit_url)
            if "Too Many Requests" in req.text:
                continue
            for item in json.loads(req.text)['data']['children']:
                try:
                    title = item['data']['title']
                    if self.team in title:
                        try:
                            return json.loads(requests.get(item['data']['url'] + "/.json").text)
                        except KeyError or TypeError:
                            continue
                except KeyError or TypeError:
                    continue

            print("\n\033[1;31;49mCouldn't find any links for that team! Try again closer to game time!\n")
            return 'None'

    # This is hacky and loopy but for some reason I can't directly
    # access the "body_html" key within the inner post dictionary
    # without raising an exception
    def fetch_links(self):
        links = []
        for item in self.game_json:
            try:
                for data in item['data']['children']:
                    for key in data['data'].keys():
                        try:
                            if key == "body_html":
                                url = data['data'][key].split("href=")[1]

                                if "http" in url:
                                    links.append(url.split("&")[0].strip("\""))
                        except IndexError or KeyError or TypeError:
                            continue
            except TypeError:
                continue
        print("\033[1;37;49m")
        pprint.pprint(links)
        return links


class HotLinkScraper(object):
    def __init__(self, links):
        super().__init__()
        self.links = links
        self.profile = webdriver.FirefoxProfile()
        self.profile.add_extension("resource/har_export_trigger-0.6.1.xpi")
        self.options = FirefoxOptions()
        self.options.add_argument("-headless")
        self.options.add_argument("-devtools")
        self.driver = webdriver.Firefox(self.profile, firefox_options=self.options)

        # Javascript to inject with selenium for HAR export
        self.export_har_js = \
            """return HAR.triggerExport().then(harLog => {
                   for (r of harLog.entries) {
                       if (r.request.url.includes("m3u8")) { 
                           return r.request;
                       }
                   }
               });"""

        # IIFE to return isolated embedded player element and extract it's source
        # for streams that need to be clicked before the HLS hotlink is exposed
        self.get_stream_iframe_js = \
            """return (() => {
                   return document.getElementById("stream")['firstElementChild']['src'];
               })();"""

        self.get_stream_iframe_js2 = \
            """return (() => {
                   return document.getElementById("ipopp")['src'];
               })();"""

        # Javascript to click on a page
        self.click_isolated_iframe = \
            """for (e of document.all) {
                   try {
                       e.click();
                   } catch (TypeError) {
                       continue;
                   }
                }"""
        self.scrape()

    # Most work needs to be done here, handling specific popular streams
    def scrape(self):
        for stream_link in self.links:
            self.driver.get(stream_link)
            if "grandmastreams" in stream_link:
                print("\nrunning gma streams js...\n")
                link = self.driver.execute_script(self.get_stream_iframe_js)
                print(link)
                self.driver.get(link)
                self.driver.execute_script(self.click_isolated_iframe)
                time.sleep(3)
                har = self.driver.execute_script(self.export_har_js)
                print("\033[1;37;49m\nURL:\n\n" + har['url'])
                print("\nHeaders:\n")
                pprint.pprint(har['headers'])
            else:
                har = self.driver.execute_script(self.export_har_js)
                print("\033[1;37;49m\nURL:\n\n" + har['url'])
                print("\nHeaders:\n")
                pprint.pprint(har['headers'])

            self.driver.quit()


def main():
    while True:
        print("\n\033[1;36;49mFor browser links only, type browser."
              "\nFor hotlinks only, type hotlink.\n"
              "For both, type both. \033[1;33;49m*Not quite ready! Will likely throw exception*\n"
              "\033[1;36;49mTo quit, type quit.\n\n")
        action = input("\033[1;32;49m>> ")
        if action == "both":
            print("\n\033[1;36;49mPlease enter the name of the team you wish to search for:\n")
            team_name = input("\033[1;32;49m>> ")
            gls = GameLinkScraper(team_name)
            if not gls.links:
                return
            else:
                HotLinkScraper(gls.links)
        elif action == "browser":
            print("\n\033[1;36;49mPlease enter the name of the team you wish to search for:\n")
            team_name = input("\033[1;32;49m>> ")
            GameLinkScraper(team_name)
        elif action == "hotlink":
            print("\n\033[1;36;49mPlease enter the url to scrape hotlink from:\n")
            url = input("\033[1;32;49m>> ")
            HotLinkScraper([url])
        elif action == "quit":
            return
        else:
            print("\n\033[1;31;49mInvalid command, try again!\n")


if __name__ == "__main__":
    main()