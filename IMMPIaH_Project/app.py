from flask import Flask, render_template, request, redirect, session, jsonify
import socket
import threading
import json

app = Flask(__name__)
app.secret_key = "secret123"   # 🔐 login security

latest_data = []

# 🔹 SOCKET SERVER
def socket_server():
    HOST = "0.0.0.0"
    PORT = 9999

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)

    print("🟢 Socket Server Running...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()


def handle_client(conn):
    global latest_data

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            data_dict = json.loads(data)

            # store latest 10 records
            latest_data.append(data_dict)
            latest_data = latest_data[-10:]

        except:
            break

    conn.close()


# 🔐 LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect("/")
        else:
            return "<h3 style='color:red'>Invalid Credentials</h3>"

    return render_template("login.html")


# 🔐 LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# 🏠 DASHBOARD (PROTECTED)
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")

    return render_template("index.html", data=latest_data)


# 📊 API FOR CHARTS
@app.route("/data")
def data():
    return jsonify({"patients": latest_data})


# 🚀 MAIN RUN
import os

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    threading.Thread(target=socket_server, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)