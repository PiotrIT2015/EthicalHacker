Świetnie — poniżej masz kompletny, praktyczny scenariusz użycia **nmap + narzędzi Windows** do odkrywania usług, wraz z konkretnymi poleceniami i wyjaśnieniem możliwych rezultatów oraz sposobem korelacji wyników nmap z informacjami lokalnymi w Windows. Zakładam, że chcesz zbadać **własną maszynę** (jej adres IPv4) i porównać to z tym, co widzi nmap z sieci.

# Założenia

* Masz zainstalowany **Nmap** na Windows (instalator Nmap instaluje też Npcap — potrzebne do niektórych trybów skanowania).
* Masz uprawnienia administratora do uruchamiania `netstat -abn`, `Get-NetTCPConnection` itp.
* Twoja maszyna ma adres IPv4, np. `192.168.1.42`.

---

# 1) Skanowanie z zewnątrz (inny komputer w tej samej sieci / inna maszyna)

Cel: zobaczyć co jest **widoczne z sieci** na twoim IPv4.

Przykładowe polecenia nmap (uruchom na *innejszym* komputerze niż skanowany host):

```bash
# szybki skan najczęściej używanych portów
nmap -sS -sV 192.168.1.42

# pełny skan wszystkich TCP portów + wykrycie wersji usług (wolniejsze)
nmap -sS -sV -p- 192.168.1.42

# dodaj UDP (bardzo wolne)
nmap -sS -sU -sV -p- 192.168.1.42

# jeśli host nie odpowiada na ICMP (firewall), wymuś brak pingów
nmap -Pn -sS -sV -p- 192.168.1.42
```

Co oznaczają najczęstsze wyniki nmap:

* `open` — na danym porcie jest socket nasłuchujący i usługa odpowiada na połączenia.
* `closed` — port osiągalny (host jest żywy), ale nic nie nasłuchuje na tym porcie.
* `filtered` — pakiet został zablokowany/odrzucony przez firewall lub brama — nmap nie może ustalić, czy port jest otwarty.
* `open|filtered` — typowy dla UDP: nie ma odpowiedzi, więc nie da się rozróżnić otwartego od filtrowanego.
* `Service detection` (`-sV`) pokaże baner/proto i zgadywaną wersję (np. `ssh 7.9p1 OpenSSH`), ale to zgadywanie — może być mylące przy baner-skróceniu lub niestandardowych usługach.

Opcje:

* TCP Connect Scan (-sT)
* UDP Scan (-sU)
* TCP FIN Scan (-sF)
* Host Discovery Scan (-sn)
* Timing Options (-T 0-5)

---

# 2) Lokalna inspekcja — co faktycznie nasłuchuje na maszynie (Windows)

Poniższe polecenia wykonujesz **na tej samej maszynie** co skanowany host — dzięki temu zobaczysz też usługi nasłuchujące tylko na localhost (127.0.0.1) i gniazda związane z konkretnymi procesami.

PowerShell (zalecane):

```powershell
# lista aktywnych nasłuchujących połączeń TCP/UDP (od Windows 10 / Server 2016)
Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess
Get-NetUDPEndpoint | Select-Object LocalAddress, LocalPort, OwningProcess

# powiąż PID z nazwą procesu
Get-Process -Id <PID>

# lista usług Windows
Get-Service | Where-Object {$_.Status -eq 'Running'} | Sort-Object DisplayName
```

Klasyczne narzędzia w CMD (również działają):

```cmd
# wyświetla porty i PID procesów (-b pokazuje nazwę programu, wymaga admin)
netstat -abn

# bez nazwy procesu (szybsze)
netstat -ano

# znajdź proces po PID
tasklist /FI "PID eq 1234"

# sprawdź czy port 80 jest osiągalny lokalnie (PowerShell)
Test-NetConnection -ComputerName 127.0.0.1 -Port 80
```

Dodatkowe GUI/narzędzia Sysinternals:

