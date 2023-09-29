from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    uri: str
    database: str
    port: int | None = None
    password: str = None
    user: str = "root"
    host: str = "localhost"


@dataclass
class Bot:
    token: str
    notify_ids: list[int]


@dataclass
class IikoCloud:
    api_key: str
    organizations: list[str]


@dataclass
class SMSCenter:
    login: str
    password: str
    use_post: bool = False
    ssl: bool = False
    charset: str = "utf8"


@dataclass
class SMSCenterSMTP:
    server: str = None
    login: str = None
    password: str = None
    smtp_from: str = None


@dataclass
class Redis:
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: str = None


@dataclass
class Development:
    debug: bool = False
    log_type: str = "console"
    maintenance: bool = False


@dataclass
class Config:
    database: DatabaseConfig
    bot: Bot
    iiko_cloud: IikoCloud
    sms_center: SMSCenter
    sms_center_smtp: SMSCenterSMTP
    redis: Redis
    development: Development
