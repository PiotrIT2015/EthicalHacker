Super — przygotowałem kompletny, praktyczny scenariusz łączący **nmap → portscan → Metasploit** przeznaczony do testów na *własnej* infrastrukturze (lab / własna maszyna). Pokazuję polecenia, jak importować wyniki do Metasploit, jak bezpiecznie zbierać informacje i jak interpretować rezultaty. Nie będę opisywał kroków uruchamiania exploitów — to ofensywne działania, które można wykonywać tylko za wyraźną zgodą i w kontrolowanym środowisku.

# Gdy i dlaczego taki workflow?

Cel: rzetelne odkrycie usług widocznych z sieci, szybka klasyfikacja podatności i uporządkowana baza wyników do dalszej analizy/raportu.
Używamy:

* **nmap** — szybkie i dokładne wykrywanie portów / banerów / wersji, zapis wyników.
* **Metasploit Framework (msfconsole)** — import wyników, scentralizowane repozytorium hostów/usług, skanery auxiliary do dalszego potwierdzania wersji i prostych słabych konfiguracji; raportowanie.
* (opcjonalnie) narzędzia lokalne do korelacji (Windows: `netstat`, `Get-NetTCPConnection`, TCPView).

---

# 1) Przykładowy plan działań (high-level)

1. Przygotowanie: upewnij się, że skanujesz tylko systemy, do których masz prawo. Włącz Npcap (Windows) / uruchom nmap jako admin/root.
2. Pełny nmap TCP + detekcja usług, zapisz wyniki w formatach.
3. (Opcjonalnie) skan UDP (wolny) dla krytycznych portów (53, 161, 137/138).
4. Załaduj wyniki do Metasploit (db_import) lub użyj `db_nmap` z poziomu msfconsole.
5. W Metasploit przejrzyj hosty/usługi, uruchom bezpieczne auxiliary-scanery do potwierdzenia banerów i konfiguracji.
6. Skompresuj wyniki do raportu; lokalnie porównaj z `netstat`/PowerShell, by znaleźć usługi bound only to localhost.

---

# 2) Konkretne polecenia — nmap (przykład)

Uruchom z innej maszyny w sieci (skan „z zewnątrz” hosta):

```bash
# TCP: wszystkie porty, service/version detection, zapisz w trzech formatach (nmap, xml, grepable)
sudo nmap -sS -sV -p- -T4 --version-intensity 5 -oA scans/target 192.168.1.42

# Jeżeli chcesz UDP (bardzo wolne), przykładowo tylko DNS + SNMP:
sudo nmap -sU -sV -p 53,161 -T3 -oA scans/target_udp 192.168.1.42

# Jeśli firewall blokuje ICMP:
sudo nmap -Pn -sS -sV -p- -oA scans/target_noping 192.168.1.42
```

Wyjścia: `scans/target.nmap`, `scans/target.xml`, `scans/target.gnmap`. XML przyda się do importu do Metasploit.

---

# 3) Import wyników do Metasploit i podstawowa praca z DB

Uruchom Metasploit (`msfconsole`) — w większości instalacji (Kali/Metasploit on Windows) dostępne z terminala:

W msfconsole:

```
# (opcjonalnie) uruchom i sprawdź DB:
db_status

# importuj plik XML z nmap:
db_import /ścieżka/do/scans/target.xml

# pokaż hosty i usługi:
hosts
services

# przeszukaj konkretne hosty:
hosts -c address,mac,os_name
services -C host:192.168.1.42

# możesz także uruchomić nmap bezpośrednio przez Metasploit:
db_nmap -sS -sV -p- 192.168.1.42
```

`db_import` wczyta hosty, porty i wykryte wersje jako rekordy w bazie danych Metasploit — wygodne do dalszych zapytań / raportów.

---

# 4) Użycie modułów auxiliary (bez uruchamiania exploitów)

Metasploit posiada wiele *bezpiecznych* modułów skanujących / zbierających informacje (np. wersje protokołów, sprawdzenie anonimowych dostępów, słabe konfiguracje). Przykładowy, bezpieczny przebieg:

W msfconsole:

```
# zobacz dostępne skanery
search type:auxiliary name:scanner

# np. sprawdzenie wersji HTTP (pobranie nagłówków) — nie robi exploitów, tylko zbiera info
use auxiliary/scanner/http/http_version
set RHOSTS 192.168.1.42
set THREADS 10
run

# skaner SSH wersji
use auxiliary/scanner/ssh/ssh_version
set RHOSTS 192.168.1.42
run
```

