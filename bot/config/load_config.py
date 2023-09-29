from environs import Env

from .config import (
    Bot,
    Config,
    DatabaseConfig,
    Development,
    IikoCloud,
    Redis,
    SMSCenter,
    SMSCenterSMTP,
)


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        bot=Bot(token=env("BOT_TOKEN"), notify_ids=list(map(int, env.list("NOTIFY_ADMIN_IDS")))),
        database=DatabaseConfig(
            host=env("DATABASE_HOST"),
            port=int(env("DATABASE_PORT")) if env("DATABASE_PORT") else None,
            user=env("DATABASE_USER"),
            password=env("DATABASE_PASSWORD"),
            database=env("DATABASE_NAME"),
            uri=env("DATABASE_URI"),
        ),
        redis=Redis(
            host=env("REDIS_HOST"),
            port=int(env("REDIS_PORT")),
            database=int(env("REDIS_DB")),
            password=env("REDIS_PASSWORD"),
        ),
        iiko_cloud=IikoCloud(
            api_key=env("IIKO_CLOUD_API_KEY"), organizations=list(map(str, env.list("IIKO_CLOUD_ORGANIZATIONS_IDS")))
        ),
        sms_center=SMSCenter(
            login=env("SMSC_LOGIN"),
            password=env("SMSC_PASSWORD"),
            use_post=env.bool("SMSC_POST"),
            ssl=env.bool("SMSC_HTTPS"),
            charset=env("SMSC_CHARSET"),
        ),
        sms_center_smtp=SMSCenterSMTP(
            server=env("SMSC_SMTP_SERVER"),
            login=env("SMSC_SMTP_LOGIN"),
            password=env("SMSC_SMTP_PASSWORD"),
            smtp_from=env("SMSC_SMTP_FROM"),
        ),
        development=Development(
            debug=env.bool("DEBUG"),
            log_type=env("LOG_TYPE"),
            maintenance=env.bool("MAINTENANCE"),
        ),
    )
