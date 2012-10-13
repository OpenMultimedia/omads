import os, sys
projectdir = os.path.dirname(__file__)
sys.path.append(projectdir)

import web, datetime

db = web.database(dbn='mysql', db='omads_data', user='root', pw='pass')
#db = web.database(dbn='sqlite', db=projectdir + '/db')

def get_banners(medium):
    return db.select('banner', where='medium=$medium', order='medium, zone, id DESC', vars=locals())

def get_banner(medium, id):
    try:
        return db.select('banner', where='medium=$medium AND id=$id', vars=locals())[0]
    except IndexError:
        return None
        
def get_delivery_banner(medium, zone):
    try:
        return db.select('banner', where='medium=$medium AND zone=$zone', order='RAND ()', limit=1, vars=locals())[0]
    except IndexError:
        return None

def new_banner(medium, zone, file, link):
    db.insert('banner', medium=medium, zone=zone, file=file, link=link, created_at=datetime.datetime.utcnow())

def del_banner(medium, id):
    import os
    try:
        banner = db.select('banner', where='medium=$medium AND id=$id', vars=locals())[0]
        db.delete('banner', where='medium=$medium AND id=$id', vars=locals())
        if banner.file and (os.path.exists(banner.file)): os.remove(banner.file)
    except:
        pass

def update_banner(medium, id, zone, file, link):
    db.update('banner', where="medium=$medium AND id=$id", vars=locals(),
       zone=zone, file=file, link=link)
