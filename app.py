import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.escape
#from tornado.template import Template
from tornado.template import Loader
try:
    import pymysql
except Exception:
    pass

#import json
#import datetime
#import time

import os
import re
import logging
try:
    from urllib.parse import urlencode
except ImportError:
    from urlparse import urlencode
from optparse import OptionParser

log = logging.getLogger(__name__)

#Model::save() - CORE/cake/libs/model/model.php, line 1290
#CmpVoucherComponent::_add_single_voucher() - APP/controllers/components/cmp_voucher.php, line 235
#CmpVoucherComponent::add_voucher() - APP/controllers/components/cmp_voucher.php, line 91
#ThirdPartiesController::json_create_voucher() - APP/controllers/third_parties_controller.php, line 823
# str 703 
#vim /usr/share/nginx/www/c2/yfi_cake/controllers/third_parties_controller.php
#vim /usr/share/nginx/www/cakephp-cakephp-a9b5b0c/yfi_cake/views/third_parties/json_create_voucher.ctp

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)
define('debug', default=False)
define('disable-log', default=False)
define('disable-console-log', default=False)
define('daemon', default=False)

config = {
        'proxy_host': '58.59.21.228',
        'proxy_port': 25,
        'proxy_username': 'yz',
        'proxy_password': 'fangbinxingqusi',
}

#tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
tornado.httpclient.AsyncHTTPClient()

class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('http://10.1.0.1:3990/logout')


class AutoHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='yfi')
            cur = conn.cursor()
            cur.execute("SELECT username FROM radcheck limit 5")
            for r in cur.fetchall():
                self.write("sql: {0}".format(r))
            cur.close()
            conn.close()
        except Exception:
            raise tornado.web.HTTPError(500)
        

class MainHandler(tornado.web.RequestHandler):
    ''' /auto
    Автоматически генерируем пароль для входа
    '''
    @tornado.web.asynchronous
    def get(self):
        """ параметры от CoovaChilli
        http://10.1.0.1/?res=notyet&uamip=10.1.0.1&uamport=3990&challenge=a3ed364c68c5f972c232b4edc91b2d75&called=00-0C-29-A1-BC-F1&mac=F4-6D-04-39-21-98&ip=10.1.0.213&nasid=nas01&sessionid=521700e500000012&userurl=http%3a%2f%2fwww.google.com%2fig%2fredirectdomain%3fbrand%3dASUT%26bmod%3dASUT&md=832E8393257075F49A8791FF26D6BAD6
        # http://10.1.0.1/coova_json/auto.php?
        res=notyet
        uamip=10.1.0.1
        uamport=3990
        challenge=a3ed364c68c5f972c232b4edc91b2d75
        called=00-0C-29-A1-BC-11
        mac=F4-6D-04-39-21-00
        ip=10.1.0.2
        nasid=nas01
        sessionid=521700e500000012
        userurl=http%3a%2f%2fwww.google.com%2fig%2fredirectdomain%3fbrand%3dASUT%26bmod%3dASUT
        md=832E8393257075F49A8791FF26D6BAD6
        """

        res = self.get_argument("res", 'notyet')
        if(res == 'success'):
            userurl = self.get_argument("userurl", self.settings.get('default_url'))
            regex =re.compile("10.1.0.1/coova_json/:")
            #if regex.search(string):
            #    res = 
            #if (preg_match("/10\.1\.0\.1\/coova_json\/:\/\//i", $userurl))
            #$dsite = '';
            #$pattern = "/10\.1\.0\.1\/coova_json\/:\/\//i";
            #$userurl = preg_replace($pattern, $dsite, $userurl);
            self.write("redirect: {0}".format(userurl))
            #self.redirect(userurl)
            return
        elif(res == 'failed'):
            self.messages = 'Error'
        else:
            self.messages = None
        # http://109.237.88.203/c2/yfi_cake/third_parties/json_create_voucher/?key=123456789&voucher_value=1-00-00-00&profile=Free30min&realm=OceanPLaza
        # {"json":{"status":"ok"},"voucher":{"username":"100000@op","password":"PTrvs05G","id":false}}
        #INSERT INTO `vouchers` (`radcheck_id`, `user_id`, `realm_id`, `profile_id`, `modified`, `created`, `id`) VALUES (NULL, '49d09fb4-f23c-4b30-9a50-2b0ba509ff00', '49d09ec6-5480-45d4-a5ae-2b0ea509ff00', '520122be-0fb4-4b71-9fa8-03f46ded58cb', '2013-08-22 22:40:24', '2013-08-22 22:40:24', '52167738-9dcc-4ed3-900c-2fd36ded58cb') 
        data = dict(key=self.settings.get('key'), voucher_value=self.settings.get('voucher_value'), profile=self.settings.get('profile'), realm=self.settings.get('realm'))
        vg = tornado.httputil.url_concat(self.settings.get('voucher_url'), data)
        #http_c = tornado.httpclien.tHTTPClient()
        #response = http_c.fetch(vaucher_new, data=urlencode(data))
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch(vg, callback=self.async_callback(self.on_response))
        #http.fetch("{0}/c2/yfi_cake/third_parties/json_create_voucher/?key=123456789&voucher_value=1-00-00-00&profile=Free30min&realm=OceanPLaza".format(hotspot_portal), callback=self.async_callback(self.on_response))
        #name = tornado.escape.xhtml_escape(self.current_user)
        self.loader = Loader(self.settings.get('template_path'))
        #self.write("url: " + vg)
        #self.finish()

    def on_response(self, response):
        if response.error: raise tornado.web.HTTPError(500)
        
        uamip = self.get_argument("uamip", None)
        uamport = self.get_argument("uamport", None)
        challenge = self.get_argument("challenge", None)
        called = self.get_argument("called", None)
        mac = self.get_argument("mac", None)
        ip = self.get_argument("ip", None)
        nasid = self.get_argument("nasid", None)
        sessionid = self.get_argument("sessionid", None)
        userurl = self.get_argument("userurl", None)
        md = self.get_argument("md", None)

        res_password = ''
        res_username = ''
        try:
            res_json = tornado.escape.json_decode(response.body)
            if(res_json['json']['status'] == 'ok'): 
                res_password = res_json['voucher']['username']
                res_username = res_json['voucher']['password']
            self.write(self.loader.load('auto.html').generate(uamip=uamip, uamport=uamport, challenge=challenge, userurl=userurl, password=res_password, username=res_username, login_url=self.settings.get('login_url'), messages=self.messages))
        except ValueError:
            pass
        finally:
            self.finish()

