#!/usr/bin/env python3
import socket, select, sys, matplotlib.pyplot as plt

if len(sys.argv) != 4:
    print("Usage: banner_grab.py <IP> <first_port> <last_port>")
    sys.exit(1)

ip, start, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
open_ports, banner_sizes = [], []

for port in range(start, end + 1):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex((ip, port)) == 0:          # 0 = połączenie OK
                r, _, _ = select.select([s], [], [], 1)
                if r:
                    banner = s.recv(4096)
                    txt = banner.decode(errors='replace').strip()
                    print(f"TCP {port:>5} – {txt}")
                    open_ports.append(port)
                    banner_sizes.append(len(banner))
    except Exception as e:
        print(f"[{port}] {e}")

if open_ports:
    plt.plot(open_ports, banner_sizes, marker="o")
    plt.xlabel("Port");  plt.ylabel("Banner length (bytes)")
    plt.title(f"Banners for {ip}");  plt.grid();  plt.show()
else:
    print("Brak otwartych portów lub bannerów w zakresie.")