* **TCPView** (Sysinternals) — interaktywna lista gniazd i procesów (łatwe szybkie filtrowanie).
* **Resource Monitor** (`resmon`) → zakładka Network → Listening Ports.

---

# 3) Scenariusz krok-po-kroku z interpretacją

1. **Zrób lokalne sprawdzenie nasłuchujących gniazd:**

   ```powershell
   Get-NetTCPConnection -State Listen | Sort-Object LocalPort
   ```

   Przykładowy wynik:

   ```
   LocalAddress LocalPort OwningProcess
   ------------ --------- -------------
   0.0.0.0      22        1234
   127.0.0.1    5432      2345
   192.168.1.42 3389      3456
   ```

   Interpretacja:

   * Port `22` nasłuchuje na `0.0.0.0` → dostępny na wszystkich interfejsach (jeśli firewall pozwala) — możliwy do wykrycia przez nmap skanujący `192.168.1.42`.
   * Port `5432` nasłuchuje na `127.0.0.1` → **tylko lokalnie**; nmap skanujący z zewnątrz *go nie zobaczy*.
   * Port `3389` nasłuchuje na konkretnym interfejsie `192.168.1.42` → powinien być widoczny z sieci lokalnej.

2. **Skan z innej maszyny nmap:**

   ```bash
   nmap -sS -sV 192.168.1.42
   ```

   Możliwy wynik:

   ```
   PORT     STATE    SERVICE   VERSION
   22/tcp   open     ssh       OpenSSH 7.9
   80/tcp   closed   http
   3389/tcp filtered ms-wbt-server
   ```

   Interpretacja:

   * `22 open` → potwierdza lokalny `0.0.0.0:22`.
   * `80 closed` → host dostępny, ale nic nie nasłuchuje na 80 (może był kiedyś webserver, ale już go nie ma).
   * `3389 filtered` → lokalnie widzimy nasłuch na 3389, ale z zewnątrz pakiety są filtrowane (Windows Firewall lub router/NAT może blokować). Nmap nie może stwierdzić, czy port jest otwarty, bo nie widzi odpowiedzi.

3. **Szczegółowa korelacja PID ↔ proces**

   * z `netstat -ano` uzyskasz linijkę np. `TCP 192.168.1.42:22 0.0.0.0:0 LISTENING 1234`
   * potem `tasklist /FI "PID eq 1234"` → `sshd.exe` lub `sshd` (jeśli używasz OpenSSH dla Windows).
   * w PowerShell: `Get-Process -Id 1234 | Select-Object Name, Path`

   To pozwala stwierdzić: **nmap port 22 = proces OpenSSH uruchomiony lokalnie**.

4. **Jeżeli nmap pokazuje `filtered` lub `host down`**

   * Sprawdź lokalny firewall: `wf.msc` (Windows Defender Firewall with Advanced Security) albo:

     ```powershell
     # listuj reguły pozwalające na inbound RDP (3389)
     Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*RDP*" } | Get-NetFirewallPortFilter
     ```
   * Jeżeli host jest za NAT-em (np. router), zewnętrzny skan z internetu zobaczy tylko IP publiczne routera — musisz robić skan z maszyny w tej samej podsieci lub skonfigurować przekierowanie portów.

5. **UDP — dodatkowa ostrożność**

   * Jeżeli nmap dla UDP nie wykrywa usługi, nie znaczy że jej nie ma (często brak odpowiedzi). Potwierdź lokalnie komendą `Get-NetUDPEndpoint` i/lub sprawdź aplikację/proces (np. DNS serwer lokalny na 53).

---

# 4) Typowe przypadki rozbieżności i co z nimi robić

* **nmap widzi mniej usług niż lokalne `Get-NetTCPConnection`**
  Powód: niektóre usługi nasłuchują tylko na `127.0.0.1` lub `::1` — są niewidoczne z sieci. Rozwiązanie: jeśli chcesz, żeby były widoczne, zmodyfikuj konfigurację usługi (bind address), ale pamiętaj o ryzyku bezpieczeństwa.

