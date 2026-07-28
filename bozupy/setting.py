import os
import logging
from pathlib import Path

import dotenv

_env_file: Path = Path("~/.env").expanduser().absolute()
if _env_file.exists() and os.environ.get("NO_LOAD_DEFAULT_DOTENV", "false").lower() != "true":
    dotenv.load_dotenv(_env_file, override=True)
_current_env_file: Path = Path(os.getcwd()) / ".env"
if _current_env_file.exists():
    dotenv.load_dotenv(_current_env_file, override=True)
_filepaths: list[Path] = [Path(fp).expanduser().absolute() for fp in os.environ.get("DOT_ENV_FILES", "").split(",") if fp]
for _filepath in _filepaths:
    if _filepath.exists():
        dotenv.load_dotenv(_filepath, override=True)


if os.getenv('LOG_LEVEL'):
    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO').upper(),
        force=True
    )


def _fetch_from_secret_manager(secret_id: str) -> str:
    import boto3
    return boto3.Session(
        profile_name=os.environ.get("AWS_SECRET_PROFILE", os.environ.get("AWS_PROFILE")),
        region_name=os.environ.get("AWS_SECRET_REGION_NAME", os.environ.get("AWS_REGION_NAME", "ap-northeast-1"))
    ).client(
        service_name='secretsmanager',
    ).get_secret_value(SecretId=secret_id)["SecretString"]


def _fetch_from_1password(secret_reference: str) -> str:
    import shutil
    import subprocess
    if not secret_reference.startswith("op://"):
        secret_reference = "op://" + secret_reference.lstrip("/")
    op_command: str | None = shutil.which(os.environ.get("OP_COMMAND", "op"))
    if op_command is None:
        raise RuntimeError("1Password CLI (op) is not found. Install it to use the 'op:' prefix.")
    command: list[str] = [op_command, "read", "--no-newline"]
    if os.environ.get("OP_ACCOUNT"):
        command += ["--account", os.environ["OP_ACCOUNT"]]
    command.append(secret_reference)
    try:
        completed: subprocess.CompletedProcess[str] = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to read a secret from 1Password: {e.stderr.strip()}") from e
    return completed.stdout.strip()


def _resolve_secret(value: str) -> str:
    if value.startswith("aws:"):
        return _fetch_from_secret_manager(value[len("aws:"):].strip())
    if value.startswith("op:"):
        return _fetch_from_1password(value[len("op:"):].strip())
    return value


BOZUPY_VERSION: str = "0.5.0"

logging.debug(f"BOZUPY_VERSION: {BOZUPY_VERSION}")
USER_AGENT: str = os.environ.get("USER_AGENT", f"bozupy:v{BOZUPY_VERSION}")
DEFAULT_CYBOZU_SUBDOMAIN: str = os.environ.get("CYBOZU_SUBDOMAIN", "")
DEFAULT_CYBOZU_USERNAME: str = os.environ.get("CYBOZU_USERNAME", "")
DEFAULT_CYBOZU_PASSWORD: str = _resolve_secret(os.environ.get("CYBOZU_PASSWORD", ""))

_is_dev_domain: bool = os.environ.get("CYBOZU_IS_DEV_DOMAIN", "false").lower() == "true"
DEFAULT_OTP_SECRET: str = os.environ.get("CYBOZU_OTP_SECRET", "")
DEFAULT_CYBOZU_REGION: str = os.environ.get("CYBOZU_REGION", "jp").lower()
DEFAULT_HOST: str = DEFAULT_CYBOZU_SUBDOMAIN + "." + ("cybozu-dev" if _is_dev_domain else "cybozu") + ".com"

DEFAULT_APP_TOKENS: dict[int, str] = {}
for key, value in os.environ.items():
    if key.startswith("KINTONE_APP_TOKEN_"):
        try:
            app_id: int = int(key.split("_")[3])
        except ValueError:
            logging.warning(f"Invalid app_id: {key}")
            continue
        DEFAULT_APP_TOKENS[app_id] = _resolve_secret(value)
        logging.debug(f"App token for app_id {app_id} is set")
