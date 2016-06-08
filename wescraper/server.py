from tornado.ioloop import IOLoop
import tornado.web as tw
import config
import os.path
import subprocess
import sys

dirname = os.path.dirname(os.path.realpath(sys.argv[0]))
scraper = os.path.join(dirname,  "scraper.py")

class WeHandler(tw.RequestHandler):
    def get(self, key_type, path):
        if not key_type in config.types:
            self.write("Type should be {}".format(str(config.types)))
            return
        if path:
            accounts = path.split('/')
            p = subprocess.Popen(["python", scraper, key_type] + accounts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            print str(err)
            self.write(out)
        else:
            self.write("You may specify a URL to search, these urls are valid:\n")
            for t in config.types:
                self.write("http://host/{}/liriansu/miawu".format(t))

app = tw.Application([
    (r'/(favicon.ico)', tw.StaticFileHandler, {"path": ""}),
    (ur'/(.*)/(.*)', WeHandler)
])
app.listen(config.tornado_port)
print "Server is up on port {} now.".format(config.tornado_port)
IOLoop.current().start()
