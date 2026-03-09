import ipaddress
import subprocess
from flask import Flask, jsonify, request


app = Flask(__name__)

def nmap_scan(ip, port=None):

    suspicious_symbols = ["$" , "\"", "\'", "\\", "@", ",", "*", "&", "|", "{", "}"]
    suspicious_commands = ["flag", "txt", "cat", "echo", "head", "tail", "more", "less", "sed", "awk", "dd", "env", "printenv", "set"]

    sus = suspicious_commands + suspicious_symbols

    if any(cmd in ip.lower() for cmd in sus):
        return { "success": False, "error": "Suspicious input detected: " }

    try:
        if port:
            command = f"nmap -sV -p {str(port)} {ip}"
            description = f"Port {port} scan with service detection"
        else:
            command = f"nmap -F -sV {ip}"
            description = "Quick port scan with service detection"

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout
        host_up = "Host is up" in output or "up" in output.lower()
        if ("{" in output):
            return { "success": False, "error": "Suspicious output detected" }

        return {
            "success": True,
            "host": ip,
            "port": port,
            "reachable": host_up,
            "scan_results": output,
            "description": description
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Scan took too long"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "Nmap is not installed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Scan failed: {str(e)}"
        }

@app.get("/check")
def checkIp():
    ip = request.args.get("ip")
    port = request.args.get("port")

    if not ip:
        return jsonify({"error": "IP address is required"}), 400

    try:
        # verify if you have an actual real ip and not some garbage
        ipaddress.ip_address(ip)
    except ValueError:
        return jsonify({"error": "Invalid IP address"}), 400

    if port:
        try:
            port_int = int(port)
            if not (1 <= port_int <= 65535):
                return jsonify({"success": False, "error": "Port must be between 1 and 65535"}), 400
        except ValueError:
            return jsonify({"success": False, "error": "Port must be a number"}), 400

    result = nmap_scan(ip, port)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
