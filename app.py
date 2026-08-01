from flask import Flask, request, jsonify, Response
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# 🔥 MULTI WAREHOUSE CONFIG
ACCOUNTS = {
    "RATAN WH": {
        "cred": "billdesk@swissmilitaryindia.com",
        "password": "Emiza@123",
        "seller_id": "80000493",
        "warehouse_id": "600071"
    },

    "ACT B2B WH": {
        "cred": "act@swissmilitaryindia.com",
        "password": "Swiss@123",
        "seller_id": "80000332",
        "warehouse_id": "600040"
    },

    "Nelamangala": {
        "cred": "sanjay.mahto@swissmilitaryindia.com",
        "password": "Emiza@123",
        "seller_id": "80000476",
        "warehouse_id": "600049",
        "user_id": "300000000850"
    }

}

# ✅ HOME
@app.route("/")
def home():
    return "Inventory + Sales Order Server Running 🚀"


# 🔥 INVENTORY DOWNLOAD API
@app.route("/get-inventory", methods=["GET"])
def get_inventory():

    try:

        warehouse = request.args.get("warehouse")

        account = ACCOUNTS.get(warehouse)

        if not account:
            return jsonify({
                "status": "FAILED",
                "message": "Invalid warehouse"
            })

        # -----------------------
        # 🔐 LOGIN
        # -----------------------

        login_url = "https://edge-service.emizainc.com/identity-service/user/login"

        login_payload = {
            "cred": account["cred"],
            "password": account["password"],
            "user_type": "SELLERS",
            "is_otp_login": False
        }

        login_headers = {
            "content-type": "application/json",
            "x-device-id": "armaze-web"
        }

        login_res = requests.post(
            login_url,
            json=login_payload,
            headers=login_headers
        )

        pim_sid = login_res.headers.get("pim-sid")

        if not pim_sid:
            return jsonify({
                "status": "FAILED",
                "message": "Login failed"
            })

        # -----------------------
        # 📦 INVENTORY CSV API
        # -----------------------

        inventory_url = (
            f"https://edge-service.emizainc.com/"
            f"inventory-service/api/v1/inventory/report/seller/csv?"
            f"report_type=inventory_report"
            f"&filter=created_at"
            f"&seller_id={account['seller_id']}"
            f"&warehouseId={account['warehouse_id']}"
        )

        headers = {
            "pim-sid": pim_sid,
            "x-device-id": "armaze-web",
            "x-seller-id": account["seller_id"],
            "x-tenant-id": "1",
            "x-user-id": "300000000850",
            "x-warehouse-id": account["warehouse_id"]
        }

        res = requests.get(inventory_url, headers=headers)

        return Response(
            res.text,
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                "attachment; filename=inventory.csv"
            }
        )

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "message": str(e)
        })


# 🔥 SALES ORDER DOWNLOAD API
@app.route("/get-sales-orders", methods=["GET"])
def get_sales_orders():

    try:

        warehouse = request.args.get("warehouse")

        # default = last 3 days
        days = int(request.args.get("days", 3))

        account = ACCOUNTS.get(warehouse)

        if not account:
            return jsonify({
                "status": "FAILED",
                "message": "Invalid warehouse"
            })

        # -----------------------
        # 🔐 LOGIN
        # -----------------------

        login_url = "https://edge-service.emizainc.com/identity-service/user/login"

        login_payload = {
            "cred": account["cred"],
            "password": account["password"],
            "user_type": "SELLERS",
            "is_otp_login": False
        }

        login_headers = {
            "content-type": "application/json",
            "x-device-id": "armaze-web"
        }

        login_res = requests.post(
            login_url,
            json=login_payload,
            headers=login_headers
        )

        pim_sid = login_res.headers.get("pim-sid")

        if not pim_sid:
            return jsonify({
                "status": "FAILED",
                "message": "Login failed"
            })

        # -----------------------
        # 📅 DATE RANGE
        # -----------------------

        today = datetime.today()

        from_date = (
            today - timedelta(days=days)
        ).strftime("%Y-%m-%d")

        to_date = today.strftime("%Y-%m-%d")

        # -----------------------
        # 📦 SALES ORDER CSV API
        # -----------------------

        sales_url = (
            f"https://edge-service.emizainc.com/"
            f"warehouse-order-processing-service/api/v1/"
            f"warehouse/order/report/csv?"
            f"seller_id={account['seller_id']}"
            f"&generated_by=Automation"
            f"&userName=Automation"
            f"&from={from_date}"
            f"&to={to_date}"
            f"&reportType=sale_order_report"
            f"&filter=created_at"
            f"&warehouseId={account['warehouse_id']}"
            f"&version=v1"
        )

        headers = {
            "pim-sid": pim_sid,
            "x-device-id": "armaze-web",
            "x-seller-id": account["seller_id"],
            "x-tenant-id": "1",
            "x-warehouse-id": account["warehouse_id"]
        }

        res = requests.get(sales_url, headers=headers)

        return Response(
            res.text,
            mimetype="text/csv",
            headers={
                "Content-Disposition":
                "attachment; filename=sales_orders.csv"
            }
        )

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "message": str(e)
        })


# 🔥 RUN SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