* **nmap pokazuje port jako `filtered`, ale lokalnie jest `LISTENING`**
  Powód: Firewall (Windows Defender lub firewall sieciowy/router) blokuje ruch przychodzący. Sprawdź i ewentualnie dodaj regułę przychodzącą.

* **nmap `open` ale nie możesz połączyć się z usługą z przeglądarki/klienta**
  Możliwe przyczyny: service wymaga TLS/SNI, wymaga konkretnego host header, dostęp wymaga uwierzytelnienia, albo aplikacja filtruje klientów (np. bind do konkretnego interfejsu). Sprawdź baner `-sV` i spróbuj połączyć się telnetem: `telnet 192.168.1.42 22` lub `nc` (jeśli dostępne).

* **nmap wykrywa wersję usługi błędnie**
  `-sV` bazuje na banerach i heurystyce — porównaj z `Get-Process`/`Get-Service` (nazwa pliku wykonywalnego, wersja pliku) albo sprawdź konfigurację danej aplikacji.

---

# 5) Szybkie „cheat-sheet” poleceń (Windows)

Lokalnie (PowerShell, admin):

```powershell
# lokalne nasłuchy
Get-NetTCPConnection -State Listen

# powiąż PID → proces
Get-Process -Id <PID>

# listuj działające usługi
Get-Service | Where-Object {$_.Status -eq 'Running'}

# sprawdź reguły firewall
Get-NetFirewallRule | Where-Object {$_.Enabled -eq "True"} | Select-Object DisplayName,Direction,Action
```

CMD (admin):

```cmd
netstat -abn
netstat -ano | findstr LISTENING
tasklist /FI "PID eq 1234"
sc query <ServiceName>
```

Z innego hosta (nmap):

```bash
nmap -sS -sV -p22,80,3389 192.168.1.42
nmap -sS -sV -p- 192.168.1.42         # wszystkie TCP porty (wolne)
nmap -sU -p53 192.168.1.42           # przykładowy UDP port
```

Narzędzia GUI:

* **TCPView** (Sysinternals) — interaktywnie: proces ↔ port.
* **Resmon** (`resmon`) → Listening Ports.
* **Windows Defender Firewall with Advanced Security** (`wf.msc`) — reguły.

---

# 6) Przykład kompletnej analizy (skrót)

1. Uruchamiasz `Get-NetTCPConnection -State Listen` → widzisz `127.0.0.1:9200` (Elasticsearch), `0.0.0.0:22` (OpenSSH), `192.168.1.42:3389` (RDP).
2. Skanujesz nmap z innej maszyny: widzisz `22 open`, `3389 filtered`, brak `9200`.
3. Wniosek:

   * `9200` nie jest widoczne, bo bound do localhost → dostępne tylko lokalnie (bezpieczne).
   * `3389` jest filtrowane → sprawdź reguły firewall/port forwarding.
   * `22` otwarte → koreluj PID z `tasklist` → sprawdź czy to rzeczywiście sshd.exe.

---

# 7) Kilka praktycznych wskazówek bezpieczeństwa

* Nie wystawiaj usług nasłuchujących na `0.0.0.0` bez potrzeby. Jeżeli usługa powinna być lokalna — binduj do `127.0.0.1`.
* Utrzymuj zasady firewall — zamykaj nieużywane porty.
* Testuj skany nmap w swojej sieci tylko na hostach, do których masz prawo — skanowanie cudzych hostów bez zgody może być nielegalne.

---

Jeśli chcesz, mogę teraz:

* przygotować **skrypt PowerShell** który automatycznie wygeneruje tabelę nasłuchujących portów + nazw procesów + czy port jest dostępny z twojego innego adresu (Test-NetConnection),
* albo przygotować **konkretny zestaw poleceń nmap** dopasowany do twojej maszyny (podaj tylko jej IPv4 i czy chcesz skanować UDP).

Co wolisz?
