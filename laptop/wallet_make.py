from pico import wallet

wallet=wallet()

print("1. For creating wallet")
print("2. For deleting an existing wallet")
option=str(input("num: "))
if option==str(1):
    username=str(input("username: "))
    pass1=str(input("password: "))
    pass2=str(input("passwrod again: "))
    wallet.create_wallet(username,pass1,pass2)
    username=""
    pass1=""
    pass2=""
elif option==str(2):
    passwd=str(input("password: "))
    print(wallet.delete_wallet(passwd))
    passwd=""
else:
    print("unknown option please try again")