import uhashlib
import ujson as json
import os
from ed25519_pico import create_solana_wallet,solana_sign_transaction
import sys
import utime
WALLET_FILE="wallet.dat"

def hash(text):
    hash_object = uhashlib.sha256(text.encode('utf-8'))
    hex_digest = hash_object.digest()
    hex_digest_str = "".join("{:02x}".format(b) for b in hex_digest)
    return hex_digest_str

def hex_bytes(hex):
    return bytes.fromhex(hex)

def generate_privatekey():
    return os.urandom(32).hex()

def xor_encrypt(msg,k):
    key=hex_bytes(k)
    message=hex_bytes(msg)
    result = bytes([message[i]^key[i%len(key)] for i in range(len(message))])
    return result.hex()

def xor_decrypt(msg,k):
    key=hex_bytes(k)
    message=hex_bytes(msg)
    result = bytes([message[i]^key[i%len(key)] for i in range(len(message))])
    return result.hex()

def create_wallet(name,password,password2):
    data=read_file()
    if data=="None" or not data:
        walletname=str(name)
        walletpasswd=str(password)
        walletpasswd2=str(password2)
        if walletpasswd==walletpasswd2:
            print("generating key please wait")
            sys.stdout.write("gen_key\n")
            
            # ✅ ADD BREATHING ROOM - LET PICO PROCESS
            for i in range(10):
                print(f"Step {i+1}/10...")
                utime.sleep(6)  # 60 seconds total but with breathing
                
            private_key,public_key=create_solana_wallet()
            
            print("done generating")
            sys.stdout.write("done_gen\n")
            
            with open(WALLET_FILE, "w") as file:
                wallet_data={
                    "name":walletname,
                    "passhash":str(hash(walletpasswd)),
                    "privatekey": xor_encrypt(private_key,str(hash(walletpasswd))),
                    "publickey":public_key
                }
                w=json.dumps(wallet_data)
                file.write(str(w))
                
            sys.stdout.write("created\n")
            return "created"
        else:
            return("different password please try again")
    else:
        return("walletexist")

def delete_wallet(password):
    data=read_file()
    if not data or data=="None":
        return None
    
    with open(WALLET_FILE, "r") as file:
        data=file.read()
    data=json.loads(data)
    hashed=hash(str(password))

    if (hashed==data["passhash"])==True:
        with open(WALLET_FILE, "w") as file:
            file.write("None")
        return 0
    else:
        return "wrongpass"
    
def read_file():
    with open(WALLET_FILE,"r") as file:
        data=file.read()
    data=data.strip()
    return data

def get_private_key(password):
    data=read_file()
    if not data or data=="None":
        return None
    data=json.loads(data)
    hashed=hash(str(password))

    if (hashed==data["passhash"])==True:
        encrypted_key=data["privatekey"]
        decrypted_key=xor_decrypt(encrypted_key,hashed)
        return str(decrypted_key)
    else:
        return None

def get_name():
    data = read_file()
    if not data or data == "None":
        return None

    try:
        data_dict = json.loads(data)
        name = data_dict.get("name", None)
        return name
    except:
        return None

