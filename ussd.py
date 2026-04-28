from utils import *

# ------------------ GROUPED BUNDLES ------------------

MTN_GROUPS = {
    "1": ("Small", [
        ("1GB","5.1 GHS"),("2GB","10.5 GHS"),("3GB","15 GHS"),
        ("4GB","19 GHS"),("5GB","24 GHS")
    ]),
    "2": ("Medium", [
        ("6GB","28 GHS"),("8GB","38 GHS"),
        ("10GB","44 GHS"),("15GB","65 GHS")
    ]),
    "3": ("Large", [
        ("20GB","83 GHS"),("25GB","104 GHS"),
        ("30GB","125 GHS"),("40GB","163 GHS"),
        ("50GB","203 GHS"),("100GB","395 GHS")
    ])
}

TELECEL_GROUPS = {
    "1": ("Standard", [
        ("5GB","30 GHS"),("10GB","50 GHS"),("15GB","68 GHS")
    ]),
    "2": ("Premium", [
        ("20GB","89 GHS"),("25GB","110 GHS"),("30GB","130 GHS")
    ])
}

AIRTEL_GROUPS = {
    "1": ("Small", [
        ("1GB","5 GHS"),("2GB","10 GHS"),("3GB","15 GHS"),
        ("4GB","20 GHS"),("5GB","25 GHS")
    ]),
    "2": ("Medium", [
        ("6GB","30 GHS"),("7GB","35 GHS"),("8GB","40 GHS"),
        ("10GB","45 GHS"),("12GB","52 GHS")
    ]),
    "3": ("Large", [
        ("15GB","65 GHS"),("20GB","83 GHS"),("25GB","106 GHS")
    ])
}

NETWORKS = {
    "1": ("MTN", MTN_GROUPS),
    "2": ("Telecel", TELECEL_GROUPS),
    "3": ("AirtelTigo", AIRTEL_GROUPS)
}

# ------------------ MAIN FUNCTION ------------------

def process_ussd(text, msisdn):
    parts = text.split("*") if text else []

    # HOME
    if text == "":
        return "CON Welcome to isCheapData\n1. Buy Data\n2. Help Center"

    # HELP
    if text == "2":
        return "END Call or WhatsApp 0558861119 / 0501247889"

    # GLOBAL BACK
    if parts and parts[-1] == "0":
        return "CON Select Network\n1. MTN\n2. Telecel\n3. AirtelTigo"

    # ------------------ BUY FLOW ------------------

    if parts[0] == "1":

        # NETWORK
        if len(parts) == 1:
            return "CON Select Network\n1. MTN\n2. Telecel\n3. AirtelTigo"

        net_key = parts[1]

        if net_key not in NETWORKS:
            return "END Invalid network"

        net_name, groups = NETWORKS[net_key]

        # CATEGORY
        if len(parts) == 2:
            msg = f"CON {net_name} Categories\n"
            for k,(name,_) in groups.items():
                msg += f"{k}. {name}\n"
            return msg + "0. Back"

        group_key = parts[2]

        if group_key not in groups:
            return "END Invalid choice"

        group_name, bundles = groups[group_key]

        # SHOW BUNDLES
        if len(parts) == 3:
            msg = f"CON {net_name} {group_name}\n"
            for i,(d,p) in enumerate(bundles,1):
                msg += f"{i}. {d} - {p}\n"
            return msg + "0. Back"

        # SELECT BUNDLE
        if len(parts) == 4:
            try:
                idx = int(parts[3]) - 1
                bundles[idx]
            except:
                return "END Invalid choice"

            return "CON Buy for:\n1. My Number\n2. Other Number\n0. Back"

        # BUY FOR
        if len(parts) == 5:

            # MY NUMBER
            if parts[4] == "1":
                phone = norm(msisdn)

                if detect(phone) != net_name:
                    return f"CON Your number is {detect(phone)}, not {net_name}\n0. Back"

                return "CON Confirm purchase?\n1. Yes\n2. No\n0. Back"

            # OTHER NUMBER
            if parts[4] == "2":
                return "CON Enter phone number\n0. Back"

        # OTHER NUMBER INPUT + RETRY
        if len(parts) >= 6 and parts[4] == "2" and parts[-1] not in ["1","2"]:

            attempts = len(parts) - 5
            phone = parts[-1]

            if not phone.isdigit() or not valid(phone):
                if attempts >= 3:
                    return "END Too many invalid attempts"
                return "CON Invalid number\nTry again:"

            if detect(phone) != net_name:
                if attempts >= 3:
                    return "END Too many invalid attempts"
                return f"CON Wrong network ({detect(phone)})\nTry again:"

            return "CON Confirm purchase?\n1. Yes\n2. No\n0. Back"

        # CONFIRM
        if (parts[4] == "1" and len(parts) == 6) or (parts[4] == "2" and len(parts) >= 7):

            confirm = parts[-1]

            if confirm == "2":
                return "END Transaction cancelled"

            if confirm == "1":
                try:
                    idx = int(parts[3]) - 1
                    data, price = bundles[idx]
                except:
                    return "END Invalid selection"

                phone = norm(msisdn) if parts[4] == "1" else parts[-2]

                # SAVE ORDER (manual mode for now)
                oid = save(net_name, data, price, phone, "PENDING")

                return (
                    "END Request received.\n"
                    "Processing your data bundle.\n"
                    "Delivery: 15 mins - 2 hours.\n"
                    f"Ref: {oid}"
                )

    return "END Invalid choice"