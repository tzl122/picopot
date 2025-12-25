# port_scanner.py
import serial.tools.list_ports

def list_ports():
    print("📡 All connected COM ports:")
    print("=" * 30)
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("❌ No ports found")
        return
    
    for port in ports:
        print(f"🔌 {port.device}")

if __name__ == "__main__":
    list_ports()