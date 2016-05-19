from wxscraper import WeixinScraper
from tornado.ioloop import IOLoop
import json
import tornado.web as tw

class WeixinHandler(tw.RequestHandler):
    def get(self, path):
        if path:
            self.write(json.dumps(WeixinScraper().crawl([path])))
        else:
            self.write("Specify a url to search")

app = tw.Application([
    (r'/(.*)', WeixinHandler)
])
app.listen(8080)
IOLoop.current().start()
