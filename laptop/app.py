# gui.py (laptop) - WITH USD CONVERSION
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
from PIL import Image, ImageTk
import time
import os
import requests

# Import your existing pico.py functionality
from pico import wallet

class PicoPotGUI:
    def __init__(self):
        # Setup LIGHT theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("PicoPot Wallet")
        self.root.geometry("380x580")  # Slightly taller for USD display
        self.root.resizable(False, False)
        
        # Initialize wallet connection
        self.wallet = None
        self.is_unlocked = False
        self.sol_price = 0.0  # SOL to USD price
        self.price_loading = True
        
        # Create welcome screen first
        self.create_welcome_screen()
        
        # Start connection after UI is shown
        self.root.after(1000, self.connect_wallet)
        # Start price updates
        self.root.after(2000, self.start_price_updates)
    
    def get_sol_price(self):
        """Get SOL to USD price from Binance API"""
        try:
            url = "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT"
            response = requests.get(url, timeout=5)
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"Failed to get SOL price: {e}")
            # Fallback price if API fails
            return 100.0  # Reasonable fallback
    
    def start_price_updates(self):
        """Start background thread for price updates"""
        def price_thread():
            while True:
                try:
                    new_price = self.get_sol_price()
                    self.sol_price = new_price
                    self.price_loading = False
                    # Update USD value if wallet is unlocked
                    if self.is_unlocked:
                        self.root.after(0, self.refresh_balance)
                except Exception as e:
                    print(f"Price update error: {e}")
                # Update every 30 seconds
                time.sleep(30)
        
        threading.Thread(target=price_thread, daemon=True).start()
    
    def connect_wallet(self):
        """Connect to Pico wallet in background"""
        def connect_thread():
            try:
                # Simulate loading for demo
                for i in range(5):
                    time.sleep(0.3)
                    progress = (i + 1) * 20
                    self.root.after(0, lambda p=progress: self.update_loading(p))
                
                self.wallet = wallet()
                self.root.after(0, self.show_password_screen)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Connection Error", f"Failed to connect to Pico: {e}"))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def create_welcome_screen(self):
        """Welcome/loading screen with logo"""
        self.clear_screen()
        
        main_frame = ctk.CTkFrame(self.root, fg_color="white")
        main_frame.pack(expand=True, fill="both", padx=0, pady=0)
        
        logo_frame = ctk.CTkFrame(main_frame, fg_color="white")
        logo_frame.pack(expand=True, fill="both", pady=30)
        
        try:
            logo_path = "logo.png"
            if os.path.exists(logo_path):
                original_image = Image.open(logo_path)
                resized_image = original_image.resize((150, 150), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(resized_image)
                
                logo_label = ctk.CTkLabel(logo_frame, image=self.logo_image, text="")
                logo_label.pack(pady=15)
            else:
                self.create_fallback_logo(logo_frame)
        except Exception as e:
            print(f"Logo loading failed: {e}")
            self.create_fallback_logo(logo_frame)
        
        title = ctk.CTkLabel(logo_frame, text="PicoPot", 
                           font=("Arial", 24, "bold"),
                           text_color="#2b2b2b")
        title.pack(pady=8)
        
        subtitle = ctk.CTkLabel(logo_frame, text="Hardware Cold Wallet", 
                              font=("Arial", 12),
                              text_color="#666666")
        subtitle.pack(pady=3)
        
        loading_frame = ctk.CTkFrame(main_frame, fg_color="white")
        loading_frame.pack(fill="x", padx=40, pady=20)
        
        self.loading_label = ctk.CTkLabel(loading_frame, 
                                        text="Connecting to Pico...",
                                        font=("Arial", 11),
                                        text_color="#444444")
        self.loading_label.pack(pady=8)
        
        self.progress = ctk.CTkProgressBar(loading_frame, 
                                         height=6,
                                         progress_color="#4CC9F0")
        self.progress.pack(fill="x", pady=8)
        self.progress.set(0)
        
        self.status_label = ctk.CTkLabel(loading_frame, 
                                       text="Initializing...",
                                       font=("Arial", 9),
                                       text_color="#888888")
        self.status_label.pack(pady=3)
    
    def create_fallback_logo(self, parent):
        """Create a fallback logo if image is not found"""
        logo_text = ctk.CTkLabel(parent, text="🪙", 
                               font=("Arial", 80),
                               text_color="#4CC9F0")
        logo_text.pack(pady=30)
    
    def show_password_screen(self):
        """Password unlock screen after connection"""
        self.clear_screen()
        
        main_frame = ctk.CTkFrame(self.root, fg_color="white")
        main_frame.pack(expand=True, fill="both", padx=0, pady=0)
        
        logo_frame = ctk.CTkFrame(main_frame, fg_color="white")
        logo_frame.pack(expand=True, fill="both", pady=20)
        
        try:
            logo_path = "logo.png"
            if os.path.exists(logo_path):
                original_image = Image.open(logo_path)
                resized_image = original_image.resize((100, 100), Image.Resampling.LANCZOS)
                self.logo_image_small = ImageTk.PhotoImage(resized_image)
                
                logo_label = ctk.CTkLabel(logo_frame, image=self.logo_image_small, text="")
                logo_label.pack(pady=10)
            else:
                logo_text = ctk.CTkLabel(logo_frame, text="🪙", 
                                       font=("Arial", 50),
                                       text_color="#4CC9F0")
                logo_text.pack(pady=10)
        except:
            logo_text = ctk.CTkLabel(logo_frame, text="🪙", 
                                   font=("Arial", 50),
                                   text_color="#4CC9F0")
            logo_text.pack(pady=10)
        
        title = ctk.CTkLabel(logo_frame, text="PicoPot", 
                           font=("Arial", 20, "bold"),
                           text_color="#2b2b2b")
        title.pack(pady=5)
        
        password_frame = ctk.CTkFrame(main_frame, fg_color="white")
        password_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(password_frame, 
                   text="Enter Password to Unlock", 
                   font=("Arial", 14, "bold"),
                   text_color="#2b2b2b").pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(password_frame, 
                                         width=200, 
                                         height=35,
                                         show="•",
                                         placeholder_text="Enter wallet password...",
                                         font=("Arial", 12))
        self.password_entry.pack(pady=10)
        self.password_entry.bind('<Return>', lambda e: self.unlock_wallet())
        
        unlock_btn = ctk.CTkButton(password_frame, 
                                 text="🔓 Unlock Wallet", 
                                 width=200,
                                 height=35,
                                 font=("Arial", 12, "bold"),
                                 fg_color="#4CC9F0",
                                 hover_color="#3aa8d4",
                                 command=self.unlock_wallet)
        unlock_btn.pack(pady=10)
        
        self.error_label = ctk.CTkLabel(password_frame, 
                                      text="",
                                      text_color="red",
                                      font=("Arial", 10))
        self.error_label.pack(pady=5)
    
    def unlock_wallet(self):
        """Unlock wallet with password"""
        password = self.password_entry.get()
        
        if not password:
            self.error_label.configure(text="Please enter password")
            return
        
        def unlock_thread():
            try:
                private_key = self.wallet.get_privatekey(password)
                if private_key and private_key != "wrongpass":
                    self.root.after(0, self.show_main_ui)
                else:
                    self.root.after(0, lambda: self.error_label.configure(text="Wrong password!"))
            except Exception as e:
                self.root.after(0, lambda: self.error_label.configure(text=f"Error: {str(e)}"))
        
        threading.Thread(target=unlock_thread, daemon=True).start()
    
    def update_loading(self, progress):
        """Update loading progress and status"""
        self.progress.set(progress / 100)
        
        status_messages = {
            20: "Searching for device...",
            40: "Establishing connection...",
            60: "Handshaking with Pico...",
            80: "Loading wallet data...",
            100: "Connected!"
        }
        
        if progress in status_messages:
            self.status_label.configure(text=status_messages[progress])
    
    def show_main_ui(self):
        """Main wallet interface"""
        self.clear_screen()
        self.is_unlocked = True
        
        header_frame = ctk.CTkFrame(self.root, fg_color="#f8f9fa", height=60)
        header_frame.pack(fill="x", padx=8, pady=8)
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=10, pady=5)
        
        name_label = ctk.CTkLabel(header_content, 
                                text=f"👛 {self.wallet.wallet_name}", 
                                font=("Arial", 14, "bold"),
                                text_color="#2b2b2b")
        name_label.pack(side="left", pady=5)
        
        # Price display in header
        self.price_label = ctk.CTkLabel(header_content, 
                                      text="SOL: $...",
                                      text_color="#4CC9F0",
                                      font=("Arial", 10, "bold"))
        self.price_label.pack(side="right", pady=5)
        
        self.create_balance_card()
        self.create_action_buttons()
        self.create_transaction_section()
        self.create_bottom_menu()
        
        # Update price display
        self.update_price_display()
    
    def update_price_display(self):
        """Update the SOL price display in header"""
        if self.price_loading:
            price_text = "SOL: Loading..."
        else:
            price_text = f"SOL: ${self.sol_price:.2f}"
        self.price_label.configure(text=price_text)
    
    def create_balance_card(self):
        """Create balance display card with reload button and USD value"""
        balance_frame = ctk.CTkFrame(self.root, fg_color="#e9ecef", height=120)  # Taller for USD
        balance_frame.pack(fill="x", padx=15, pady=8)
        balance_frame.pack_propagate(False)
        
        balance_content = ctk.CTkFrame(balance_frame, fg_color="transparent")
        balance_content.pack(expand=True, fill="both", padx=15, pady=10)
        
        # Top row: Balance label + Reload button
        top_row = ctk.CTkFrame(balance_content, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 5))
        
        balance_label = ctk.CTkLabel(top_row, 
                                   text="Balance", 
                                   text_color="#666666", 
                                   font=("Arial", 11))
        balance_label.pack(side="left")
        
        # Reload button next to balance label
        reload_btn = ctk.CTkButton(top_row, 
                                 text="🔄", 
                                 width=30, 
                                 height=25,
                                 font=("Arial", 10),
                                 fg_color="#4CC9F0",
                                 hover_color="#3aa8d4",
                                 command=self.refresh_balance)
        reload_btn.pack(side="right")
        
        # SOL Balance amount
        self.balance_amount = ctk.CTkLabel(balance_content, 
                                         text="...", 
                                         font=("Arial", 20, "bold"),
                                         text_color="#2b2b2b")
        self.balance_amount.pack(anchor="w", pady=2)
        
        # USD Value
        self.usd_amount = ctk.CTkLabel(balance_content, 
                                     text="...", 
                                     font=("Arial", 14),
                                     text_color="#28a745")  # Green color for USD
        self.usd_amount.pack(anchor="w", pady=2)
        
        self.address_label = ctk.CTkLabel(balance_content, 
                                        text="...", 
                                        text_color="#666666", 
                                        font=("Arial", 9))
        self.address_label.pack(anchor="w", pady=2)
        
        # Load balance initially
        self.refresh_balance()
    
    def refresh_balance(self):
        """Refresh balance in background"""
        def refresh():
            try:
                wallet_info = self.wallet.get_walletinfo()
                if isinstance(wallet_info, dict):
                    balance = wallet_info["balance"]
                    address = wallet_info["address"][:8] + "..." + wallet_info["address"][-6:]
                    self.root.after(0, lambda: self.display_balance(balance, address))
                else:
                    self.root.after(0, lambda: self.display_balance(0, "No wallet"))
            except Exception as e:
                self.root.after(0, lambda: self.display_balance(0, f"Error: {e}"))
        
        threading.Thread(target=refresh, daemon=True).start()
    
    def display_balance(self, balance, address):
        """Update balance display with USD conversion"""
        self.balance_amount.configure(text=f"{balance:.6f} SOL")
        self.address_label.configure(text=address)
        
        # Update USD value
        if balance > 0 and self.sol_price > 0:
            usd_value = balance * self.sol_price
            self.usd_amount.configure(text=f"≈ ${usd_value:,.2f} USD")
        else:
            self.usd_amount.configure(text="≈ $0.00 USD")
        
        # Update price display
        self.update_price_display()
    
    def create_action_buttons(self):
        """Create Send/Receive buttons"""
        action_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=8)
        
        btn_row = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_row.pack(fill="x")
        
        send_btn = ctk.CTkButton(btn_row, 
                               text="📤 Send", 
                               width=110, 
                               height=38,
                               font=("Arial", 12, "bold"),
                               fg_color="#4CC9F0",
                               hover_color="#3aa8d4",
                               command=self.show_send_dialog)
        send_btn.pack(side="left", expand=True, padx=3)
        
        receive_btn = ctk.CTkButton(btn_row, 
                                  text="📥 Receive", 
                                  width=110, 
                                  height=38,
                                  font=("Arial", 12, "bold"),
                                  fg_color="#4CC9F0", 
                                  hover_color="#3aa8d4",
                                  command=self.show_receive_dialog)
        receive_btn.pack(side="right", expand=True, padx=3)
    
    def create_transaction_section(self):
        """Create transaction history section"""
        tx_frame = ctk.CTkFrame(self.root, fg_color="#f8f9fa")
        tx_frame.pack(fill="both", expand=True, padx=15, pady=8)
        
        tx_label = ctk.CTkLabel(tx_frame, 
                              text="Recent Transactions", 
                              font=("Arial", 12, "bold"),
                              text_color="#2b2b2b")
        tx_label.pack(pady=10)
        
        self.tx_text = ctk.CTkTextbox(tx_frame, 
                                    height=100,  # Slightly smaller to accommodate USD
                                    font=("Arial", 9),
                                    fg_color="white",
                                    text_color="#333333")
        self.tx_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.tx_text.insert("1.0", "No transactions yet...\n\nSend or receive SOL to see transactions here.")
        self.tx_text.configure(state="disabled")
    
    def create_bottom_menu(self):
        """Create bottom navigation menu - REMOVED SETTINGS"""
        menu_frame = ctk.CTkFrame(self.root, fg_color="#f8f9fa", height=45)
        menu_frame.pack(fill="x", side="bottom", pady=5)
        menu_frame.pack_propagate(False)
        
        btn_frame = ctk.CTkFrame(menu_frame, fg_color="transparent")
        btn_frame.pack(expand=True, fill="both", padx=15, pady=5)
        
        wallet_btn = ctk.CTkButton(btn_frame, 
                                 text="👛 Wallet", 
                                 width=100,
                                 height=30,
                                 font=("Arial", 10),
                                 fg_color="#6c757d",
                                 hover_color="#5a6268",
                                 command=self.show_wallet_management)
        wallet_btn.pack(side="left", padx=5)
        
        lock_btn = ctk.CTkButton(btn_frame, 
                               text="🔒 Lock", 
                               width=80,
                               height=30,
                               font=("Arial", 10),
                               fg_color="#6c757d",
                               hover_color="#5a6268",
                               command=self.lock_wallet)
        lock_btn.pack(side="right", padx=5)
    
    def lock_wallet(self):
        """Lock the wallet and return to password screen"""
        self.is_unlocked = False
        self.show_password_screen()
    
    def show_send_dialog(self):
        """Show send SOL dialog with dynamic fee info and USD conversion"""
        if not self.is_unlocked:
            messagebox.showwarning("Locked", "Please unlock wallet first")
            return
            
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Send SOL")
        dialog.geometry("400x450")  # Taller for USD info
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Get current balance first
        current_balance = 0
        try:
            wallet_info = self.wallet.get_walletinfo()
            if isinstance(wallet_info, dict):
                current_balance = wallet_info["balance"]
                usd_value = current_balance * self.sol_price if self.sol_price > 0 else 0
                balance_label = ctk.CTkLabel(dialog, 
                                           text=f"Current Balance: {current_balance:.6f} SOL (${usd_value:,.2f})",
                                           font=("Arial", 12, "bold"),
                                           text_color="#4CC9F0")
                balance_label.pack(pady=10)
        except:
            pass
        
        ctk.CTkLabel(dialog, text="Recipient Address:").pack(pady=8)
        address_entry = ctk.CTkEntry(dialog, width=350, placeholder_text="Enter Solana address...")
        address_entry.pack(pady=3)
        
        ctk.CTkLabel(dialog, text="Amount (SOL):").pack(pady=8)
        amount_entry = ctk.CTkEntry(dialog, width=200, placeholder_text="0.0")
        amount_entry.pack(pady=3)
        
        # USD conversion label
        usd_conversion_label = ctk.CTkLabel(dialog, 
                                          text="≈ $0.00 USD",
                                          text_color="#28a745",
                                          font=("Arial", 10))
        usd_conversion_label.pack(pady=2)
        
        # Update USD conversion when amount changes
        def update_usd_conversion(*args):
            try:
                amount = amount_entry.get()
                if amount and float(amount) > 0 and self.sol_price > 0:
                    usd_value = float(amount) * self.sol_price
                    usd_conversion_label.configure(text=f"≈ ${usd_value:,.2f} USD")
                else:
                    usd_conversion_label.configure(text="≈ $0.00 USD")
            except:
                usd_conversion_label.configure(text="≈ $0.00 USD")
        
        amount_entry.bind('<KeyRelease>', update_usd_conversion)
        
        # Dynamic fee info
        fee_info_label = ctk.CTkLabel(dialog, 
                                    text="💡 Calculating network fee...",
                                    text_color="#666666",
                                    font=("Arial", 10))
        fee_info_label.pack(pady=5)
        
        # Max amount button
        def set_max_amount():
            if current_balance > 0:
                # Leave room for fees by setting 99% of balance
                safe_max = current_balance * 0.99
                amount_entry.delete(0, 'end')
                amount_entry.insert(0, f"{safe_max:.6f}")
                fee_info_label.configure(text=f"💡 Max safe amount: {safe_max:.6f} SOL (includes fee buffer)")
                update_usd_conversion()
        
        max_btn = ctk.CTkButton(dialog, 
                              text="🎯 Set Max Safe Amount", 
                              width=180,
                              height=25,
                              font=("Arial", 10),
                              fg_color="#28a745",
                              hover_color="#218838",
                              command=set_max_amount)
        max_btn.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Wallet Password:").pack(pady=8)
        password_entry = ctk.CTkEntry(dialog, width=200, show="•")
        password_entry.pack(pady=3)
        
        def send_transaction():
            recipient = address_entry.get()
            amount = amount_entry.get()
            password = password_entry.get()
            
            if not all([recipient, amount, password]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            try:
                amount_float = float(amount)
                private_key = self.wallet.get_privatekey(password)
                
                if private_key and private_key != "wrongpass":
                    # Show loading
                    loading_label = ctk.CTkLabel(dialog, text="🔄 Processing transaction...", text_color="#4CC9F0")
                    loading_label.pack(pady=5)
                    dialog.update()
                    
                    result = self.wallet.send_sol(private_key, recipient, amount_float)
                    messagebox.showinfo("Success", f"✅ Transaction sent!\n\nSignature: {result}")
                    dialog.destroy()
                    self.refresh_balance()
                else:
                    messagebox.showerror("Error", "❌ Wrong password!")
            except Exception as e:
                error_msg = str(e)
                if "insufficient balance" in error_msg.lower():
                    error_msg = "💰 Insufficient balance for transaction + fees. Try sending a slightly smaller amount or use the 'Set Max Safe Amount' button."
                elif "adjusted amount" in error_msg.lower():
                    messagebox.showwarning("Amount Adjusted", f"⚠️ {error_msg}")
                    return
                messagebox.showerror("Error", f"❌ {error_msg}")
        
        send_btn = ctk.CTkButton(dialog, 
                               text="🚀 Send Transaction", 
                               fg_color="#4CC9F0",
                               hover_color="#3aa8d4",
                               command=send_transaction)
        send_btn.pack(pady=15)
        
        # Calculate and show actual fee estimate
        def update_fee_estimate():
            try:
                fee_estimate = 0.000005
                fee_usd = fee_estimate * self.sol_price if self.sol_price > 0 else 0
                fee_info_label.configure(text=f"💡 Estimated fee: ~{fee_estimate:.6f} SOL (${fee_usd:.4f})")
            except:
                fee_info_label.configure(text="💡 Network fee: ~0.000005 SOL (estimate)")
        
        dialog.after(1000, update_fee_estimate)
    
    def show_receive_dialog(self):
        """Show receive address dialog"""
        if not self.is_unlocked:
            messagebox.showwarning("Locked", "Please unlock wallet first")
            return
            
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Receive SOL")
        dialog.geometry("350x200")
        
        try:
            wallet_info = self.wallet.get_walletinfo()
            if isinstance(wallet_info, dict):
                address = wallet_info["address"]
                
                ctk.CTkLabel(dialog, text="Your Address:", font=("Arial", 12)).pack(pady=15)
                
                addr_frame = ctk.CTkFrame(dialog, fg_color="#e9ecef")
                addr_frame.pack(fill="x", padx=15, pady=8)
                
                addr_label = ctk.CTkLabel(addr_frame, 
                                        text=address, 
                                        font=("Arial", 9),
                                        wraplength=300)
                addr_label.pack(pady=8, padx=8)
                
                def copy_address():
                    self.root.clipboard_clear()
                    self.root.clipboard_append(address)
                    messagebox.showinfo("Copied", "Address copied to clipboard!")
                
                copy_btn = ctk.CTkButton(dialog, 
                                       text="Copy Address", 
                                       fg_color="#4CC9F0",
                                       hover_color="#3aa8d4",
                                       command=copy_address)
                copy_btn.pack(pady=8)
            else:
                ctk.CTkLabel(dialog, text="No wallet found").pack(pady=20)
        except:
            ctk.CTkLabel(dialog, text="Error loading wallet").pack(pady=20)
    
    def show_wallet_management(self):
        """Show wallet management options - FIXED DELETE WALLET"""
        if not self.is_unlocked:
            messagebox.showwarning("Locked", "Please unlock wallet first")
            return
            
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Wallet Management")
        dialog.geometry("350x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create new wallet section
        create_frame = ctk.CTkFrame(dialog)
        create_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(create_frame, text="Create New Wallet", 
                   font=("Arial", 12, "bold")).pack(pady=8)
        
        ctk.CTkLabel(create_frame, text="Wallet Name:").pack()
        name_entry = ctk.CTkEntry(create_frame, width=200)
        name_entry.pack(pady=3)
        
        ctk.CTkLabel(create_frame, text="Password:").pack()
        pass1_entry = ctk.CTkEntry(create_frame, width=200, show="•")
        pass1_entry.pack(pady=3)
        
        ctk.CTkLabel(create_frame, text="Confirm Password:").pack()
        pass2_entry = ctk.CTkEntry(create_frame, width=200, show="•")
        pass2_entry.pack(pady=3)
        
        def create_wallet():
            name = name_entry.get()
            pass1 = pass1_entry.get()
            pass2 = pass2_entry.get()
            
            if not all([name, pass1, pass2]):
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            if pass1 != pass2:
                messagebox.showerror("Error", "Passwords don't match")
                return
            
            def create_thread():
                try:
                    result = self.wallet.create_wallet(name, pass1, pass2)
                    self.root.after(0, lambda: messagebox.showinfo("Result", result))
                    if result == "created":
                        self.root.after(0, dialog.destroy)
                        self.root.after(0, self.show_password_screen)
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            
            threading.Thread(target=create_thread, daemon=True).start()
        
        create_btn = ctk.CTkButton(create_frame, 
                                 text="Create Wallet",
                                 fg_color="#4CC9F0",
                                 hover_color="#3aa8d4", 
                                 command=create_wallet)
        create_btn.pack(pady=8)
        
        # Delete wallet section - FIXED
        delete_frame = ctk.CTkFrame(dialog)
        delete_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(delete_frame, text="Delete Wallet", 
                   font=("Arial", 12, "bold")).pack(pady=8)
        
        ctk.CTkLabel(delete_frame, text="Password:").pack()
        del_pass_entry = ctk.CTkEntry(delete_frame, width=200, show="•")
        del_pass_entry.pack(pady=3)
        
        def delete_wallet():
            password = del_pass_entry.get()
            if not password:
                messagebox.showerror("Error", "Enter password")
                return
            
            if messagebox.askyesno("Confirm", "Permanently delete wallet? This cannot be undone!"):
                def delete_thread():
                    try:
                        result = self.wallet.delete_wallet(password)
                        self.root.after(0, lambda: messagebox.showinfo("Result", result))
                        if result == "done":
                            self.root.after(0, dialog.destroy)
                            self.root.after(0, self.show_password_screen)
                        elif result == "wrongpass":
                            self.root.after(0, lambda: messagebox.showerror("Error", "Wrong password!"))
                        else:
                            self.root.after(0, lambda: messagebox.showerror("Error", "Failed to delete wallet"))
                    except Exception as e:
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Delete failed: {str(e)}"))
                
                threading.Thread(target=delete_thread, daemon=True).start()
        
        delete_btn = ctk.CTkButton(delete_frame, 
                                 text="Delete Wallet", 
                                 fg_color="#dc3545",
                                 hover_color="#c82333",
                                 command=delete_wallet)
        delete_btn.pack(pady=8)
    
    def clear_screen(self):
        """Clear all widgets from root"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

# Run the application
if __name__ == "__main__":
    app = PicoPotGUI()
    app.run()