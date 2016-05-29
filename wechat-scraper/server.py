from tornado.ioloop import IOLoop
import tornado.web as tw
import os.path
import subprocess
import sys

dirname = os.path.dirname(os.path.realpath(sys.argv[0]))
scraper = os.path.join(dirname,  "wxscraper.py")

class WeixinHandler(tw.RequestHandler):
    def get(self, path):
        if path:
            accounts = path.split('/')
            p = subprocess.Popen(["python", scraper] + accounts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            self.write(out)
        else:
            self.write("You may specify a URL to search, such as (http://host/liriansu/miawu)")

class KeywordHandler(tw.RequestHandler):
    def get(self, key_type, path):
        allow_types = ["all", "year", "month", "week", "day"]
        if not key_type in ["all", "year", "month", "week", "day"]:
            self.write("Type should be in :" + str(allow_types))
        if path:
            accounts = path.split('/')
            p = subprocess.Popen(["python", scraper] + [key_type] + accounts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            self.write(out)
        else:
            self.write("You may specify a URL to search, such as (http://host/keyword-(type)/liriansu/miawu)")

app = tw.Application([
    (r'/(favicon.ico)', tw.StaticFileHandler, {"path": ""}),
    (r'/keyword-(.*)/(.*)', KeywordHandler),
    (r'/(.*)', WeixinHandler)
])
app.listen(80)
print "Server is up on port 80 now."
IOLoop.current().start()
