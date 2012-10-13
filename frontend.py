from random import randint
import web
import model

urls = (
    '/(.+)/(.+)/', 'banners',
    '/.*\.php.*', 'default', # para las consultas que lleguen esperando OpenX
)

class banners:
    def GET(self, medium, zone):
        web.header("Content-Type","text/html; charset=utf-8")
        try:
            banner = model.get_delivery_banner(medium, zone)
            if not banner:
                return 'a'
                
            banner_html = '<img style="border:0;" src="/static/%s" />' % (banner.file)
            if banner.link:
                banner_html = '<a href="%s">%s</a>' % (banner.link, banner_html)
            return '<html><body class="banner-%s" style="margin:0;">%s</body></html>' % (banner.id, banner_html)
        except:
            return web.notfound()
            
class default:
    def GET(self):
        return '<html></html>'

application = web.application(urls, globals())

if __name__ == '__main__':
    application.run()
