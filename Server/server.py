import tornado.httpserver
import tornado.ioloop
import tornado.web

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("<a href=\"https://www.youtube.com/watch?v=dQw4w9WgXcQ\">Hello World</a>")

application = tornado.web.Application([
    (r'/', RootHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application, ssl_options={
        "certfile": "./letsencrypt/cert.pem",
        "keyfile": "./letsencrypt/key.pem",
        "ca_certs": "./letsencrypt/fullchain.pem",
    })
    http_server.listen(443)
    tornado.ioloop.IOLoop.instance().start()


