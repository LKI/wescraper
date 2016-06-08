from tornado.ioloop import IOLoop
import tornado.web as tw
import config
import os.path
import subprocess
import sys

dirname = os.path.dirname(os.path.realpath(sys.argv[0]))
scraper = os.path.join(dirname,  "scraper.py")

class WeHandler(tw.RequestHandler):
    def get(self, key_type, path=None):
        if key_type in config.types and path:
            accounts = path.split('/')
            p = subprocess.Popen(["python", scraper, key_type] + accounts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            print str(err)
            self.write(out)
        else:
            self.write("Change url to http://host/type/key1/key2 to search.\n")
            self.write("For example, these urls are valid:\n")
            for t in config.types:
                self.write("http://host/{}/liriansu\n".format(t))

app = tw.Application([
    (r'/(favicon.ico)', tw.StaticFileHandler, {"path": ""}),
    (ur'/(.*)/(.*)', WeHandler),
    (ur'/(.*)', WeHandler)
])
app.listen(config.tornado_port)
print "Server is up on port {} now.".format(config.tornado_port)
IOLoop.current().start()
