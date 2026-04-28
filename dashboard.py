from flask import session, redirect, request, Response
from utils import *
import datetime, csv, io

# 🔐 LOGIN PAGE
def login_page(error=""):
    return f"""
    <html>
    <head>
    <title>Admin Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body style="background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);">

    <div class="container d-flex justify-content-center align-items-center" style="height:100vh;">
        <div class="card p-4 shadow" style="width:350px;border-radius:15px;">
            <h3 class="text-center mb-3">🔐 Admin Login</h3>

            {"<div class='alert alert-danger'>"+error+"</div>" if error else ""}

            <form method="post">
                <input name="username" class="form-control mb-3" placeholder="Username" required>
                <input type="password" name="password" class="form-control mb-3" placeholder="Password" required>
                <button class="btn btn-dark w-100">Login</button>
            </form>
        </div>
    </div>

    </body>
    </html>
    """

def login_handler(req):
    if req.method == "POST":
        if req.form.get("username") == "admin" and req.form.get("password") == "1234":
            session["admin"] = True
            return redirect("/admin")
        return login_page("Invalid login")
    return login_page()

def logout():
    session.clear()
    return redirect("/login")

# 📤 EXPORT CSV
def export_orders():
    orders = load_orders()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID","Network","Bundle","Price","Phone","Status","Time"])

    for o in orders:
        writer.writerow([o["id"],o["network"],o["bundle"],o["price"],o["phone"],o["status"],o["time"]])

    output.seek(0)

    return Response(output, mimetype="text/csv",
        headers={"Content-Disposition":"attachment;filename=orders.csv"})

# ✅ NEW: UPDATE STATUS (FIXES YOUR ERROR)
def update_status(req):
    if not session.get("admin"):
        return redirect("/login")

    oid = req.args.get("id")
    status = req.args.get("status")

    orders = load_orders()

    for o in orders:
        if o["id"] == oid:
            o["status"] = status

    save_all_orders(orders)

    return redirect("/admin")

# 📊 DASHBOARD
def admin_view(req):
    if not session.get("admin"):
        return redirect("/login")

    q = req.args.get("q","").lower()
    data = load_orders()

    if q:
        data = [o for o in data if q in o["id"].lower() or q in o["phone"]]

    # DAILY
    today = datetime.datetime.now().date()

    def price_to_float(p):
        try: return float(p.split()[0])
        except: return 0

    today_orders = [o for o in data if datetime.datetime.fromisoformat(o["time"]).date()==today]

    today_count = len(today_orders)
    today_revenue = sum(price_to_float(o["price"]) for o in today_orders)

    # CHART DATA
    mtn = sum(1 for o in data if o["network"]=="MTN")
    telecel = sum(1 for o in data if o["network"]=="Telecel")
    airtel = sum(1 for o in data if o["network"]=="AirtelTigo")

    pending = sum(1 for o in data if o["status"]=="PENDING")
    completed = sum(1 for o in data if o["status"]=="COMPLETED")

    count = len(data)

    html = f"""
    <html>
    <head>
    <title>Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>

    <body class="bg-light p-4">

    <!-- 🔔 SOUND -->
    <audio id="notify">
        <source src="https://www.soundjay.com/buttons/sounds/button-3.mp3">
    </audio>

    <div class="container">

    <div class="d-flex justify-content-between mb-4">
        <h2>📊 Dashboard</h2>
        <div>
            <a href="/export" class="btn btn-success">Export</a>
            <a href="/logout" class="btn btn-danger">Logout</a>
        </div>
    </div>

    <!-- SEARCH -->
    <form class="row mb-3">
        <div class="col-md-6">
            <input name="q" class="form-control" placeholder="Search ID or phone" value="{q}">
        </div>
        <div class="col-md-2">
            <button class="btn btn-dark w-100">Search</button>
        </div>
    </form>

    <!-- DAILY -->
    <div class="row mb-4">
        <div class="col-md-6">
            <div class="alert alert-info">
                Today's Orders: {today_count}
            </div>
        </div>

        <div class="col-md-6">
            <div class="alert alert-success">
                Today's Revenue: GHS {today_revenue:.2f}
            </div>
        </div>
    </div>

    <!-- TABLE -->
    <table class="table table-bordered table-hover">
    <thead class="table-dark">
    <tr>
    <th>ID</th><th>Network</th><th>Bundle</th><th>Phone</th><th>Status</th><th>Time</th><th>Action</th>
    </tr>
    </thead>
    <tbody>
    """

    for o in reversed(data):

        color = {
            "PENDING": "warning",
            "PROCESSING": "info",
            "COMPLETED": "success",
            "FAILED": "danger"
        }.get(o["status"], "secondary")

        html += f"""
        <tr>
        <td>{o['id']}</td>
        <td>{o['network']}</td>
        <td>{o['bundle']}</td>

        <td>
            {o['phone']}
            <button onclick="navigator.clipboard.writeText('{o['phone']}')" class="btn btn-sm btn-outline-dark">📋</button>
        </td>

        <td><span class="badge bg-{color}">{o['status']}</span></td>
        <td>{o['time']}</td>

        <td>
            <a href="/update?id={o['id']}&status=PROCESSING" class="btn btn-sm btn-primary">Process</a>
            <a href="/update?id={o['id']}&status=COMPLETED" class="btn btn-sm btn-success">Done</a>
            <a href="/update?id={o['id']}&status=FAILED" class="btn btn-sm btn-danger">Fail</a>
        </td>
        </tr>
        """

    html += f"""
    </tbody></table>

    </div>

    <script>
    let oldCount = localStorage.getItem("order_count") || 0;
    let newCount = {count};

    if (newCount > oldCount) {{
        document.getElementById("notify").play();
    }}

    localStorage.setItem("order_count", newCount);

    setTimeout(() => location.reload(), 5000);
    </script>

    </body>
    </html>
    """

    return html