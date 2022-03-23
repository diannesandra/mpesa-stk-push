import requests
import hmac
import hashlib
import json
import string
import random

iPayTransact = "https://apis.ipayafrica.com/payments/v2/transact"
iPayMpesa = "https://apis.ipayafrica.com/payments/v2/transact/push/mpesa"
iPayTransactMobile = "https://apis.ipayafrica.com/payments/v2/transact"
iPayQueryTransaction = "https://apis.ipayafrica.com/payments/v2/transaction/search"
iPayRefund = "https://apis.ipayafrica.com/payments/v2/transaction/refund"
iPayAlgorithm = 'sha256'
iPayKey = "SECretKey"  # use "demoCHANGED" for testing where vid is set to "demo"
iPayVid = "demo"  # Vendor ID
iPaySecret = b"demoCHANGED"


def prepare_stk_data(order_id, amount, customer_phone, customer_email, customer_notifications=0):
    iPayData = {
        "live": 0,
        "oid": order_id,
        "inv": order_id,
        "amount": amount,
        "tel": customer_phone,
        "eml": customer_email,
        "vid": iPayVid,
        "curr": "KES",
        "p1": "YOUR-CUSTOM-PARAMETER",
        "p2": "YOUR-CUSTOM-PARAMETER",
        "p3": "YOUR-CUSTOM-PARAMETER",
        "p4": "YOUR-CUSTOM-PARAMETER",
        "cbk": "https://enktpf6b4e4rm.x.pipedream.net",
        "cst": customer_notifications,
        "crl": 0,
        "autopay": 1
    }
    # The hash digital signature hash of the data for verification.
    hashCode = f"{iPayData['live']}{iPayData['oid']}{iPayData['inv']}{iPayData['amount']}{iPayData['tel']}{iPayData['eml']}{iPayData['vid']}{iPayData['curr']}{iPayData['p1']}{iPayData['p2']}{iPayData['p3']}{iPayData['p4']}{iPayData['cst']}{iPayData['cbk']}"
    h = hmac.new(iPaySecret, bytes(hashCode, 'utf-8'), hashlib.sha256)
    hash = h.hexdigest()
    iPayData["hash"] = hash
    return iPayData

def init_stk(order_id, customer_tel, customer_email, amount, send_receipt=0):
    data = prepare_stk_data(order_id, amount, customer_tel,
                            customer_email, customer_notifications=send_receipt)
    response = requests.post(iPayTransact, headers={
                             "Content-Type": "application/json; "}, data=json.dumps(data))
    response = response.json()
    if response['status'] == 1:
        response['data']['vid'] = data["vid"]
        response['data']['tel'] = customer_tel
        response['data']['email'] = customer_email
    response['data']['status'] = response['status']
    return response['data']


def send_stk(order_id, customer_telephone, customer_email, amount):
    stk_data = init_stk(order_id, customer_telephone, customer_email, amount)
    if stk_data['status'] == 1:
        vid = stk_data['vid']
        sid = stk_data['sid']
        hashCode = f"{customer_telephone}{vid}{sid}"
        h = hmac.new(iPaySecret, bytes(hashCode, 'utf-8'), hashlib.sha256)
        hash = h.hexdigest()
        data = {
            "phone": customer_telephone,
            "vid": vid,
            "sid": sid,
            "hash": hash
        }
        response = requests.post(iPayMpesa, headers={
            "Content-Type": "application/json; "}, data=json.dumps(data))
        response = response.json()
        if response['status'] == 1:
            return (True, "Successfully sent to the client", order_id)
        else:
            return (False, "An error occured ")
    else:
        return (False, "An error occured while initiating request")


def check_transaction(order_id, vid):
    hashCode = f"{order_id}{vid}"
    h = hmac.new(iPaySecret, bytes(hashCode, 'utf-8'), hashlib.sha256)
    hash = h.hexdigest()
    data = {
        "oid": order_id,
        "vid": vid,
        "hash": hash
    }
    response = requests.post(iPayQueryTransaction, headers={
                             "Content-Type": "application/json; "}, data=json.dumps(data))
    response = response.json()
    print(response)
    if response['status'] == 1:
        return (True, response['data'])
    else:
        return (False, "Transaction not found or something went wrong")


if __name__ == "__main__":
    letters = string.ascii_letters
    dummy_order_id = ''.join(random.choice(letters) for i in range(10))
    result = send_stk(dummy_order_id, "254712345678",
                      "email@gmail.com", 10)
    if result[0]:
        print(result[1])
    else:
        print(result[1])
    #check_transaction("dsjknkjsdn", iPayVid)
