import sys
import os
import uhashlib
import ujson as json
from wallet import *
import utime

WALLET_FILE="wallet.dat"
run=True
def commands(line):
    if line=="stoptzl":
        return False
    
    elif line=="ping":
        sys.stdout.write("pong\n")
        return True
    
    elif line=="getname":
        sys.stdout.write(f"{get_name()}\n")
        return True
    
    elif line.startswith("getprivatekey"):
        data=read_file()
        if not data or data=="None" or data==None:
            sys.stdout.write("nowallet\n")
            data=""
            return True
        data=json.loads(data)
        password=line.split(":")[1]
        if hash(password)==data["passhash"]:
            sys.stdout.write(f"{data["privatekey"]}\n")
            data=""
            password=""
            return True
        else:
            sys.stdout.write("wrongpass\n")
            data=""
            password=""
            return True
        
    elif line.startswith("deletewallet"):
        data=read_file()
        if not data or data=="None" or data==None:
            sys.stdout.write("nowallet\n")
            data=""
            return True
        
        password=line.split(":")[1]
        ans_del=delete_wallet(password)
        if ans_del==0:
            sys.stdout.write("done\n")
            data=""
            password=""
            return True
        else:
            sys.stdout.write("wrongpass\n")
            data=""
            password=""
            return True
    
    elif line.startswith("createwallet"):
        usrdata=(line.split(":")[1],line.split(":")[2],line.split(":")[3])
        ans_make=create_wallet(usrdata[0],usrdata[1],usrdata[2])
        if ans_make=="walletexist":
            sys.stdout.write("walletexist\n")
            usrdata=""
            return True
        elif ans_make=="created":
            sys.stdout.write("created\n")
            usrdata=""
            return True

    elif line=="getpublickey":
        data=read_file()
        if not data or data=="None" or data==None:
            sys.stdout.write("nowallet\n")
            data=""
            return True
        else:
            data=json.loads(data)
            pub=data["publickey"]
            sys.stdout.write(f"{pub}\n")
            data=""
            pub=""
            return True
    else:
        sys.stdout.write("unknown\n")
        return True

while run==True:
    line=sys.stdin.readline().strip()
    if line:
        run=commands(line)
    else:
        pass
    utime.sleep(0.05)
