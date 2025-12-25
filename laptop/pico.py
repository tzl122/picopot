import os,hashlib
import serial,json
import base58
import time
import requests
import codecs
from cryptography.hazmat.primitives.asymmetric import ed25519
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solana.rpc.api import Client
from solana.rpc.commitment import Finalized
from solana.rpc.types import TxOpts


class wallet:
	def __init__(self):
		connected=False
		print("connect your device")
		while connected==False:
			try:
				self.ser = serial.Serial("COM5", 115200, timeout=1)
				connected=True
			except:
				pass

		print("Connected Waiting to boot...")		
		time.sleep(3)
		self.wallet_name=str(self.send_command("getname"))
		if self.wallet_name is None or self.wallet_name == "None":
			pass
	
	def hash(self,text):
		hash_object = hashlib.sha256(str(text).encode('utf-8'))
		hex_digest = hash_object.digest()
		hex_digest_str = "".join("{:02x}".format(b) for b in hex_digest)
		return hex_digest_str
	
	def send_command(self,cmd):
		self.ser.reset_input_buffer()
		self.ser.write((cmd + "\n").encode())
		response = self.ser.readline().decode().strip()
		return response

	def create_wallet(self,name,password,password2):
		if password!=password2:
			return "password_mismatch"
		else:
			command=f"createwallet:{str(name)}:{str(password)}:{str(password2)}"
			self.ser.write((command + "\n").encode())
			
			print("⏳ Key generation started - waiting...")
			
			# ✅ SIMPLE - JUST LISTEN FOR ANY RESPONSE
			while True:
				response = self.ser.readline().decode().strip()
				if response:
					print(f"Pico: {response}")
					
				if response == "created":
					return "created"
				elif response == "walletexist":
					return "walletexist"
				elif response == "different password please try again":
					return "password_mismatch"

	def delete_wallet(self,password):
		command=f"deletewallet:{str(password)}"
		return self.send_command(command)

	def get_privatekey(self,password):
		command=f"getprivatekey:{str(password)}"
		recieve=self.send_command(command)
		if recieve=="wrongpass":
			return "wrongpass"
		else:
			return self.xor_decrypt(recieve,self.hash(password))
	
	def hex_bytes(self,hex):
		return bytes.fromhex(hex)

	def xor_decrypt(self,msg,k):
		key=self.hex_bytes(k)
		message=self.hex_bytes(msg)
		result = bytes([message[i]^key[i%len(key)] for i in range(len(message))])
		return result.hex()

	def get_address(self,hex_public_key_str: str) -> str:
		"""
		Converts a hex-encoded raw 32-byte Ed25519 Public Key into a 
		Solana Base58-encoded address.
		
		Solana addresses are simply the raw 32-byte public key Base58-encoded.
		"""
		
		# 1. Decode the hex string into raw 32-byte bytes
		try:
			public_key_bytes = codecs.decode(hex_public_key_str, 'hex')
		except Exception:
			return "Error: Invalid hexadecimal string format."

		if len(public_key_bytes) != 32:
			return f"Error: Public key must be exactly 32 bytes (64 hex characters), got {len(public_key_bytes)} bytes."
		solana_address = base58.b58encode(public_key_bytes).decode('utf-8')
		
		return solana_address

	def get_balance(self, address_str):
		client = Client("https://api.devnet.solana.com")  
		pubkey = Pubkey.from_string(address_str)
		res = client.get_balance(pubkey) 
		lamports = res.value
		return lamports / 1_000_000_000

	def get_walletinfo(self):
		try:
			name=self.wallet_name
			public_key=self.get_publickey()
			addr=self.get_address(public_key)
			balance=self.get_balance(addr)
			return {
				"name":name,
				"address":addr,
				"public_key":public_key,
				"balance": balance
			}
		except:
			return "No wallet, fail to load wallet"

	def get_publickey(self):
		return self.send_command("getpublickey")
	
	def send_sol(self, private_key_hex: str, recipient_address: str, amount_sol: float):
		client = Client("https://api.devnet.solana.com")
		LAMPORTS_PER_SOL = 1_000_000_000
		
		try:
			sk_bytes = bytes.fromhex(private_key_hex)
			if len(sk_bytes) != 32:
				raise ValueError("Private key must be 32 bytes (64 hex).")
			sender = Keypair.from_seed(sk_bytes)
		except Exception as e:
			raise Exception(f"Invalid private key: {e}")

		sender_pub = sender.pubkey()
		recipient_pub = Pubkey.from_string(recipient_address)
		
		# Get sender's current balance
		try:
			balance_resp = client.get_balance(sender_pub)
			current_balance_lamports = balance_resp.value
			current_balance_sol = current_balance_lamports / LAMPORTS_PER_SOL
		except Exception as e:
			raise Exception(f"Failed to get balance: {e}")

		# --- Calculate actual transaction fee ---
		try:
			# First, build the transaction to calculate fee
			bh = client.get_latest_blockhash().value.blockhash
			ix = transfer(
				TransferParams(
					from_pubkey=sender_pub,
					to_pubkey=recipient_pub,
					lamports=10000,  # Dummy amount for fee calculation
				)
			)
			tx = Transaction.new_signed_with_payer(
				instructions=[ix],
				payer=sender_pub,
				signing_keypairs=[sender],
				recent_blockhash=bh,
			)
			
			# Get fee for the transaction
			fee_response = client.get_fee_for_message(tx.message)
			if fee_response.value is None:
				raise Exception("Could not calculate transaction fee")
			
			actual_fee_lamports = fee_response.value
			actual_fee_sol = actual_fee_lamports / LAMPORTS_PER_SOL
			
			# Add small buffer for safety (10%)
			fee_buffer = actual_fee_lamports * 0.1
			total_fee_lamports = actual_fee_lamports + fee_buffer
			total_fee_sol = total_fee_lamports / LAMPORTS_PER_SOL
			
		except Exception as e:
			print(f"Fee calculation failed, using default: {e}")
			# Fallback to safe estimate
			total_fee_lamports = 10000  # 0.00001 SOL as fallback
			total_fee_sol = 0.00001

		# Calculate maximum possible amount (leave room for actual fees)
		max_possible_amount = current_balance_sol - total_fee_sol
		
		# If trying to send more than possible, adjust automatically
		if amount_sol > max_possible_amount:
			if max_possible_amount <= 0:
				raise Exception(f"Insufficient balance for fees. Need at least {total_fee_sol:.6f} SOL for transaction fees.")
			
			# Auto-adjust to maximum possible amount
			adjusted_amount = max_possible_amount
			print(f"⚠️  Adjusted amount from {amount_sol} SOL to {adjusted_amount:.6f} SOL to cover {total_fee_sol:.6f} SOL in fees")
			amount_sol = adjusted_amount

		lamports = int(amount_sol * LAMPORTS_PER_SOL)

		# Final validation
		if current_balance_lamports < lamports + total_fee_lamports:
			raise Exception(f"Insufficient balance. Have {current_balance_sol:.6f} SOL, need {amount_sol:.6f} SOL + {total_fee_sol:.6f} SOL fees = {amount_sol + total_fee_sol:.6f} SOL total.")

		# --- Now build the actual transaction ---
		try:
			bh = client.get_latest_blockhash().value.blockhash
		except Exception as e:
			raise Exception(f"Failed to fetch blockhash: {e}")

		# --- Create actual instruction ---
		ix = transfer(
			TransferParams(
				from_pubkey=sender_pub,
				to_pubkey=recipient_pub,
				lamports=lamports,
			)
		)

		# --- Build + sign tx ---
		try:
			tx = Transaction.new_signed_with_payer(
				instructions=[ix],
				payer=sender_pub,
				signing_keypairs=[sender],
				recent_blockhash=bh,
			)
		except Exception as e:
			raise Exception(f"Transaction signing failed: {e}")

		# --- Send transaction ---
		try:
			opts = TxOpts(
				skip_preflight=False,
				preflight_commitment=Finalized,
				skip_confirmation=False,
				max_retries=10,
			)
			resp = client.send_transaction(tx, opts=opts)
			return f"{resp.value} (Fee: {total_fee_sol:.6f} SOL)"  # Return signature + fee info
		except Exception as e:
			raise Exception(f"RPC send_transaction error: {e}")
		