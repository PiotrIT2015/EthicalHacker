#!/usr/bin/env python3
"""
nmap_banner.py  <host> <first_port> <last_port>

Przykład: python nmap_banner.py 10.0.0.5 1 100
"""
import sys, nmap, json, matplotlib.pyplot as plt

# ---- Walidacja argumentów -------------------------------------
if len(sys.argv) != 4:
    print("Usage: python nmap_banner.py <host> <first_port> <last_port>")
    sys.exit(1)

host, p_start, p_end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

# ---- Konfiguracja Nmapa ---------------------------------------
nm = nmap.PortScanner()
port_range = f"{p_start}-{p_end}"

print(f"[+] Skanuję {host} TCP ports {port_range} …\n"
      f"    Używam -sV --script banner (może potrwać chwilę)\n")

nm.scan(
    hosts=host,
    ports=port_range,
    arguments="-sV --script banner --host-timeout 15m --max-retries 2",
)

# ---- Parsowanie wyników ---------------------------------------
open_ports, banner_sizes = [], []

for proto in nm[host].all_protocols():         # zwykle tylko 'tcp'
    for port in nm[host][proto]:
        state = nm[host][proto][port]["state"]
        if state != "open":
            continue

        # informacje o usłudze
        service = nm[host][proto][port].get("name", "?")
        product = nm[host][proto][port].get("product", "")
        version = nm[host][proto][port].get("version", "")
        extrainfo = nm[host][proto][port].get("extrainfo", "")

        # banner z NSE (jeśli był)
        scripts = nm[host][proto][port].get("script", {})
        banner = scripts.get("banner", "").strip()

        print(f"TCP {port:>5} | {service:<10} "
              f"| {product} {version} {extrainfo}".strip())
        if banner:
            print(f"           banner: {banner}")

        open_ports.append(port)
        banner_sizes.append(len(banner.encode()))

# ---- Prosty wykres --------------------------------------------
if open_ports:
    plt.plot(open_ports, banner_sizes, marker="o")
    plt.title(f"Rozmiar bannerów dla {host}")
    plt.xlabel("Port")
    plt.ylabel("Długość bannera (B)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("\nBrak otwartych portów lub bannerów w podanym zakresie.")


