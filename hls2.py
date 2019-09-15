import requests
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions


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

            print("\nCouldn't find any links for that team! Try again closer to game time!\n")
            return 'None'

    def fetch_links(self):
        links = []
        for item in self.game_json:
            for data in item['data']['children']:
                for key in data['data'].keys():
                    try:
                        if key == "body_html":
                            url = data['data'][key].split("href=")[1]
                            if "http" in url:
                                links.append(url.split("&")[0].strip("\""))
                    except IndexError or KeyError or TypeError:
                        continue
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
        self.export_har_js = \
            """return HAR.triggerExport().then(harLog => {
                   for (r of harLog.entries) {
                       if (r.request.url.includes("m3u8")) { 
                           return r.request;
                       }
                   }
               });"""

        self.get_stream_iframe_js = \
            """return (() => {
                   ifs = [];
                   for (e of document.all) {
                       if (e.innerHTML.includes("gma")) {
                           ifs.push(e);
                       }
                   }
                   return(ifs)[5].innerHTML;
               })();"""

        self.click_isolated_iframe = \
            """for (e of document.all) {
                  e.click();
                }"""
        self.scrape()

    def scrape(self):
        for stream_link in self.links:
            self.driver.get(stream_link)
            if "grandmastreams" in stream_link:
                print("\nrunning gma streams js...\n")
                a = self.driver.execute_script(self.get_stream_iframe_js)
                link = a.split("<iframe src=")[1].split(" ")[0].strip("\"")
                print(link)
                self.driver.close()
                self.driver.get(link)
                self.driver.execute_script(self.click_isolated_iframe)
                har = self.driver.execute_script(self.export_har_js)
                print(har)
            else:
                a = self.driver.execute_script(self.export_har_js)
                print(a)

            self.driver.quit()


def main():
    team_name = input("\nPlease enter the name of the team you wish to search for:\n")
    gls = GameLinkScraper(team_name)
    if not gls.links:
        return
    else:
        HotLinkScraper(gls.links)


if __name__ == "__main__":
    main()
