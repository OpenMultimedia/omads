# -*- coding: utf-8 -*- #
import os, sys

PROJECT_DIR = os.path.dirname(__file__)

MEDIA_RE = 'telesur|vtv|cienciasalud'

ZONES = (
    ('A', 300, 600),
    ('B', 300, 250),
    ('C', 468, 60),
    ('D', 728, 90),
    ('E', 234, 60),
    ('F', 300, 50),
    ('G', 220, 70),
)

# MySQL db access
DB = {
    'host': 'localhost',
    'name': 'omads_data',
    'user': 'root',
    'pass':  'pass',
}