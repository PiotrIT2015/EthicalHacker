#!/usr/bin/env python3
"""
Pobiera wartość ciasteczek JSESSIONID i PHPSESSID z podanego URL.
Użycie: uruchom skrypt i podaj URL gdy program poprosi.
"""

import requests
from urllib.parse import urlparse

def normalize_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        raise ValueError("Pusty URL.")
    parsed = urlparse(raw_url)
    if not parsed.scheme:
        # jeśli brak schematu, dodaj https jako domyślny
        raw_url = "https://" + raw_url
    return raw_url

def get_session_cookies(url: str, timeout: int = 10, verify_ssl: bool = True):
    """Wykonuje GET i zwraca obiekt session.cookies (RequestsCookieJar)."""
    session = requests.Session()
    # Opcjonalne nagłówki, żeby imitować przeglądarkę
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; CookieFetcher/1.0)"
    })
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True, verify=verify_ssl)
        # session.cookies zawiera ciasteczka z całego przebiegu (po redirectach)
        return session.cookies, resp.status_code, resp.url
    except requests.exceptions.SSLError as e:
        raise RuntimeError(f"Błąd SSL: {e}")
    except requests.exceptions.ConnectTimeout:
        raise RuntimeError("Przekroczono limit czasu połączenia.")
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f"Błąd połączenia: {e}")
    except Exception as e:
        raise RuntimeError(f"Nieoczekiwany błąd: {e}")

def main():
    raw_url = input("Podaj URL (np. https://example.com): ").strip()
    try:
        url = normalize_url(raw_url)
    except ValueError as e:
        print("Błąd:", e)
        return

    # Opcjonalna konfiguracja — jeżeli potrzebujesz wyłączyć weryfikację SSL, ustaw False.
    verify_ssl = True

    try:
        cookies, status_code, final_url = get_session_cookies(url, verify_ssl=verify_ssl)
    except RuntimeError as e:
        print("Nie udało się pobrać strony:", e)
        return

    # Spróbuj pobrać konkretne ciasteczka
    jsession = cookies.get("JSESSIONID")
    phpsess = cookies.get("PHPSESSID")

    print(f"\nHTTP status: {status_code}")
    print(f"Końcowy URL po ewentualnych przekierowaniach: {final_url}\n")

    if jsession:
        print(f"Znaleziono JSESSIONID: {jsession}")
    else:
        print("Nie znaleziono ciasteczka JSESSIONID.")

    if phpsess:
        print(f"Znaleziono PHPSESSID: {phpsess}")
    else:
        print("Nie znaleziono ciasteczka PHPSESSID.")

    # Dodatkowo wypisz wszystkie ciasteczka (opcjonalnie)
    if len(cookies) > 0:
        print("\nWszystkie ciasteczka (nazwa = wartość):")
        for name, value in cookies.items():
            print(f" - {name} = {value}")
    else:
        print("\nBrak ciasteczek w odpowiedzi.")

    print("\nUwaga bezpieczeństwa: nigdy nie ujawniaj prawdziwych wartości sesji innym osobom. "
          "Wykorzystuj te dane tylko na domenach, do których masz uprawnienia.")

if __name__ == "__main__":
    main()
