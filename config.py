import os

# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    ELASTIC_SEARCH_QUEUE_NAME = os.getenv("ELASTIC_SEARCH_QUEUE_NAME", "catalog_indexing")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    QUEUE_ENABLE = os.getenv("QUEUE_ENABLE", "False") == "True"
    API_TOKEN = os.getenv("API_TOKEN", "testing_random_123")
    MAX_CONSUME_MESSAGE_TIME = int(os.getenv("MAX_CONSUME_MESSAGE_TIME", "30"))
    CONSUMER_MAX_WORKERS = int(os.getenv("CONSUMER_MAX_WORKERS", "100"))
    BULK_CHUNK_SIZE = int(os.getenv("BULK_CHUNK_SIZE", "500"))
    MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL", "mongodb://localhost:27017")
    ELASTIC_SEARCH_URL = os.getenv("ELASTIC_SEARCH_URL", "http://localhost:9200")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    BHASHINI_USERID = os.getenv("BHASHINI_USERID", "userid")
    BHASHINI_ULCA_API_KEY = os.getenv("BHASHINI_ULCA_API_KEY", "apikey")
    LANGUAGE_LIST = [lang.strip() for lang in os.getenv("LANGUAGE_LIST", "").split(",")]
    IS_TEST = os.getenv("IS_TEST", "False") == "True"
    PARALLEL_PROCESSES = int(os.getenv("PARALLEL_PROCESSES", "10"))


class LocalConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    ENV = True
    # SQLALCHEMY_DATABASE_URI = "postgresql://flask:flask@localhost:5433/flask"
    BAP_URL = os.getenv("BAP_URL", "http://localhost:9900/protocol/v1")
    MONGO_DATABASE_HOST = "localhost"
    MONGO_DATABASE_PORT = 27017
    MONGO_DATABASE_NAME = "sandbox_bap"
    CLIENT_WEBHOOK_ENDPOINT = os.getenv("CLIENT_WEBHOOK_ENDPOINT",
                                        "https://616e-2409-4042-4d8d-a7b7-c127-cb03-c9c2-ecae.in.ngrok.io/clientApis/response")


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    ENV = True
    # SQLALCHEMY_DATABASE_URI = "postgresql://flask:flask@localhost:5433/flask"
    BAP_URL = os.getenv("BAP_URL", "http://localhost:9900/protocol/v1")
    MONGO_DATABASE_HOST = "localhost"
    MONGO_DATABASE_PORT = 27017
    MONGO_DATABASE_NAME = "sandbox_bap"
    CLIENT_WEBHOOK_ENDPOINT = os.getenv("CLIENT_WEBHOOK_ENDPOINT",
                                        "https://616e-2409-4042-4d8d-a7b7-c127-cb03-c9c2-ecae.in.ngrok.io/clientApis/response")


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    JWT_COOKIE_CSRF_PROTECT = False
    MMI_CLIENT_ID = os.getenv("MMI_CLIENT_ID")
    MMI_CLIENT_SECRET = os.getenv("MMI_CLIENT_SECRET")
    MMI_ADVANCE_API_KEY = os.getenv("MMI_ADVANCE_API_KEY")
    BAP_URL = os.getenv("BAP_URL", "http://localhost:9002/protocol/v1")
    MONGO_DATABASE_HOST = os.getenv("MONGO_DATABASE_HOST", "mongo")
    MONGO_DATABASE_PORT = int(os.getenv("MONGO_DATABASE_PORT", 27017))
    MONGO_DATABASE_NAME = os.getenv("MONGO_DATABASE_NAME", "sandbox_bap")
    CLIENT_WEBHOOK_ENDPOINT = os.getenv("CLIENT_WEBHOOK_ENDPOINT", "http://localhost:3001/clientApis/response")


config_by_name = dict(
    local=LocalConfig,
    dev=DevelopmentConfig,
    prod=ProductionConfig,
)

key = Config.SECRET_KEY


def get_config_by_name(config_name, default=None, env_param_name=None):
    config_env = os.getenv(env_param_name or "ENV")
    config_value = default
    if config_env:
        config_value = getattr(config_by_name[config_env](), config_name, default)
    return config_value


def get_email_config_value_for_name(config_name):
    email_config_value = get_config_by_name("SES") or {}
    config = email_config_value.get(config_name)
    return config


if __name__ == '__main__':
    os.environ["ENV"] = "dev"
    print(get_config_by_name("DOMAIN"))

    os.environ["ENV"] = "prod"
    print(get_email_config_value_for_name("from_email"))