Te moduły jedynie łączą się i zbierają banery — pomagają potwierdzić to, co nmap zgadł. Nie podaję modułów exploitujących podatności w konkretnych usługach.

---

# 5) Interpretacja wyników — jak korelować nmap ⇄ Metasploit ⇄ Windows

1. `nmap` pokazuje port X jako `open` i `Service: name/version`.

   * W Metasploit: po `db_import` znajdziesz ten port w `services`. Możesz uruchomić odpowiedni auxiliary scanner, by potwierdzić baner/protokół.
   * W Windows (na skanowanym hoście): użyj `netstat -ano` lub PowerShell `Get-NetTCPConnection -State Listen` aby sprawdzić, **czy proces nasłuchuje na 0.0.0.0 czy tylko na 127.0.0.1**. Jeśli 127.0.0.1 — nmap z zewnątrz tego nie pokaże.

2. `nmap` pokazuje port jako `filtered`

   * Metasploit: możesz próbować `auxiliary/scanner` modułami, ale wynik też może być filtrowany. Sprawdź firewall na hoście (`wf.msc` / `Get-NetFirewallRule`) lub reguły na routerze.
   * Windows lokalnie: `netsh advfirewall firewall show rule name=all` + Event Log do debugu.

3. Rozbieżność wersji (nmap mówi np. `Apache 2.4.6`, Metasploit/auxiliary zwraca inny baner)

   * Banery mogą być zmodyfikowane; potwierdź wersję pliku binarnego lokalnie albo sprawdź HTTP response headers bezpośrednio (curl/wget/telnet) i porównaj.

---

# 6) Przykładowy, bezpieczny raport z wynikami

* Host: `192.168.1.42`

  * nmap: `22/tcp open ssh OpenSSH 7.9` → zaimportowane do MSF (services table).
  * Windows: `Get-NetTCPConnection` → `0.0.0.0:22` → PID 1234 → `sshd.exe` (potwierdzenie procesu).
  * RDP `3389/tcp` → `filtered` (nmap) → Windows Firewall block inbound RDP rule → action: konieczna korekta reguł jeśli dostęp z zewnątrz wymagany.
  * Elasticsearch `9200` widoczny lokalnie (127.0.0.1) → brak w nmap z zewnątrz → decyzja bezpieczeństwa: zostawić bound na localhost, albo jeśli trzeba expose’ować — dodać auth i ograniczyć IP.

W raporcie wypisz: wykryte usługi, porty, pewność (nmap baner vs auxiliary potwierdzenie vs lokalne potwierdzenie procesu), rekomendacje (zamknąć nieużywane, ograniczyć bind address, dodać firewall, uwierzytelnienie).

---

# 7) Bezpieczeństwo, etyka i ograniczenia

* **Zawsze** testuj tylko systemy, do których masz uprawnienia. Skanowanie i próby wykorzystania luk bez zgody mogą być przestępstwem.
* Metasploit to potężne narzędzie ofensywne; traktuj je jako narzędzie testowe w kontrolowanym labie. Opisane powyżej kroki (nmap, db_import, auxiliary scanners) są informacyjne i obronne.
* Wyniki detekcji wersji to heurystyka — ZAWSZE weryfikuj lokalnie, zanim wyciągniesz wnioski o podatnościach.

---

# 8) Chcesz skrypt / gotowy playbook?

Mogę przygotować od razu:

* PowerShell script, który zbiera `Get-NetTCPConnection` + `Get-Service` i tworzy CSV raportu; **lub**
* Bash skrypt (Linux) / instrukcję krok-po-kroku do automatycznego nmap → db_import → uruchomienia kilku auxiliary scannerów → wygenerowania prostego raportu.

Który wariant wolisz? (PowerShell dla Windows czy skrypt bash dla maszyny atakującej w labie?)

Dobra — zrobię to praktycznie i bezpiecznie. Poniżej znajdziesz gotowy **skrypt w Pythonie**, który:

1. Uruchamia `nmap` (zapisuje wynik w XML),
2. łączy się do działającego Metasploit RPC (msfrpcd lub msfconsole + `load msgrpc`),
3. importuje plik XML do bazy Metasploit (`db_import`),
4. uruchamia z poziomu konsoli Metasploit komendy `hosts` i `services` i wypisuje ich wynik (żebyś szybko zobaczył, co zostało zaimportowane).

Skrypt nie uruchamia exploitów — tylko automatyzuje **zbieranie danych** i import do Metasploit. Bazuje na bibliotece `pymetasploit3` (polecana do automatyzacji Metasploit w Pythonie). Dokumentacja i repozytorium biblioteki: pymetasploit3 (GitHub/PyPI). ([GitHub][1])

---

