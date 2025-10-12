#!/usr/bin/env python3
"""
scapy_simple_scan.py
Prosty narzędzie do testów penetracyjnych (ICMP + TCP SYN scan) wykorzystujące scapy.
Interaktywne: pyta o adres, potwierdzenie uprawnień, zapisuje wynik do pliku .txt.

Uwaga: używaj tylko na systemach, do których masz zgodę.
Uruchom jako root/admin.
"""

import sys
import time
import socket
import argparse
from datetime import datetime
from scapy.all import IP, ICMP, TCP, sr1, sr, conf

# Domyślna lista portów (często wykorzystywane / typowe)
DEFAULT_PORTS = [21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 123, 135, 139, 143, 161, 162, 389, 443, 445, 465, 587, 636, 993, 995, 1723, 3306, 3389, 5900, 6379, 8000, 8080, 9200]

# Ustawienia domyślne
SYN_TIMEOUT = 1.0      # timeout na odpowiedź SYN/ACK (w sekundach)
SYN_RETRIES = 1
SLEEP_BETWEEN = 0.05   # opóźnienie pomiędzy wysyłanymi pakietami (rate limiting)
BANNER_TIMEOUT = 2.0   # timeout dla banner grab (socket)


def confirm_permission(target):
    print("\n!!! Uwaga !!!")
    print(f"Zamierzasz przeskanować host: {target}")
    print("Wykonuj testy tylko na systemach, do których masz upoważnienie.")
    ans = input("Czy masz zgodę właściciela/administratorów? (tak/nie): ").strip().lower()
    if ans not in ("tak", "t", "yes", "y"):
        print("Brak potwierdzenia — przerywam.")
        sys.exit(1)


def icmp_ping(target):
    """Prosty ICMP echo request - zwraca True jeśli odpowiedź (PONG)"""
    pkt = IP(dst=target)/ICMP()
    try:
        # sr1: send and receive one answer
        resp = sr1(pkt, timeout=1, verbose=0)
        if resp is None:
            return False, None
        else:
            # resp.ttl czy inne pola można wykorzystać
            return True, resp.summary()
    except PermissionError:
        raise
    except Exception as e:
        return False, f"błąd ICMP: {e}"


def syn_scan_ports(target, ports, timeout=SYN_TIMEOUT, retries=SYN_RETRIES, sleep_between=SLEEP_BETWEEN):
    """
    Wykonuje prosty TCP SYN scan (podobny do nmap -sS) na liście portów.
    Zwraca dict: port -> status ('open'/'closed'/'filtered'/ 'no-response') oraz dodatkowe info (raw summary)
    """
    results = {}
    conf.verb = 0  # wycisz scapy
    for port in ports:
        time.sleep(sleep_between)
        pkt = IP(dst=target)/TCP(dport=port, flags="S")
        try:
            resp = sr1(pkt, timeout=timeout, retry=retries, verbose=0)
        except Exception as e:
            results[port] = ("error", str(e))
            continue

        if resp is None:
            # brak odpowiedzi -> prawdopodobnie filtered albo drop
            results[port] = ("no-response", "")
        elif resp.haslayer(TCP):
            tcp_layer = resp.getlayer(TCP)
            if tcp_layer.flags & 0x12:  # SYN+ACK (0x12)
                # port otwarty — wysyłamy RST, żeby nie zostawić połowy połączenia
                rst = IP(dst=target)/TCP(dport=port, flags="R", seq=tcp_layer.ack)
                try:
                    # wysyłamy bez oczekiwania na odpowiedź
                    sr(rst, timeout=0.5, verbose=0)
                except Exception:
                    pass
                results[port] = ("open", f"SYN/ACK (seq={tcp_layer.seq} ack={tcp_layer.ack})")
            elif tcp_layer.flags & 0x14:  # RST+ACK (0x14) -> closed
                results[port] = ("closed", "RST/ACK")
            else:
                results[port] = ("unknown-tcp-flags", f"flags={tcp_layer.flags}")
        else:
            # otrzymano coś innego (np. ICMP unreachable)
            results[port] = ("other-response", resp.summary())
    return results


