# -*- coding: utf-8 -*- #
""" OMAds frontend """
import os, sys
sys.path.append(os.path.dirname(__file__))

from settings import *
import web
import model
import memcache


urls = (
    '/(.+)/(.+)/(\d+)/click/', 'Click',
    '/(.+)/(.+)/(.+)/', 'Banners',
    '/(.+)/(.+)/', 'Banners',
)

BANNER_CACHE_SECONDS = 1
SOTRE_VIEWS_INTERVAL_SECONDS = 30

class Banners:
    def GET(self, medium, zone, subzone=''):
        # memcached connection and keys
        mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        banner_key = str('banner_%s_%s_%s' % (medium, zone, subzone))
        banner_counting_key = 'counting_%s' % banner_key
        banner_views_key = 'views_%s' % banner_key
        
        # get banner from cache or database
        banner = mc.get(banner_key)
        if not banner:
            banner = model.get_delivery_banner(medium, zone, subzone)
            mc.set(banner_key, banner, BANNER_CACHE_SECONDS)
        
        # banner not found
        if not banner: return web.notfound()
        
        # if necessary store views count in database 
        if not mc.get(banner_counting_key):
            views = mc.get(banner_views_key)
            if views: model.increment_banner_views(banner.medium, banner.id, int(views))
            mc.set(banner_views_key, 0)
            mc.set(banner_counting_key, True, SOTRE_VIEWS_INTERVAL_SECONDS)
        
        # increment views count in cache
        mc.incr(banner_views_key)
        
        # build response
        banner_html = '<img style="border:0;" src="/%s" />' % (banner.file)
        target = '_top' if banner.link_mode == 0 else '_blank'
        if banner.link: banner_html = '<a href="/%s/%s/%s/click/" target="%s">%s</a>' % (banner.medium, banner.zone, banner.id, target, banner_html)
        web.header("Content-Type","text/html; charset=utf-8")
        
        return '<html><body class="banner-%s" style="margin:0;">%s</body></html>' % (banner.id, banner_html)
      
class Click:
    def GET(self, medium, zone, id):
        banner = model.get_banner(medium, id)
        if not banner or banner.zone != zone: return web.notfound()
        model.increment_banner_click_count(medium, banner.id)
        
        raise web.seeother(banner.link)

application = web.application(urls, globals()).wsgifunc()
# if __name__ == '__main__':
#     app = web.application(urls, globals())
#     app.run()