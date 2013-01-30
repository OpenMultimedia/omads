# -*- coding: utf-8 -*- #
import os, sys

PROJECT_DIR = os.path.dirname(__file__)

# TODO: integrate media to application logic, for instance in a db table
# media sites or client separation
MEDIA_RE = 'telesur|vtv|cienciasalud'

# MySQL database connection
DB = {
    'host': 'localhost',
    'name': 'omads_data',
    'user': 'root',
    'pass':  'pass',
}

# Zone configuration bassed on banners' size
ZONES = (
    ('A', 300, 600),
    ('B', 300, 250),
    ('C', 468, 60),
    ('D', 728, 90),
    ('E', 234, 60),
    ('F', 300, 50),
    ('G', 220, 70),
)

# time to cache banner query. A higher value improves performance but reduces randomness
BANNER_CACHE_SECONDS = 4

# time interval to store banner views count from memory to database.
SOTRE_VIEWS_INTERVAL_SECONDS = 30
