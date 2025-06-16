#!/usr/bin/env python3
import paramiko
import time
import ipaddress

def ip_address_valid(ip_addr: str) -> bool:
    try:
        ipaddress.IPv4Address(ip_addr)
        return True
    except ipaddress.AddressValueError:
        return False

def run_commands(
    ip: str,
    username: str,
    password: str,
    commands: list[str],
    delay: float,
    frequency: int
) -> None:
    session = None
    try:
        session = paramiko.SSHClient()
        session.load_system_host_keys()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Connecting to {ip} ...")
        session.connect(ip, username=username, password=password)

        chan = session.invoke_shell()
        chan.send("terminal length 0\n")
        time.sleep(1)

        for _ in range(frequency):
            for cmd in commands:
                chan.send(cmd + "\n")
                time.sleep(delay)
    except paramiko.AuthenticationException:
        print("✖  Błędny login lub hasło – sprawdź dane!")
    except Exception as exc:
        print(f"✖  Błąd: {exc}")
    finally:
        if session:
            session.close()

def main():
    while True:
        ip_addr = input("Adres IP urządzenia sieciowego: ").strip()
        if ip_address_valid(ip_addr):
            break
        print("✖  Niepoprawny adres IP – spróbuj ponownie.")

    username = input("Nazwa użytkownika: ").strip()
    password = input("Hasło: ").strip()
    commands = [cmd.strip() for cmd in input("Polecenia (oddzielone przecinkami): ").split(",")]
    delay = float(input("Opóźnienie między poleceniami (s): ").strip())
    frequency = int(input("Ile razy powtórzyć zestaw poleceń: ").strip())

    run_commands(ip_addr, username, password, commands, delay, frequency)

if __name__ == "__main__":
    main()
