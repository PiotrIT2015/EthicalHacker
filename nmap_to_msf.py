#!/usr/bin/env python3
"""
nmap_to_msf.py
- uruchamia nmap (zapis xml)
- łączy się do Metasploit RPC (pymetasploit3)
- importuje xml przez db_import
- pobiera i wypisuje hosts/services

Uwaga: działa z msfrpcd lub z msfconsole z załadowanym msgrpc.
Instalacja: pip install pymetasploit3
"""

import argparse
import os
import subprocess
import tempfile
import time
from pathlib import Path

# pymetasploit3
try:
    from pymetasploit3.msfrpc import MsfRpcClient
except Exception as e:
    raise SystemExit("Musisz zainstalować 'pymetasploit3'. Uruchom: pip install pymetasploit3\nSzczegóły: " + str(e))


def run_nmap_xml(target, extra_args=None, out_prefix=None):
    """Uruchamia nmap i zapisuje wynik w formacie XML (oraz .nmap/.gnmap). Zwraca ścieżkę do pliku XML."""
    if extra_args is None:
        extra_args = []
    if out_prefix is None:
        tmpdir = tempfile.mkdtemp(prefix="nmap_msf_")
        out_prefix = os.path.join(tmpdir, "scan")
    cmd = ["nmap", "-sS", "-sV", "-p-", "-T4", "-oA", out_prefix, target] + extra_args
    print("[*] Uruchamiam nmap:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"nmap zakończył się błędem: {e}")
    xml_path = out_prefix + ".xml"
    if not os.path.exists(xml_path):
        raise SystemExit("nmap nie wygenerował pliku XML (sprawdź uprawnienia / dostępność nmap).")
    print("[+] Plik XML:", xml_path)
    return xml_path


def connect_msf(rpc_password, host="127.0.0.1", port=55553, ssl=False):
    """
    Łączy z Metasploit RPC.
    Domyślnie port 55553 dla msfrpcd; dla msgrpc plugin w msfconsole port 55552 (można zmienić).
    """
    print(f"[*] Łączenie z Metasploit RPC @ {host}:{port} (ssl={ssl}) ...")
    client = MsfRpcClient(rpc_password, server=host, port=port, ssl=ssl)
    if not client.authenticated:
        raise SystemExit("Nie udało się uwierzytelnić w Metasploit RPC (sprawdź hasło, port, czy msfrpcd/msgrpc działa).")
    print("[+] Połączono z Metasploit RPC.")
    return client


def console_exec_and_read(console, cmd, wait=0.3, timeout=10.0):
    """
    Zapisuje komendę do konsoli RPC, czyta wyjście aż do promptu lub timeout.
    Zwraca zebrany output (string).
    """
    if not cmd.endswith("\n"):
        cmd = cmd + "\n"
    console.write(cmd)
    out = ""
    deadline = time.time() + timeout
    while True:
        part = console.read()
        # `read()` zwraca dict z kluczami: data, prompt, busy
        data = ""
        try:
            data = part.get("data", "")
        except Exception:
            data = str(part)
        out += data
        # jeśli prompt == 'msf > ' i busy == False → zakończ
        prompt = part.get("prompt") if isinstance(part, dict) else None
        busy = part.get("busy") if isinstance(part, dict) else False
        if prompt and not busy and prompt.strip().endswith("msf >"):
            break
        if time.time() > deadline:
            out += "\n[!] timeout reading console\n"
            break
        time.sleep(wait)
    return out


def import_xml_via_console(client, xml_path):
    """
    Import pliku XML do Metasploit poprzez wykonywanie komendy 'db_import <xml>' w konsoli RPC.
    Zwraca output konsoli.
    """
    cons = client.consoles.console()
    # odczytaj początkowy baner
    _ = cons.read()
    cmd = f"db_import {xml_path}"
    print("[*] Importuję do Metasploit:", cmd)
    out = console_exec_and_read(cons, cmd, wait=0.2, timeout=60.0)
    return out, cons


def run_hosts_services(cons):
    """Uruchamia 'hosts -c address,mac,os_name' i 'services -c host,port,name,info' i zwraca wyniki."""
    print("[*] Pobieram hosts ...")
    hosts_out = console_exec_and_read(cons, "hosts -c address,mac,os_name", wait=0.2, timeout=10.0)
    print("[*] Pobieram services ...")
    services_out = console_exec_and_read(cons, "services -c host,port,name,info", wait=0.2, timeout=10.0)
    return hosts_out, services_out


def main():
    p = argparse.ArgumentParser(description="Nmap -> Metasploit import (bez exploitowania).")
    p.add_argument("--target", required=True, help="adres IP/host do przeskanowania")
    p.add_argument("--rpc-pass", required=True, help="hasło RPC Metasploit (msfrpcd lub msgrpc Pass)")
    p.add_argument("--rpc-host", default="127.0.0.1", help="host Metasploit RPC")
    p.add_argument("--rpc-port", type=int, default=55553, help="port Metasploit RPC (default 55553 msfrpcd)")
    p.add_argument("--rpc-ssl", action="store_true", help="użyj SSL do RPC (jeśli skonfigurowane)")
    args = p.parse_args()

    xml = run_nmap_xml(args.target)
    client = connect_msf(args.rpc_pass, host=args.rpc_host, port=args.rpc_port, ssl=args.rpc_ssl)
    import_out, cons = import_xml_via_console(client, xml)
    print("\n=== db_import output ===\n")
    print(import_out)

    hosts_out, services_out = run_hosts_services(cons)
    print("\n=== hosts (columns: address,mac,os_name) ===\n")
    print(hosts_out)
    print("\n=== services (columns: host,port,name,info) ===\n")
    print(services_out)

    print("\n[+] Gotowe. Pamiętaj: skrypt nie wykonuje exploitów.")

if __name__ == "__main__":
    main()
