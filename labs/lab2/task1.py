import hashlib
import hmac
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum

SALT_SIZE = 5
ITERRATIONS = 300_000


class User:
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{2,63}@[a-zA-Z]+\.[a-zA-Z]{2,}$")

    username: str
    _email: str
    role: str
    active: bool

    __password_hash: bytes
    __password_salt: bytes

    def __init__(
        self, username: str, email: str, password: str, role: str, active: bool
    ) -> None:
        self.username = username
        self.email = email
        self.role = role
        self.active = active

        self.__password_hash = b""
        self.__password_salt = b""
        self.set_password(password)

    def __str__(self) -> str:
        return f"Username: {self.username}\nEmail: {self.email}\nRole: {self.role}\nActive: {self.active}"

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not self.EMAIL_PATTERN.match(value):
            raise ValueError(f"invalid email format: {value}")

        self._email = value

    def set_password(self, password: str) -> None:
        if not isinstance(password, str) or not password:
            raise ValueError("password can't be empty")

        self.__password_salt = os.urandom(SALT_SIZE)
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, ITERRATIONS
        )

    def check_password(self, password: str) -> bool:
        if not self.active:
            return False
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.__password_salt, ITERRATIONS
        )
        return hmac.compare_digest(password_hash, self.__password_hash)

    def deactivate(self) -> None:
        self.active = False


class Admin(User):
    permissions: set[str]

    def __init__(
        self,
        uname: str,
        mail: str,
        password: str,
        role: str,
        active: bool,
        permissions: set[str],
    ) -> None:
        super().__init__(uname, mail, password, role, active)
        self.permissions = set(permissions)

    def grant_permission(self, permission: str) -> None:
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        self.permissions.remove(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self) -> str:
        return f"Admin\n{super().__str__()}\nPermissions: {self.permissions}"


SESSION_TIMEOUT_SEC = 900


class Session:
    ip: str
    login_time: datetime
    last_activity: datetime

    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.login_time = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("timeout can't be empty")
        return datetime.now(timezone.utc) - self.last_activity <= timedelta(
            seconds=timeout_sec
        )


class Action(Enum):
    LoginSuccess = "Succesful login"
    LoginFailure = "Failed login"
    Logout = "Logout"


@dataclass
class Log:
    username: str
    action: Action
    time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        return (
            f"{self.time.isoformat()} Username: {self.username} Action: {self.action}"
        )


class AuditLog:
    entries: list[Log]

    def __init__(self) -> None:
        self.entries = []

    def append(self, username: str, action: Action) -> None:
        self.entries.append(Log(username, action))


class UserAccount:
    user: User
    session: Session | None
    logs: AuditLog

    def __init__(self, user: User) -> None:
        self.user = user
        self.session = None
        self.logs = AuditLog()

    def login(self, username: str, password: str, ip: str) -> None:
        action = (
            Action.LoginSuccess
            if username == self.user.username
            and self.user.check_password(password)
            and not self.is_authenticated()
            else Action.LoginFailure
        )

        if action == Action.LoginSuccess:
            self.session = Session(ip)
            self.session.touch()

        self.logs.append(username, action)

    def is_authenticated(self) -> bool:
        if self.session is None:
            return False
        return self.session.is_active(SESSION_TIMEOUT_SEC)

    def logout(self) -> None:
        self.session = None
        self.logs.append(self.user.username, Action.Logout)

    def __str__(self) -> str:
        return str(self.user)

    def __getitem__(self, index):
        match index.lower():
            case "username":
                return self.user.username
            case "email":
                return self.user.email
            case "active":
                return self.user.active
            case "role":
                return self.user.role
            case "permissions":
                if isinstance(self.user, Admin):
                    return self.user.permissions
                raise TypeError("user is not admin")
            case "ip":
                if self.session:
                    return self.session.ip
                return None
            case "login_time":
                if self.session:
                    return self.session.login_time
                return None
            case "last_activity":
                if self.session:
                    return self.session.last_activity
                return None
            case "logs":
                return list(map(str, self.logs.entries))
            case _:
                raise KeyError("key doesn't exists")

    def __setitem__(self, index, value: object) -> None:
        match index.lower():
            case "username":
                if not isinstance(value, str):
                    raise TypeError
                self.user.username = value
            case "email":
                if not isinstance(value, str):
                    raise TypeError(
                        f"expected str for email got {type(value).__name__}"
                    )
                self.user.email = value
            case "active":
                if not isinstance(value, bool):
                    raise TypeError(
                        f"expected bool for active got {type(value).__name__}"
                    )
                self.user.active = value
            case "role":
                if not isinstance(value, str):
                    raise TypeError(f"expected str for role got {type(value).__name__}")
                self.user.role = value
            case "permissions":
                if not isinstance(self.user, Admin):
                    raise TypeError("user is not admin")

                if not isinstance(value, (set, list, tuple)):
                    raise TypeError(
                        f"expected a collection of permissions got {type(value).__name__}"
                    )

                if not all(isinstance(item, str) for item in value):
                    raise TypeError(
                        f"collection contains non str value: {type(value).__name__}"
                    )

                self.user.permissions = set(value)
            case "ip":
                if not self.session:
                    raise KeyError("session isn't initialized yet")

                if not isinstance(value, str):
                    raise TypeError(f"expected str for ip got {type(value).__name__}")

                self.session.ip = value
            case "login_time":
                raise KeyError("can't change login time")
            case "last_activity":
                raise KeyError("can't change last activity")
            case "logs":
                raise KeyError("can't change logs")
            case _:
                raise KeyError("key doesn't exists")