def banner_grab(target, port, timeout=BANNER_TIMEOUT):
    """
    Próbuje pobrać krótki banner z portu używając prostego socket.connect/read.
    Nie wysyła agresywnych payloadów — tylko czeka na to, co serwer sam wyśle.
    """
    try:
        with socket.create_connection((target, port), timeout=timeout) as s:
            s.settimeout(timeout)
            try:
                data = s.recv(1024)
                if not data:
                    return None
                try:
                    return data.decode(errors="replace").strip()
                except Exception:
                    return repr(data)
            except socket.timeout:
                return None
    except Exception as e:
        return f"socket-error: {e}"


def save_report(target, icmp_res, scan_results, banners, start_time):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"scan_{target}_{ts}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(f"Scan report for {target}\n")
        f.write(f"Start: {start_time.isoformat()}\n")
        f.write(f"End:   {datetime.now().isoformat()}\n\n")

        f.write("== ICMP ping ==\n")
        if icmp_res[0]:
            f.write(f"Responsive: YES\n")
            f.write(f"Detail: {icmp_res[1]}\n")
        else:
            f.write("Responsive: NO\n")
            if icmp_res[1]:
                f.write(f"Detail: {icmp_res[1]}\n")
        f.write("\n")

        f.write("== TCP SYN scan results ==\n")
        open_ports = []
        for port in sorted(scan_results.keys()):
            status, info = scan_results[port]
            f.write(f"Port {port:5d} : {status:12s}  {info}\n")
            if status == "open":
                open_ports.append(port)
        f.write("\n")

        if open_ports:
            f.write("== Banner grab (open ports) ==\n")
            for p in open_ports:
                b = banners.get(p)
                f.write(f"Port {p:5d}: banner: {b}\n")
        else:
            f.write("Brak otwartych portów (lub brak potwierdzeń SYN/ACK).\n")

    return fname


def main():
    parser = argparse.ArgumentParser(description="Prosty skaner (Scapy) - ICMP + TCP SYN scan; zapis wyników do .txt")
    parser.add_argument("--target", help="adres IP celu (opcjonalnie podany jako argument)", default=None)
    parser.add_argument("--ports", help="lista portów oddzielona przecinkami (np. 22,80,443) lub 'default'", default="default")
    parser.add_argument("--banner", help="czy próbować pobrać bannery z otwartych portów? (tak/nie)", default="tak")
    args = parser.parse_args()

    # input target
    target = args.target
    if not target:
        target = input("Podaj adres IPv4 celu: ").strip()
    if not target:
        print("Brak celu. Przerywam.")
        sys.exit(1)

    # confirm permission
    confirm_permission(target)

    # parse ports
    if args.ports == "default":
        ports = DEFAULT_PORTS
    else:
        try:
            ports = [int(p.strip()) for p in args.ports.split(",") if p.strip()]
            if not ports:
                ports = DEFAULT_PORTS
        except Exception:
            print("Błąd parsowania portów — używam domyślnej listy.")
            ports = DEFAULT_PORTS

    # banner option
    do_banner = str(args.banner).strip().lower() in ("tak", "t", "yes", "y", "1", "true")

    # run scans
    print(f"\n[*] Rozpoczynam skan na {target}")
    start_time = datetime.now()

    try:
        icmp_ok, icmp_info = icmp_ping(target)
    except PermissionError:
        print("[!] Błąd uprawnień: musisz uruchomić skrypt jako root/Administrator (żeby wysyłać ICMP/surowe pakiety).")
        sys.exit(1)
    except Exception as e:
        print("[!] Błąd podczas ICMP:", e)
        icmp_ok, icmp_info = (False, str(e))

    print(f"ICMP responsive: {'YES' if icmp_ok else 'NO'}")

    print(f"[*] TCP SYN scan: {len(ports)} portów (timeout={SYN_TIMEOUT}s, delay={SLEEP_BETWEEN}s)")
    scan_results = syn_scan_ports(target, ports)

    # banner grab only for open ports if user wants
    banners = {}
    if do_banner:
        open_ports = [p for p, (st, _) in scan_results.items() if st == "open"]
        if open_ports:
            print(f"[*] Próbuję pobrać bannery z portów: {open_ports}")
            for p in open_ports:
                b = banner_grab(target, p)
                banners[p] = b
                # małe opóźnienie
                time.sleep(0.2)
        else:
            print("[*] Brak otwartych portów do pobrania bannerów.")

    # save report
    fname = save_report(target, (icmp_ok, icmp_info), scan_results, banners, start_time)
    print(f"\n[+] Zapisano raport do pliku: {fname}")
    print("Koniec.")

if __name__ == "__main__":
    main()
