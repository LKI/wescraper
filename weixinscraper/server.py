from wxscraper import WeixinScraper
from tornado.ioloop import IOLoop
import json
import tornado.web as tw

class WeixinHandler(tw.RequestHandler):
    def get(self, path):
        if path:
            self.write(json.dumps(WeixinScraper().crawl(path.split('/'))))
        else:
            self.write("You may specify a URL to search, such as (http://host/liriansu/miawu)")

app = tw.Application([
    (r'/(.*)', WeixinHandler)
])
app.listen(80)
IOLoop.current().start()