# Prerekwizyty — co musisz mieć przed uruchomieniem

* Zainstalowany `nmap` (dostępny w PATH).
* Metasploit uruchomione i dostępne przez RPC:

  * albo uruchom `msfrpcd -P <haslo>` (uruchamia daemon RPC),
  * albo uruchom `msfconsole` i w środku wykonaj `load msgrpc Pass=<haslo>`.
    (W README pymetasploit3 są oba warianty). ([GitHub][1])
* Zainstalowana biblioteka Python: `pip install pymetasploit3` (albo `pip3 install pymetasploit3`). ([PyPI][2])
* Uruchamiaj skan i import **TYLKO** na hostach, do których masz uprawnienia.

---

# Skrypt (python3)

Zapisz jako np. `nmap_to_msf.py` i uruchom: `python3 nmap_to_msf.py --target 192.168.1.42 --rpc-pass sekret`
(Przykładowe wywołanie w sekcji komentarza w skrypcie).


```
nmap_to_msf.py
- uruchamia nmap (zapis xml)
- łączy się do Metasploit RPC (pymetasploit3)
- importuje xml przez db_import
- pobiera i wypisuje hosts/services

Uwaga: działa z msfrpcd lub z msfconsole z załadowanym msgrpc.
Instalacja: pip install pymetasploit3
```



---

# Wyjaśnienie działania i wskazówki

* `run_nmap_xml` używa `nmap -sS -sV -p- -oA <prefix>` → tworzy pliki `.nmap`, `.xml`, `.gnmap`. Skrypt zwraca ścieżkę do XML (`<prefix>.xml`). To XML importuje Metasploit.
* `MsfRpcClient` z `pymetasploit3` łączy się z Metasploit RPC. Domyślnie `msfrpcd` słucha na 55553; `msfconsole` + plugin `msgrpc` domyślnie 55552 — dostosuj `--rpc-port`. Dokumentacja biblioteki pokazuje obie opcje. ([GitHub][1])
* Import wykonujemy przez konsolę RPC (wysyłamy komendę `db_import <plik.xml>`). To rozwiązanie jest uniwersalne (działa niezależnie od tego, czy RPC serwer to `msfrpcd` czy `msgrpc` w `msfconsole`) — RPC ma metody `console.write` i `console.read`. (Skrypt czeka aż konsola zwróci prompt lub do timeoutu.) ([docs.rapid7.com][3])
* Po imporcie uruchamiamy `hosts` oraz `services` przez konsolę by wypisać, co trafiło do bazy.

---

# Uwaga o zgodności / możliwych problemach

* Różne wersje Metasploit / pymetasploit3 mogą mieć drobne różnice w API (nazwy metod, obsługa SSL). Jeżeli klient nie może się połączyć: sprawdź, czy `msfrpcd` działa albo czy w msfconsole wykonałeś `load msgrpc Pass=<haslo>`. ([GitHub][1])
* Jeśli `console.read()` zwraca strukturę inną niż oczekiwana, skrypt doda info o timeout i wypisze surowy output — możesz wtedy dostosować `console_exec_and_read` (np. dłuższy timeout).
* Jeśli chcesz, mogę dopisać: automatyczne uruchamianie kilku **bezpiecznych** modułów `auxiliary/scanner/*` po imporcie (np. potwierdzanie banerów HTTP/SSH) — powiem też jak filtrować hosty i zapisywać CSV z wynikami.

---

# Bezpieczeństwo i etyka (krótkie przypomnienie)

* Ten skrypt służy do automatyzacji zbierania/porządkowania danych w legalnym kontekście (twoje maszyny / laby).
* **Nie** używaj go do atakowania systemów bez wyraźnej zgody właściciela. Metasploit potrafi wykonywać ofensywne akcje — skrypt celowo ich nie wykonuje.

---

Jeżeli chcesz, mogę teraz:

* dopracować skrypt (np. dodać logowanie do pliku CSV, workspace selection, automatyczne uruchamianie kilku `auxiliary/scanner` w Metasploit i zebranie ich outputu),
* albo przygotować wersję która nie uruchamia nmap lokalnie, tylko importuje wcześniej wygenerowany XML.

Co preferujesz?

[1]: https://github.com/DanMcInerney/pymetasploit3 "GitHub - DanMcInerney/pymetasploit3: Automation library for Metasploit"
[2]: https://pypi.org/project/pymetasploit3/?utm_source=chatgpt.com "pymetasploit3"
[3]: https://docs.rapid7.com/metasploit/standard-api-methods-reference/?utm_source=chatgpt.com "Standard API Methods Reference | Metasploit Documentation"
