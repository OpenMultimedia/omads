# -*- coding: utf-8 -*- #
""" OMAds frontend """
import os, sys
sys.path.append(os.path.dirname(__file__))

from settings import *
import web
import model
import memcache
import re


urls = (
    '/(.+)/(.+)/(\d+)/click/', 'Click',
    '/(.+)/(.+)/(.+)/', 'Banners',
    '/(.+)/(.+)/', 'Banners',
)

#POPUP_RE = re.compile(r'(.+),\s*(\d+)\s*,\s*(\d+)')

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
        banner_type = model.banner_get_type(banner)
        banner_zone = model.banner_get_zone_tuple(banner)
        if banner_type == 'image':
            banner_html = '<img style="border:0;width:%s;height:%s;" src="/%s" />' % (banner_zone[1], banner_zone[2], banner.file)
        elif banner_type == 'video':
            banner_url = 'http://ad.openmultimedia.biz/%s' % banner.file
            banner_html = '''
            <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=9,0,0,0" width="%s" height="%s" id="OMAdPlayer" align="middle">
            <param name="allowScriptAccess" value="*" /> <param name="allowFullScreen" value="true" />
            <param name="movie" value="http://www.platipus.nl/flvplayer/download/1.0/FLVPlayer.swf?video=%s" />
            <param name"quality" value="high" /><param name="bgcolor" value="#0000" />
            <embed src="http://www.platipus.nl/flvplayer/download/1.0/FLVPlayer.swf?video=%s"
                   quality="high" bgcolor="#000000" width="%s" height="%s" name="VideoPlayer" align="middle" allowScriptAccess="*" allowFullScreen="true"
                   type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" /> </object>
            ''' % (banner_zone[1], banner_zone[2], banner_url, banner_url, banner_zone[1], banner_zone[2])
            #banner_html = '<img style="border:0;width:%s;height:%s;" src="/%s.jpg" />' % (banner_zone[1], banner_zone[2], banner.file)
        elif banner_type == 'flash':
            banner_html = '<img style="border:0;width:%s;height:%s;" src="/%s" />' % (banner_zone[1], banner_zone[2], banner.file)
        else:
            banner_html = '<img style="border:0;width:%s;height:%s;" src="/%s" />' % (banner_zone[1], banner_zone[2], banner.file)
        
        if banner.link:
            banner_href = '/%s/%s/%s/click/' % (banner.medium, banner.zone, banner.id)
            if banner.link_mode == 2:
                banner_href = "javascript:window.open('%s','','width=800,height=600,location=no,menubar=no,status=no,toolbar=no');return false;" % banner_href
                banner_html = '<a href="#" onclick="%s">%s</a>' % (banner_href, banner_html)
            else:
                target = '_top' if banner.link_mode == 0 else '_blank'
                banner_html = '<a href="%s" target="%s">%s</a>' % (banner_href, target, banner_html)
        
        web.header("Content-Type","text/html; charset=utf-8")        
        return '<html><body class="banner-%s" style="margin:0;">%s</body></html>' % (banner.id, banner_html)
      
class Click:
    def GET(self, medium, zone, id):
        banner = model.get_banner(medium, id)
        if not banner or banner.zone != zone: return web.notfound()
        model.increment_banner_click_count(medium, banner.id)
        
        raise web.seeother(banner.link)


if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
else:
    application = web.application(urls, globals()).wsgifunc()