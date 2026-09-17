users = {
    "risk_manager": {
        "role": "risk_analyst",
        "clearance": 4,
        "department": "RiskManagement",
        "active": True,
    },
    "business_analyst": {
        "role": "business_analyst",
        "clearance": 2,
        "department": "Business",
        "active": True,
    },
    "legal_counsel": {
        "role": "legal",
        "clearance": 3,
        "department": "Legal",
        "active": True,
    },
    "contractor_dev": {
        "role": "contractor",
        "clearance": 2,
        "department": "Contract",
        "active": True,
    },
    "obsolete_system": {
        "role": "legacy_system",
        "clearance": 1,
        "department": "Legacy",
        "active": False,
    },
}
resources = [
    ("risk_registers", 4),
    ("business_requirements", 2),
    ("legal_documents", 3),
    ("contract_code", 2),
    ("governance_framework", 4),
    ("meeting_minutes", 1),
    ("regulatory_reports", 3),
    ("executive_dashboards", 4),
    ("project_specs", 2),
    ("public_statements", 1),
]
security_levels = ("Public", "Internal Use", "Restricted", "Highly Restricted")
blocked_users = {"obsolete_system", "contract_expired", "legal_hold"}

row = "|{:^30}|{:^20}|"
check_log = "user={} \nresource={} -> {} {}\n"
separator = "—" * 53


def check_access(username: str, resource: tuple[str, int]):
    if username in blocked_users:
        print(check_log.format(username, resource[0], "DENY", "\n(User is blocked.)"))
        return

    if user := users.get(username, None):
        if not user["active"]:
            print(
                check_log.format(
                    username, resource[0], "DENY", "\n(Account inactive.)"
                )
            )
            return

        if int(user["clearance"]) >= resource[1]:
            print(check_log.format(username, resource[0], "ALLOW", ""))
            return
        else:
            print(
                check_log.format(username, resource[0], "DENY", "\n(User not found.)")
            )
            return
    else:
        print(
            check_log.format(
                username, resource[0], "DENY", "\n(Insufficient clearance)."
            )
        )
        return


def main():
    print(separator)

    for resource in resources:
        name, level = resource
        level = security_levels[level - 1]

        print(row.format(name, level))

    print(separator)
    print("\n")

    for user in users:
        for resource in resources:
            check_access(user, resource)


if __name__ == "__main__":
    main()
