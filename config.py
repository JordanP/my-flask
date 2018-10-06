class Config(object):
    DEBUG = False
    TESTING = False
    TARGET_BACKENDS = {}


class ConfigProd(Config):
    SQREEN_WEBHOOK_SECRET_KEY = b'prodsecretkey'
    TARGET_BACKENDS = {
        'log': {
            'class': 'myapp.models.LogTargetBackend',
            'arguments': {
                'log_filename': './sqreenio.logs'
            }
        },
        'http': {
            'class': 'myapp.models.HTTPTargetBackend',
            'arguments': {
                'remote_url': 'https://google.fr'
            }
        }
    }


class ConfigTest(Config):
    SQREEN_WEBHOOK_SECRET_KEY = b'testsecret'
    DEBUG = True
    TESTING = True
