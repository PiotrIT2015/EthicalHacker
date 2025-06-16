#!/usr/bin/env python3
import socket
import select
import sys
import matplotlib.pyplot as plt

# --- walidacja argumentów -------------------------------
if len(sys.argv) != 4:
    print("Usage: python banner_grab.py <IP> <first_port> <last_port>")
    sys.exit(1)

ip    = sys.argv[1]
start = int(sys.argv[2])
end   = int(sys.argv[3])

open_ports   = []
banner_sizes = []

for port in range(start, end + 1):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex((ip, port)) == 0:         # 0 => połączenie OK
                ready, _, _ = select.select([s], [], [], 1)
                if ready:
                    banner = s.recv(4096)
                    print(f"TCP {port:>5} – {banner.decode(errors='replace').strip()}")
                    open_ports.append(port)
                    banner_sizes.append(len(banner))
    except Exception as e:
        print(f"[{port}] {e}")

if open_ports:
    plt.plot(open_ports, banner_sizes, marker="o")
    plt.xlabel("Port")
    plt.ylabel("Długość nagłówka (B)")
    plt.title(f"Rozmiary bannerów dla {ip}")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("Brak otwartych portów lub bannerów w podanym zakresie.")

