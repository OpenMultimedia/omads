import os, sys
import memcache
projectdir = os.path.dirname(__file__)
sys.path.append(projectdir)

import web
import model

urls = (
    '/(.+)/(.+)/click/', 'Click',
    '/(.+)/(.+)/', 'Banners',
    '/.*\.php.*', 'Default', # para las consultas que lleguen esperando OpenX
)

class Banners:
    def GET(self, medium, zone):
        web.header("Content-Type","text/html; charset=utf-8")
        
        mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        banner_key = str('banner_%s_%s' % (medium, zone))
        banner_counting_key = 'counting_%s' % banner_key
        banner_views_key = 'views_%s' % banner_key
        
        banner = mc.get(banner_key)
        if not banner:
            banner = model.get_delivery_banner(medium, zone)
            mc.set(banner_key, banner, 2)
        
        if not banner: return web.notfound()
        
        if not mc.get(banner_counting_key):
            views = mc.get(banner_views_key)
            if views: model.increment_banner_views(banner.medium, banner.id, int(views))
            mc.set(banner_views_key, 0)
            mc.set(banner_counting_key, True, 30)
        
        mc.incr(banner_views_key)
        
                
        banner_html = '<img style="border:0;" src="/%s" />' % (banner.file)
        if banner.link:
            banner_html = '<a href="/%s/%s/click/" target="_top">%s</a>' % (banner.medium, banner.zone, banner_html)
        return '<html><body class="banner-%s" style="margin:0;">%s</body></html>' % (banner.id, banner_html)
      
class Click:
    def GET(self, medium, zone):
        banner = model.get_delivery_banner(medium, zone)
        if not banner: return web.notfound()
        model.increment_banner_click_count(medium, banner.id)
        raise web.seeother(banner.link)
              
class Default:
    def GET(self):
        return '<html></html>'

application = web.application(urls, globals()).wsgifunc()