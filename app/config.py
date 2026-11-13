import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-dev-insegura')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    VIACEP_BASE_URL = os.getenv('VIACEP_BASE_URL', 'https://viacep.com.br/ws')
    VIACEP_TIMEOUT = 5


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///professores_dev.db'
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class ProductionConfig(Config):
    DEBUG = False

    @staticmethod
    def _ajustar_url(url):
        if url and url.startswith('postgresql://'):
            return url.replace('postgresql://', 'postgresql+psycopg://', 1)
        return url

    SQLALCHEMY_DATABASE_URI = _ajustar_url(os.getenv('DATABASE_URL'))


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}

