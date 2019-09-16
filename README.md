###### **An HLS hotlink scraper for stream links posted to r/nflstreams**

This project is still in it's infancy and is incredibly simple right now. It is capable of scraping the
browser links for any specified team, and will *eventually* be capable of scraping the actual
HLS hotlinks for any given page. 

Currently, the main issue with development is the fact that the only real testing that can be done is during times
while there are live game links. The other hurdle is the fact that the sites where the streams are
hosted vary wildly, and only a few have a common thread to simplify handling them.

This project consists of two main classes, BrowserLinkScraper and HotLinkScraper.
BrowserLinkScraper returns a list of the browser links that were scraped from the r/nflstreams
subreddit for the specified team. HotLinkScraper will eventually work in conjunction with BrowserLinkScraper to be
able to fetch the live HLS hotlinks from list of pages returned by BrowserLinkScraper. 
For now, they can be used separately via the interactive interface (just pass the page's link to the 
HotLinkScraper class) You can also import this module to use the classes in other projects, though
it is not technically setup to be a proper module yet.

With this still being brand-new and experimental it is still buggy, and a bit slow.

Use of the HotLinkScraper class requires the selenium module to be installed to allow for headless
page loading. Included in this repository in the resource directory is the "HARTriggerExport" addon for 
firefox which is installed to the temporary profile of the headless browser that is spawned to
allow for a javascript injection that triggers the export of the HTTP Archive of the network calls made by
the page to fetch the required resources. It only supports the use of the firefox driver at this time
and has **NOT** yet been tested in a windows environment.

Will update as I am able to add/test more. (: