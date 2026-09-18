import csv
import functools
import hashlib
import json
import os
import pathlib
import sys
from collections.abc import Callable
from datetime import datetime
from typing import ParamSpec, TypeVar, cast
from zoneinfo import ZoneInfo

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from shared.student import VARIANT_NUMBER

salt = f"{VARIANT_NUMBER!s:0>5s}"

users_to_register = (
    ("risk_manager", "APT@Detect10n"),
    ("business_analyst", "Red@Team2023"),
    ("legal_counsel", "Blue@T3am124"),
    ("contractor_dev", "InfoS3c@2023"),
    ("obsolete_system", "Def3ns3@Key33"),
    ("forensic_lead", "ThreatH@nt3r"),
    ("forensic_analyst", "Incident@R3sp0nse"),
    ("incident_commander", "Cyber@Defense2023"),
    ("retired_expert", "NetworkS3c!99"),
    ("red_team_lead", "Malwar3@Scan"),
    ("", "APT@Detect10n")
)

USER_CSV_DB_PATH = "labs/lab1/data/users.csv"
JSON_LOG_PATH = "labs/lab1/data/log.json"

users_db: dict[str, str] = {}

row = "|{:^30}|{:^130}|"
separator = "—" * 163


class ValidationError(Exception):
    pass


P = ParamSpec("P")
R = TypeVar("R")


def log_event(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        result = func(*args, **kwargs)
        time = datetime.now(tz=ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%d %H:%M:%S")

        username = kwargs.get("username") or (args[0] if args else "Unknown")

        if result:
            text = f"Successful login for {username}"
        else:
            text = f"Failed login for {username}"
        print(text)

        json_log = {
            "event": "login",
            "user": username,
            "result": "success" if result else "failure",
            "timestamp": time,
            "args": list(args),
            "kwargs": kwargs,
        }

        try:
            log_path = pathlib.Path(JSON_LOG_PATH)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            current_logs: list[dict[str, object]] = []
            if log_path.exists() and log_path.stat().st_size > 0:
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        raw_data: object = json.load(f)  # pyright: ignore[reportAny]
                        if isinstance(raw_data, list):
                            current_logs = cast(list[dict[str, object]], raw_data)
                except json.JSONDecodeError:
                    current_logs = []

            current_logs.append(json_log)

            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(current_logs, f, indent=4, ensure_ascii=False)

        except json.JSONDecodeError:
            print("cant read JSON file")

        except (FileNotFoundError, PermissionError, OSError) as err:
            print(f"error while opening file {err}")

        return result

    return wrapper


def generate_hash(password: str, salt: str = "00000") -> str:
    if not password.strip() or not salt.strip():
        raise ValueError("password or salt is empty")

    if len(password) < 12:
        raise ValidationError(
            f"password '{password}' too small, {len(password)} chars when minimal is 12"
        )

    hash = hashlib.blake2b(key=password.encode("utf-8"), salt=salt.encode("utf-8"))
    return hash.hexdigest()


def create_user(username: str, password: str) -> tuple[str, str]:
    if not username.strip() or not password.strip():
        raise ValueError("username or password is empty")
    return (username, generate_hash(password, salt))


def create_users():
    pathlib.Path("labs/lab1/data").mkdir(parents=True, exist_ok=True)

    with open(USER_CSV_DB_PATH, "+w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for user_to_register in users_to_register:
            user = create_user(*user_to_register)
            writer.writerow(user)


@log_event
def login(username: str, password: str) -> bool:
    if not username.strip() or not password.strip():
        raise ValueError("username or password is empty")

    stored_hash = users_db.get(username)
    if stored_hash is None:
        return False

    return stored_hash == generate_hash(password, salt)


def main():
    try:
        create_users()
    except (OSError, FileNotFoundError, PermissionError) as err:
        print(f"error while creating db {err}")
    except (ValidationError, ValueError) as err:
        print(f"error in user data {err}")

    try:
        with open(USER_CSV_DB_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)

            users_db.update(dict(reader))

            print(separator)
            for username, pwd_hash in users_db.items():
                print(row.format(username, pwd_hash))
                print(separator)
    except (OSError, FileNotFoundError, PermissionError) as err:
        print(f"error while opening database {err}")
        return


if __name__ == "__main__":
    main()

    _ = login("risk_manager", "APT@Detect10n")
    _ = login("risk_manager", "WrongPassword123")
    _ = login("ghost_user", "SomeSecurePass123")
