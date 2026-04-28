from flask import Flask, request
from ussd import process_ussd
from dashboard import admin_view, login_handler, logout, export_orders, update_status

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route('/ussd', methods=['POST'])
def ussd():
    return process_ussd(
        request.form.get("text",""),
        request.form.get("phoneNumber","")
    )

@app.route('/login', methods=['GET','POST'])
def login():
    return login_handler(request)

@app.route('/admin')
def admin():
    return admin_view(request)

@app.route('/logout')
def logout_route():
    return logout()

@app.route('/export')
def export():
    return export_orders()

@app.route('/update')
def update():
    return update_status(request)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
