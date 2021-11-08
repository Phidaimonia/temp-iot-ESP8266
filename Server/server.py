import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.template as T
import json

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(temp.generate(myvalue="dQw4w9WgXcQ"))


class JSONHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(slovnik))



application = tornado.web.Application(handlers=[
    (r'/', RootHandler),
    (r'/json/', JSONHandler),
    (r'/json', JSONHandler),
    ('/(.*)', tornado.web.StaticFileHandler, {'path': './static'})

])

if __name__ == '__main__':
    
    loader = T.Loader("./Static/HTML/")
    temp = loader.load("index.html")

    slovnik = {"HTTP" : 80, 
                "HTTPS" : 443}


    http_server = tornado.httpserver.HTTPServer(application)

    # ssl_options={
    #    "certfile": "./letsencrypt/cert.pem",
    #    "keyfile": "./letsencrypt/key.pem",
    #    "ca_certs": "./letsencrypt/fullchain.pem",
    #}


    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()


