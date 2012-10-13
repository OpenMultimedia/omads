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


def get_render(medium):
    return web.template.render(projectdir + '/templates', base='base', globals={'medium': medium})

class Index:

    def GET(self, medium):
        """ Show page """
        banners = model.get_banners(medium)
        
        return get_render(medium).index(banners)
        #return render.index(banners)


class View:

    def GET(self, medium, id):
        """ View single post """
        banner = model.get_banner(medium, int(id))
        return get_render(medium).view(banner)


class New:

    form = web.form.Form(
        #web.form.Dropdown('medium', args=('telesur', 'vtv'), description="Medio:"),
        web.form.Dropdown('zone', args=(('A', 'A (300x600)'), ('B', 'B (300x250)'), ('C', 'C (468x60)' ), ('D', 'D (728x90)'), ('E', 'E (234x60)')), description="Zona:"),
        web.form.File('file', description="Archivo:"),
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
        fout = open(projectdir + '/' + filename, 'w') # creates the file where the uploaded file should be stored
        fout.write(x.file.file.read()) # writes the uploaded file to the newly created file.
        fout.close() # closes the file, upload complete.

        model.new_banner(medium, form.d.zone, filename, form.d.link)
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
            filename='static/%s.jpg' % uuid.uuid4()
            fout = open(projectdir + '/' + filename, 'w') # creates the file where the uploaded file should be stored
            fout.write(x.file.file.read()) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
            if os.path.exists(projectdir + '/' + banner.file):
                os.remove(projectdir + '/' + banner.file)
        else:
            filename = banner.file
            
        model.update_banner(medium, int(id), form.d.zone, filename, form.d.link)
        raise web.seeother('/%s' % medium)



application = web.application(urls, globals()).wsgifunc()

