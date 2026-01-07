DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'votesphere',
    'raise_on_warnings': False,
    'autocommit': True,
    'connect_timeout': 10
}

DEFAULT_SYSTEM_SETTINGS = [
    ('election_name', 'School Election 2025'),
    ('election_date', '2025-12-19'),
    ('election_status', 'inactive'),
    ('election_duration', '3600'),
    ('election_target_time', ''),
    ('min_app_version', '2.3')
]