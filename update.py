from logging import (
    FileHandler,
    StreamHandler,
    INFO,
    basicConfig,
    error as log_error,
    info as log_info,
)
from os import path as ospath, environ, remove
from subprocess import run as srun, call as scall
from importlib.metadata import distributions
from dotenv import load_dotenv, dotenv_values
from pymongo import MongoClient

if ospath.exists("log.txt"):
    with open("log.txt", "r+") as f:
        f.truncate(0)

if ospath.exists("rlog.txt"):
    remove("rlog.txt")

basicConfig(
    format="[%(asctime)s] [%(levelname)s] - %(message)s",
    datefmt="%d-%b-%y %I:%M:%S %p",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

load_dotenv("config_sample.env", override=True)

BOT_TOKEN = environ.get("BOT_TOKEN", "")
if len(BOT_TOKEN) == 0:
    log_error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

bot_id = BOT_TOKEN.split(":", 1)[0]

DATABASE_URL = environ.get("DATABASE_URL", "")
if len(DATABASE_URL) == 0:
    DATABASE_URL = None

if DATABASE_URL is not None:
    conn = MongoClient(DATABASE_URL)
    db = conn.wzmlx
    old_config = db.settings.deployConfig.find_one({"_id": bot_id})
    config_dict = db.settings.config.find_one({"_id": bot_id})
    if old_config is not None:
        del old_config["_id"]
    if (
        old_config is not None
        and old_config == dict(dotenv_values("config_sample.env"))
        or old_config is None
    ) and config_dict is not None:
        environ["UPSTREAM_REPO"] = config_dict.get("UPSTREAM_REPO", "")
        environ["UPSTREAM_BRANCH"] = config_dict.get("UPSTREAM_BRANCH", "")
        environ["UPGRADE_PACKAGES"] = config_dict.get("UPDATE_PACKAGES", "False")
    conn.close()

UPGRADE_PACKAGES = environ.get("UPGRADE_PACKAGES", "False")
if UPGRADE_PACKAGES.lower() == "true":
    packages = [dist.metadata["Name"] for dist in distributions()]
    scall("uv pip install --system " + " ".join(packages), shell=True)

UPSTREAM_REPO = ""
UPSTREAM_BRANCH = "master"

if ospath.exists(".git"):
    srun(["rm", "-rf", ".git"])

log_info("Application Environment Configured Successfully !!")
log_info("UPSTREAM_REPO: Disguised | UPSTREAM_BRANCH: Protected")
