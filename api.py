from flask import Flask, jsonify, request
from ipay import check_transaction, send_stk, iPayVid
import string
import random
import re

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello_world():
    return 'API SUCCESS'


@app.route('/send_stk', methods=['POST'])
def initiate_payment():

    content = request.get_json()
    phone = content['phone']
    email = content['email']
    amount = content['amount']

    letters = string.ascii_letters
    dummy_order_id = ''.join(random.choice(letters) for i in range(10))
    phone_number = re.match(
        r'2547[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', phone)
    if phone_number:
        if int(amount) >= 10:
            result = send_stk(
                dummy_order_id, phone_number.string, email, amount)
            if result[0] == 1:
                print(phone_number.string, dummy_order_id, amount)
                return jsonify({"success": True, "message": f"{result[1]} with Order ID: {result[2]}"})
            else:
                return jsonify({"success": False, "message": result[1]})
        else:
            return jsonify({"success": False, "message": "The amount must be at least 10KES"})


@app.route('/check', methods=['POST'])
def verify_payment():
    content = request.get_json()
    order_id = content['order_id']
    result = check_transaction(order_id, iPayVid)
    if result[0] == 1:
        return jsonify({"success": True, "message": result[1]})
    else:
        return jsonify({"success": False, "message": result[1]})




if __name__ == '__main__':
    app.run(debug=True)
