from flask import Flask, render_template, request, redirect, flash
import subprocess
import ipaddress

app = Flask(__name__)
app.secret_key = "change_this_secret"


def run_cmd(cmd):
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr


def valid_ip(ip):
    try:
        ipaddress.ip_network(ip, strict=False)
        return True
    except ValueError:
        return False


@app.route("/")
def index():
    rules = run_cmd(["iptables", "-L", "INPUT", "-n", "--line-numbers"])
    return render_template("index.html", rules=rules)


@app.route("/allow", methods=["POST"])
def allow():
    ip = request.form["ip"].strip()

    if not valid_ip(ip):
        flash("Invalid IP or CIDR.")
        return redirect("/")

    run_cmd([
        "iptables",
        "-A",
        "INPUT",
        "-s",
        ip,
        "-j",
        "ACCEPT"
    ])

    flash(f"Allowed {ip}")
    return redirect("/")


@app.route("/block", methods=["POST"])
def block():
    ip = request.form["ip"].strip()

    if not valid_ip(ip):
        flash("Invalid IP or CIDR.")
        return redirect("/")

    run_cmd([
        "iptables",
        "-A",
        "INPUT",
        "-s",
        ip,
        "-j",
        "DROP"
    ])

    flash(f"Blocked {ip}")
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    rule = request.form["rule"].strip()

    if not rule.isdigit():
        flash("Rule number must be numeric.")
        return redirect("/")

    run_cmd([
        "iptables",
        "-D",
        "INPUT",
        rule
    ])

    flash(f"Deleted rule {rule}")
    return redirect("/")


@app.route("/flush", methods=["POST"])
def flush():
    run_cmd([
        "iptables",
        "-F",
        "INPUT"
    ])

    flash("All INPUT rules removed.")
    return redirect("/")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
