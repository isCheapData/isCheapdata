import requests
import datetime, uuid, json, os

API_KEY = "260428113113-boznFZ-MUZ1Cy-AzCcDo-A15zhC-4JyAWd"
ORDERS_FILE = "orders.json"


# ======================
# API FUNCTION
# ======================
def send_data(phone, package):
    url = "https://dataworksgh.com/agent/wallet_mtn_pay.php"

    payload = {
        "network": "MTN",
        "package": str(package),
        "beneficiary": phone,
        "beneficiary_repeat": phone
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        res = requests.post(url, data=payload, headers=headers, timeout=30)

        print("STATUS:", res.status_code)
        print("RAW:", res.text)

        return {"code": res.status_code, "response": res.text}

    except Exception as e:
        return {"code": 500, "message": str(e)}


# ======================
# HELPERS
# ======================
def gen_id():
    return "ORD" + uuid.uuid4().hex[:6].upper()


def norm(p):
    p = p.strip()

    if p.startswith("+233"):
        p = "0" + p[4:]
    elif p.startswith("233"):
        p = "0" + p[3:]

    return p


# REAL GHANA PREFIXES
MTN_PREFIXES = ["024", "025", "053", "054", "055", "059"]
TELECEL_PREFIXES = ["020", "050"]
AIRTEL_PREFIXES = ["026", "027", "056", "057"]


def valid(p):
    p = norm(p)

    if not p.isdigit():
        return False

    if len(p) != 10:
        return False

    if not p.startswith("0"):
        return False

    prefix = p[:3]

    if prefix in MTN_PREFIXES + TELECEL_PREFIXES + AIRTEL_PREFIXES:
        return True

    return False


def detect(p):
    p = norm(p)
    prefix = p[:3]

    if prefix in MTN_PREFIXES:
        return "MTN"

    if prefix in TELECEL_PREFIXES:
        return "Telecel"

    if prefix in AIRTEL_PREFIXES:
        return "AirtelTigo"

    return "Unknown"


# ======================
# ORDER STORAGE
# ======================
def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []

    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_all_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=4)


def save(network, bundle, price, phone, status):
    orders = load_orders()

    oid = gen_id()
    t = datetime.datetime.now().isoformat()

    new_order = {
        "id": oid,
        "network": network,
        "bundle": bundle,
        "price": price,
        "phone": phone,
        "status": status,
        "time": t
    }

    orders.append(new_order)
    save_all_orders(orders)

    return oid


# ======================
# MAIN PROCESS FUNCTION
# ======================
def process_order(phone, gig, bundle_name, price):
    phone = norm(phone)

    if not valid(phone):
        return {"status": "error", "message": "Invalid phone number"}

    network = detect(phone)

    response = send_data(phone, gig)

    status = "SUCCESS" if response.get("code") == 200 else "FAILED"

    order_id = save(network, bundle_name, price, phone, status)

    return {
        "order_id": order_id,
        "network": network,
        "phone": phone,
        "bundle": bundle_name,
        "status": status,
        "api_response": response
    }
