""" OMAds backend """
import os, sys
projectdir = os.path.dirname(__file__)
sys.path.append(projectdir)

import web
import model

### Url mappings

MEDIA_RE = 'telesur|vtv'

urls = (
    '/(%s)' % MEDIA_RE, 'Index',
    '/(%s)/view/(\d+)' % MEDIA_RE, 'View',
    '/(%s)/new' % MEDIA_RE, 'New',
    '/(%s)/delete/(\d+)' % MEDIA_RE, 'Delete',
    '/(%s)/edit/(\d+)' % MEDIA_RE, 'Edit',
)

ZONES = (('A', 'A (300x600)'), ('B', 'B (300x250)'), ('C', 'C (468x60)' ), ('D', 'D (728x90)'), ('E', 'E (234x60)'))

def get_render(medium):
    return web.template.render(projectdir + '/templates', base='base', globals={'medium': medium, 'zones': ZONES})

class Index:

    def GET(self, medium):
        """ View banner list """
        zone = web.input().zone if 'zone' in web.input() else ''
        banners = model.get_banners(medium, zone)
        return get_render(medium).index(banners)


class View:

    def GET(self, medium, id):
        """ View single banner """
        banner = model.get_banner(medium, int(id))
        return get_render(medium).view(banner)

def get_zone_for_file(file_image):
    from PIL import Image
    try:
        s = Image.open(file_image).size
        if s[0] == 300 and s[1] == 600: return 'A'
        if s[0] == 300 and s[1] == 250: return 'B'
        if s[0] == 468 and s[1] == 60: return 'C'
        if s[0] == 728 and s[1] == 90: return 'D'
        if s[0] == 234 and s[1] == 60: return 'E'
        return ''
    except:
        return ''

class New:

    form = web.form.Form(
        #web.form.Dropdown('medium', args=('telesur', 'vtv'), description="Medio:"),
        web.form.File('file', description="Archivo:"),
        web.form.Dropdown('zone', args=(('auto', 'Determinar por archivo'), ('', 'Sin Zona')) + ZONES, description="Zona:"),
        web.form.Textbox('link', size=50, description="Link:"),
        web.form.Button('Guardar'),
    )

    def GET(self, medium):
        form = self.form()
        return get_render(medium).new(form)

    def POST(self, medium):
        import uuid
        form = self.form()
        x = web.input(file={})
        if not form.validates() or not 'file' in x:
            return get_render(medium).new(form)

        filename='static/%s.jpg' % uuid.uuid4()
        path = '%s/%s' % (projectdir, filename)
        fout = open(path, 'w') # creates the file where the uploaded file should be stored
        fout.write(x.file.file.read()) # writes the uploaded file to the newly created file.
        fout.close() # closes the file, upload complete.
        
        if form.d.zone == 'auto':
            zone = get_zone_for_file(open(path, 'r'))
        else:
            zone = form.d.zone

        model.new_banner(medium, zone, filename, form.d.link)
        raise web.seeother('/%s' % medium)


class Delete:

    def POST(self, medium, id):
        model.del_banner(medium, int(id))
        raise web.seeother('/%s' % medium)


class Edit:

    def GET(self, medium, id):
        banner = model.get_banner(medium, int(id))
        form = New.form()
        form.fill(banner)
        return get_render(medium).edit(medium, banner, form)


    def POST(self, medium, id):
        import uuid
        form = New.form()
        x = web.input(file={})
        banner = model.get_banner(medium, int(id))
        if not form.validates():
            return get_render(medium).edit(medium, banner, form)
        
        if 'file' in x and x.file.filename:
            image_file = x.file.file
            filename='static/%s.jpg' % uuid.uuid4()
            fout = open(projectdir + '/' + filename, 'w') # creates the file where the uploaded file should be stored
            fout.write(image_file.read()) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
            if os.path.exists(projectdir + '/' + banner.file):
                os.remove(projectdir + '/' + banner.file)
        else:
            image_file = None
            filename = banner.file
        
        if form.d.zone == 'auto':
            zone = get_zone_for_file(image_file or open(projectdir + '/' + filename, 'r'))
        else:
            zone = form.d.zone
            
        model.update_banner(medium, int(id), zone, filename, form.d.link)
        raise web.seeother('/%s' % medium)



application = web.application(urls, globals()).wsgifunc()

