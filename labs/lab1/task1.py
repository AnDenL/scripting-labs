import os
import random
import string
import sys
from enum import Enum

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class Safety(Enum):
    Forbidden = 0
    Weak = 1
    Medium = 2
    Strong = 3
    VeryStrong = 4


def safety_to_string(safety: Safety):
    match safety:
        case Safety.Forbidden:
            return "Forbidden"
        case Safety.Weak:
            return "Weak"
        case Safety.Medium:
            return "Medium"
        case Safety.Strong:
            return "Strong"
        case Safety.VeryStrong:
            return "Very strong"


passwords = [
    "APT@Detect10n",
    "simple",
    "Red@Team2023",
    "participant",
    "Blue@T3am",
    "common123",
    "Purple@T34m",
    "regular123",
    "Gr33n@Team",
    "normal123",
]
criteria = {
    "min_length": 7,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}
forbidden_passwords = {
    "simple",
    "participant",
    "common123",
    "regular123",
    "normal123",
    "test",
}


row = "|{:^20}|{:^16}|"
separator = "—" * 39


def main():
    first = random.randrange(0, len(passwords))
    second = random.randrange(0, len(passwords))
    third = random.randrange(0, len(passwords))

    passwords.append(passwords[first])
    passwords.append(passwords[second])
    passwords.append(passwords[third])

    print(separator)
    print(row.format("passwords", "safety"))
    print(separator)

    min_length = criteria["min_length"]
    special_symbols = set(string.punctuation)

    for password in passwords:
        safety = Safety.Forbidden

        if password not in forbidden_passwords and len(password) > min_length:
            criteria_passed = 0

            has_digits = False
            has_upper = False
            has_special = False

            for ch in password:
                has_digits = has_digits or ch.isdigit()
                has_upper = has_upper or ch.isupper()
                has_special = has_special or (ch in special_symbols)

            criteria_passed += has_digits + has_upper + has_special

            match criteria_passed:
                case 1:
                    safety = Safety.Weak
                case 2:
                    safety = Safety.Medium
                case 3:
                    safety = (
                        Safety.VeryStrong
                        if len(password) > min_length + 4
                        else Safety.Strong
                    )
                case _:
                    pass

        print(row.format(password, safety_to_string(safety)))

    print(separator)


if __name__ == "__main__":
    main()
