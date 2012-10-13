""" OMAds backend """
from random import randint
import web
import model

### Url mappings

urls = (
    '/', 'Index',
    '/view/(\d+)', 'View',
    '/new', 'New',
    '/delete/(\d+)', 'Delete',
    '/edit/(\d+)', 'Edit',
)


### Templates
t_globals = {
    'datestr': web.datestr
}
render = web.template.render('templates', base='base', globals=t_globals)


class Index:

    def GET(self):
        """ Show page """
        banners = model.get_banners()
        return render.index(banners)


class View:

    def GET(self, id):
        """ View single post """
        banner = model.get_banner(int(id))
        return render.view(banner)


class New:

    form = web.form.Form(
        web.form.Dropdown('medium', args=('telesur', 'vtv'), description="Medio:"),
        web.form.Dropdown('zone', args=(('A', 'A (300x600)'), ('B', 'B (300x250)'), ('C', 'C (468x60)' ), ('D', 'D (728x90)'), ('E', 'E (234x60)')), description="Zona:"),
        web.form.File('file', description="Archivo:"),
        web.form.Textbox('link', size=50, description="Link:"),
        web.form.Button('Guardar'),
    )

    def GET(self):
        form = self.form()
        return render.new(form)

    def POST(self):
        import uuid
        form = self.form()
        x = web.input(file={})
        if not form.validates() or not 'file' in x:
            return render.new(form)

        filename='static/%s.jpg' % uuid.uuid4()
        fout = open(filename, 'w') # creates the file where the uploaded file should be stored
        fout.write(x.file.file.read()) # writes the uploaded file to the newly created file.
        fout.close() # closes the file, upload complete.

        model.new_banner(form.d.medium, form.d.zone, filename, form.d.link)
        raise web.seeother('/')


class Delete:

    def POST(self, id):
        model.del_banner(int(id))
        raise web.seeother('/')


class Edit:

    def GET(self, id):
        banner = model.get_banner(int(id))
        form = New.form()
        form.fill(banner)
        return render.edit(banner, form)


    def POST(self, id):
        import os
        import uuid
        form = New.form()
        x = web.input(file={})
        banner = model.get_banner(int(id))
        if not form.validates():
            return render.edit(banner, form)
        
        if 'file' in x and x.file.filename:
            filename='static/%s.jpg' % uuid.uuid4()
            fout = open(filename, 'w') # creates the file where the uploaded file should be stored
            fout.write(x.file.file.read()) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
            if os.path.exists(banner.file):
                os.remove(banner.file)
        else:
            filename = banner.file
            
        model.update_banner(int(id), form.d.medium, form.d.zone, filename, form.d.link)
        raise web.seeother('/')



app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()