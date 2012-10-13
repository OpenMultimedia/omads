import web, datetime

#db = web.database(dbn='mysql', db='omads_data', user='omads_user')
db = web.database(dbn='sqlite', db='db')

def get_banners():
    return db.select('banner', order='medium, zone, id DESC')

def get_banner(id):
    try:
        return db.select('banner', where='id=$id', vars=locals())[0]
    except IndexError:
        return None
        
def get_delivery_banner(medium, zone):
    try:
        return db.select('banner', where='medium=$medium AND zone=$zone', order='RANDOM()', limit=1, vars=locals())[0]
    except IndexError:
        return None

def new_banner(medium, zone, file, link):
    db.insert('banner', medium=medium, zone=zone, file=file, link=link, created_at=datetime.datetime.utcnow())

def del_banner(id):
    import os
    try:
        banner = db.select('banner', where='id=$id', vars=locals())[0]
        db.delete('banner', where="id=$id", vars=locals())
        if banner.file and (os.path.exists(banner.file)): os.remove(banner.file)
    except:
        pass

def update_banner(id, medium, zone, file, link):
    db.update('banner', where="id=$id", vars=locals(),
       medium=medium, zone=zone, file=file, link=link)