def main():
    parser = OptionParser()
    parser.add_option('-d', '--debug', action='store_true', default=False)
    parser.add_option('--disable-log', dest='nolog', action='store_true', default=False)
    parser.add_option('--disable-console-log', dest='noconsole', action='store_true', default=False)
    parser.add_option('-D', '--daemon', action='store_true', default=False)

    (options, args) = parser.parse_args()

    if options.daemon:
        demonize(options.realm, options)

    if options.debug:
        listen_on = '0.0.0.0'
    else:
        listen_on = '127.0.0.1'
        
    #if not options.nolog: 
    #    teg.enable_log('example.log', debug = options.debug, console = not options.noconsole)
    
    #settings = teg.Settings.instance()
    settings = {
		"cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
   		"login_url": "/coova_json/login.php",
        "port": 8889,
        'template_path': os.path.join(os.path.dirname(__file__), "templates"),
        'static_path': os.path.join(os.path.dirname(__file__), "static"),
        'voucher_url': "http://127.0.0.1/c2/yfi_cake/third_parties/json_create_voucher/",
        'key': '123456789',
        'voucher_value': '0-01-00-00',
        'profile': 'Free30min',
        'realm': 'OceanPLaza',
        'default_url': 'http://oceanplaza.com.ua/'
    }

    #settings.set('debug', options.debug)
    
    ## Settings for tornado app, as usual
    #appSettings = {
    #    'cookie_secret': 'MySecretSting',
    #    'login_url': os.path.join(settings.get('ui_prefix'), 'login'),
    #    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    #    'template_path' : os.path.join(os.path.dirname(__file__), 'templates')
    #}
    
    urlMap = [
        #    #Index page renderer
        (r"/", MainHandler),
        (r"/go", MainHandler),
        (r"/t", AutoHandler),
    #    (r'/ui',                                ui.Index),
    #    
    #    # REST controllers
    #    (r'/api/page',                          api.Page),
    #    (r'/api/page/(?P<oid>[0-9]*)',          api.Page),
    #    (r'/api/tag',                           api.Tag),
    #    (r'/api/tag/(?P<oid>[0-9]*)',           api.Tag),
    #    (r'/api/comment',                       api.Comment),
    #    (r'/api/comment/(?P<oid>[0-9]*)',       api.Comment)
        (r"/logout", LogoutHandler),
    ]
    
    #application = tornado.web.Application(urlMap, **appSettings)
    application = tornado.web.Application(urlMap, **settings)
    application.listen(settings.get('port'), listen_on)
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == '__main__': main()
