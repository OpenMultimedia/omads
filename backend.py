# -*- coding: utf-8 -*- #
""" OMAds backend """
import os, sys
sys.path.append(os.path.dirname(__file__))

from settings import *
import web
import model
from utils import *

urls = (
    '/(%s)' % MEDIA_RE, 'Index',
    '/(%s)/view/(\d+)' % MEDIA_RE, 'View',
    '/(%s)/new' % MEDIA_RE, 'New',
    '/(%s)/delete/(\d+)' % MEDIA_RE, 'Delete',
    '/(%s)/edit/(\d+)' % MEDIA_RE, 'Edit',
)

def get_render(medium):
    return web.template.render(PROJECT_DIR + '/templates', base='base', globals={
        'medium': medium,
        'zones': ZONES,
        'formatWithCommas': formatWithCommas, 
    })
    
VE_STATES = (
    (-2, u'Cualquier ubicación'),
    (-1, 'Extranjero'),
    (0, 'Todo Venezuela'),
    (1, 'Amazonas'),
    (2, 'Anzoategui'),
    (3, 'Apure'),
    (4, 'Aragua'),
    (5, 'Barinas'),
    (6, 'Bolívar'),
    (7, 'Carabobo'),
    (8, 'Cojedes'),
    (9, 'Delta Amacuro'),
    (10, 'Dependencias Federales'),
    (11, 'Distrito Capital'),
    (12, 'Falcón'),
    (13, 'Guárico'),
    (14, 'Lara'),
    (15, 'Mérida'),
    (16, 'Miranda'),
    (17, 'Monagas'),
    (18, 'Nueva Esparta'),
    (19, 'Portuguesa'),
    (20, 'Sucre'),
    (21, 'Táchira'),
    (22, 'Trujillo'),
    (23, 'Vargas'),
    (24, 'Yaracuy'),
    (25, 'Zulia'),
)

class Index:

    def GET(self, medium):
        """ View banner list """
        zone = web.input().zone if 'zone' in web.input() else ''
        banners = model.get_banners(medium, zone)
        return get_render(medium).index(banners, zone)


class View:

    def GET(self, medium, id):
        """ View single banner """
        banner = model.get_banner(medium, int(id))
        return get_render(medium).view(banner)

def get_zone_for_file(file_image):
    from PIL import Image
    try:
        s = Image.open(file_image).size
        for z in ZONES:
            if s[0] == z[1] and s[1] == z[2]: return z[0]
        return ''
    except:
        return ''

class New:

    form = web.form.Form(
        #web.form.Dropdown('medium', args=('telesur', 'vtv'), description="Medio:"),
        web.form.File('file', description="Archivo:", post='(formato JPG)'),
        web.form.Dropdown('zone', args=[('auto', 'Determinar con base en el archivo'), ('', 'Sin Zona')] + [(z[0], '%s (%sx%s)' % (z[0], z[1], z[2])) for z in ZONES], description="Zona:"),
        web.form.Dropdown('subzone', args=([('', '---')] + [str(x) for x in range(1, 20)]), description="Sub-zona:", post='(opcional)'),
        web.form.Textbox('link', size=50, description="Link:", post='(opcional)'),
        web.form.Dropdown('link_mode', args=((0, u'Abrir en la misma página'), (1, 'Abrir en nueva página o pestaña'), (2, 'Abrir en ventana emergente (pop-up)')), description="Modo de link:"),
        web.form.Dropdown('weight', args=range(0, 100, 10), description="Peso:", value=50, post='(aumenta o disminuye la probabilidad de mostrar el banner)'),
        web.form.Dropdown('states', disabled='disabled', args=VE_STATES, multiple='multiple', value=-2, size=8, description="Geo-despliegue:", post='Muestra banner en la(s) region(es) seleccionada(s).<br />Mantener preisonado crtl ó shift para seleccionar más de una ubicación'),
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
        path = '%s/%s' % (PROJECT_DIR, filename)
        fout = open(path, 'w')
        fout.write(x.file.file.read())
        fout.close()
        
        if form.d.zone == 'auto':
            zone = get_zone_for_file(open(path, 'r'))
        else:
            zone = form.d.zone

        model.new_banner(medium, zone, filename, form.d.link, form.d.link_mode, form.d.weight, form.d.subzone)
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
        
        if 'file' in x and x.file:
            image_file = x.file.file
            filename='static/%s.jpg' % uuid.uuid4()
            fout = open('%s/%s' % (PROJECT_DIR, filename), 'w')
            fout.write(image_file.read())
            fout.close()
            if os.path.exists('%s/%s' % (PROJECT_DIR, banner.file)):
                os.remove('%s/%s' % (PROJECT_DIR, banner.file))
        else:
            image_file = None
            filename = banner.file
        
        if form.d.zone == 'auto':
            zone = get_zone_for_file(image_file or open(PROJECT_DIR + '/' + filename, 'r'))
        else:
            zone = form.d.zone
            
        model.update_banner(medium, int(id), zone, filename, form.d.link, form.d.link_mode, form.d.weight, form.d.subzone)
        raise web.seeother('/%s' % medium)


if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
else:
    application = web.application(urls, globals()).wsgifunc()
