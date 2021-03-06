# -*- coding: utf-8 -*- #
from settings import *
import web, datetime
 
#db = web.database(dbn='mysql', host=DB['host'], db=DB['name'], user=DB['user'], pw=DB['pass'])
db = web.database(dbn='sqlite', db='bd')

def get_banners(medium, zone='', subzone=''):
    and_where = ' AND zone=$zone' if zone else ''
    if isinstance(subzone, basestring): and_where+= ' AND subzone=$subzone'
    return db.select('banner', where='medium=$medium'+and_where, order='medium, zone, subzone, id DESC', vars=locals())

def get_banner(medium, id):
    try:
        return db.select('banner', where='medium=$medium AND id=$id', vars=locals())[0]
    except IndexError:
        return None

def banner_get_type(banner):
    import os
    
    name, ext = os.path.splitext(banner.file)
    if ext in IMAGE_FILE_EXTENSIONS:
        return 'image'
    if ext in VIDEO_FILE_EXTENSIONS:
        return 'video'
    if ext in FLASH_FILE_EXTENSIONS:
        return 'flash'
        
def banner_get_zone_tuple(banner):
    for zone in ZONES:
        if zone[0] == banner.zone:
            return zone
     
        
def get_delivery_banner(medium, zone, subzone=''):
    try:
        and_where = ' AND subzone=$subzone' if subzone else ''
        #return db.select('banner', where='medium=$medium AND zone=$zone'+and_where, order='RAND ()', limit=1, vars=locals())[0]
        return db.query('SELECT *, (RAND() * weight) AS SCORE FROM banner WHERE weight>0 AND medium=$medium AND zone=$zone '+ and_where +' ORDER BY SCORE DESC LIMIT 1', vars=locals())[0];
    except IndexError:
        return None

def new_banner(medium, zone, file, link='', link_mode=0, weight=50, subzone=''):
    db.insert('banner', medium=medium, zone=zone, subzone=subzone, file=file, link=link, link_mode=link_mode, weight=weight, created_at=datetime.datetime.utcnow())

def del_banner(medium, id):
    import os
    try:
        banner = db.select('banner', where='medium=$medium AND id=$id', vars=locals())[0]
        banner_type = banner_get_type(banner)
        path = '%s/%s' % (PROJECT_DIR, banner.file)
        db.delete('banner', where='medium=$medium AND id=$id', vars=locals())
        if banner.file and (os.path.exists(path)):
            os.remove(path)
            if banner_type == 'video':
                os.remove('%s.jpg' % path)
    except:
        pass

def update_banner(medium, id, zone, file, link='', link_mode=0, weight=50, subzone=''):
    db.update('banner', where="medium=$medium AND id=$id", vars=locals(),
       zone=zone, file=file, link=link, link_mode=link_mode, weight=weight, subzone=subzone)

def increment_banner_click_count(medium, id):
    db.query('UPDATE banner SET clicks = (clicks + 1) WHERE medium=$medium AND id=$id', vars=locals());

def increment_banner_views(medium, id, views):
    db.query('UPDATE banner SET views = (views + $views) WHERE medium=$medium AND id=$id', vars=locals());
