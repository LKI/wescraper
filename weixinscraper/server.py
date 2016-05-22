from tornado.ioloop import IOLoop
import tornado.web as tw
import os.path
import subprocess

scraper = "wxscraper.py";
if not os.path.exists(scraper):
    scraper = os.path.join("weixinscraper", scraper)

class WeixinHandler(tw.RequestHandler):
    def get(self, path):
        if path:
            accounts = path.split('/')
            p = subprocess.Popen(["python", scraper, accounts], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            self.write(out)
        else:
            self.write("You may specify a URL to search, such as (http://host/liriansu/miawu)")

app = tw.Application([
    (r'/(.*)', WeixinHandler)
])
app.listen(80)
IOLoop.current().start()
