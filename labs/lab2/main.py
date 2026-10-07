import sys

from .task1 import *


def demo() -> None:
    print("\n--- User creation ---")
    account = UserAccount(
        User("Gorobeus", "gorobeus56@gmail.com", "Larp1006W", "tester", True)
    )
    print(f"Created: \n{account}")

    print("\n--- Login fail ---")
    account.login("Libertartarianposadist", "dirtyhair1337", "192.168.1.100")
    print(f"User authenticated: {account.is_authenticated()}")

    print("\n--- Login success ---")
    account.login("Gorobeus", "Larp1006W", "192.168.1.100")
    print(f"User authenticated: {account.is_authenticated()}")

    print("\n--- Email сhange ---")
    try:
        account["email"] = "dirtyhair1337@gmail.com"
        print(f"Email changed to: {account['email']}")

        print("Trying to set an invalid email:")
        account["email"] = "hello_world(print)"
    except ValueError as e:
        print(f"Error: {e}")

    print("\n--- Admin ---")
    admin_account = UserAccount(
        Admin(
            "AnDenL", "andenlbd@gmail.com", "gfG6k5kvKCHn", "admin", True, {"read_logs"}
        )
    )
    admin_account["permissions"] = {"read_logs", "ban_users"}
    print(f"New permissions: {admin_account['permissions']}")

    print("\n--- Timeout ---")
    print("Changing last_activity time...")
    if account.session:
        account.session.last_activity = datetime.now(timezone.utc) - timedelta(
            seconds=SESSION_TIMEOUT_SEC + 1
        )
    print(f"User authenticated: {account.is_authenticated()}")

    print("\n--- Logout ---")
    account.login("Gorobeus", "Larp1006W", "192.168.1.100")
    print(f"Logged into account: {account.is_authenticated()}")
    account.logout()
    print(f"Logout: {account.is_authenticated()}")

    print("\n--- Logs ---")
    # тип через __getitem__ не відомий
    print("\n".join(account["logs"]))  # pyright: ignore[reportCallIssue, reportArgumentType]


def main() -> None:
    if "demo" in sys.argv:
        demo()


if __name__ == "__main__":
    main()
