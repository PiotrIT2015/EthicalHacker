Krótko: nic poza wykrywaniem żywych hostów — **`nmap -sn 10.6.6.0/24`** zrobi *ping scan* na całej podsieci /24 (adresy 10.6.6.0–10.6.6.255) i wypisze które adresy odpowiadają (są „up”). Nie wykonuje skanowania portów.

Szczegóły i ważne uwagi:

* `-sn` (dawniej `-sP`) = **host discovery only** — Nmap tylko wykrywa hosty, nie skanuje portów.
* Na sieci lokalnej uruchomiony jako root zwykle użyje **ARP** (bardzo skuteczne) i wtedy zobaczysz dodatkowo **MAC address** i producenta interfejsu. Uruchomiony bez uprawnień może użyć ICMP/TCP probe’ów (ICMP echo, sondy TCP), więc rezultat może się różnić.
* Jeśli hosty mają zapory blokujące ICMP i odpowiedzi TCP, mogą być oznaczone jako *down* mimo że są aktywne.
* Nmap wykona odwrócone wyszukiwanie DNS (jeśli dostępne) i wypisze nazwy hostów obok adresów IP.

Przykładowy (symulowany) output:

```
$ sudo nmap -sn 10.6.6.0/24

Starting Nmap 7.XX ( https://nmap.org ) at 2025-10-19 12:34 CEST
Nmap scan report for 10.6.6.1
Host is up (0.00033s latency).
MAC Address: 00:11:22:33:44:55 (Cisco Systems)

Nmap scan report for host-2.example.com (10.6.6.42)
Host is up (0.0012s latency).
MAC Address: AA:BB:CC:DD:EE:FF (Intel)

Nmap scan report for 10.6.6.100
Host is up (0.0021s latency).

Nmap done: 256 IP addresses (3 hosts up) scanned in 2.34 seconds
```

Rzeczy praktyczne:

* Chcesz zobaczyć MAC i vendor → uruchom z uprawnieniami root/sudo na tej samej sieci lokalnej.
* Podejrzanie mało „up” hostów → możliwe blokowanie ICMP/TCP przez firewall.
* Jeżeli chcesz dodatkowo przeskanować porty znalezionych hostów, użyj np. `nmap -sV 10.6.6.42` (po wykryciu adresu).

Jeśli chcesz, mogę: pokazać różnicę wyników z/bez sudo, albo przygotować polecenie które równocześnie zapisze wynik do pliku (np. `-oA`), albo zademonstrować przykładowy wynik dla Twojej podsieci. Co wolisz?

Krótko: `nmap 10.6.6.23` wykona domyślne skanowanie tej pojedynczej maszyny — czyli discovery + skan **1000 najczęściej używanych portów TCP** (domyślnie SYN scan jeśli masz uprawnienia root, inaczej TCP connect). Wynik to lista znalezionych portów (open/closed/filtered), ewentualne nazwy usług i kilka nagłówkowych informacji (reverse-DNS, czas skanu itp.).

Szczegóły ważne w praktyce

* Domyślnie Nmap:

  * sprawdza czy host jest „up” (host discovery),
  * skanuje **1000 najpopularniejszych portów TCP**,
  * robi **reverse DNS** (jeśli dostępne),
  * jeśli uruchomisz jako **root/sudo** → użyje **SYN scan** (`-sS`), szybciej i dyskretniej; bez uprawnień użyje **connect scan** (`-sT`).
* Nie wykonuje domyślnie wykrywania wersji usług (`-sV`) ani wykrywania systemu operacyjnego (`-O`) ani skanowania wszystkich portów (`-p-`).
* Jeśli host blokuje/ignoruje pakiety wykrywania hosta, nmap może uznać go za *down* — użyj `-Pn`, aby pominąć discovery i wymusić skanowanie portów.

Przykładowy (symulowany) output dla `nmap 10.6.6.23`:

```
$ nmap 10.6.6.23

Starting Nmap 7.xx ( https://nmap.org ) at 2025-10-19 13:00 CEST
Nmap scan report for 10.6.6.23
Host is up (0.0010s latency).
Not shown: 997 closed ports
PORT     STATE    SERVICE
22/tcp   open     ssh
80/tcp   open     http
443/tcp  filtered https

Nmap done: 1 IP address (1 host up) scanned in 2.45 seconds
```

Co robić dalej (opcje przydatne)

* Pełny zakres portów: `nmap -p- 10.6.6.23`
* Wykrywanie wersji usług: `nmap -sV 10.6.6.23`
* Wykrywanie systemu operacyjnego: `sudo nmap -O 10.6.6.23`
* Pomiń host discovery (jeśli host nie odpowiada na ping): `nmap -Pn 10.6.6.23`
* Zapis do plików: `nmap -oA wyniki 10.6.6.23`

Jeśli chcesz, przygotuję od razu polecenie dostosowane do Twojego celu (np. wykryć usługi, przeskanować wszystkie porty albo obejść blokadę ICMP) i wyjaśnię ryzyka/zgodę w kontekście Twojej sieci. Co chcesz zbadać?

Krótko: `sudo nmap -O 10.6.6.23` uruchomi **detekcję systemu operacyjnego** (OS fingerprinting) przeciwko hostowi 10.6.6.23, używając surowych pakietów (wymaga uprawnień root/sudo). Wynik to raport z próbą odgadnięcia systemu operacyjnego/wersji, plus standardowe informacje o hostie i portach, które nmap wykorzystał do fingerprintingu.

Co dokładnie robi i co zobaczysz

* `-O` = **OS detection** — Nmap wysyła różne niestandardowe pakiety TCP/UDP/ICMP i bada odpowiedzi (czas, ustawione flagi, specyficzne zachowania TCP/IP) aby dopasować „fingerprint” do bazy znanych systemów.
* Wymaga uruchomienia jako **root/sudo**, bo potrzebne są raw sockets / surowe pakiety.
* Wyświetli:

  * informację czy host jest *up* i jego latency,
  * listę wykrytych otwartych portów (jeśli jakieś znaleziono),
  * sekcję **OS details** z proponowanym systemem operacyjnym i pewnością (np. `Linux 3.x - 4.x`),
  * ewentualne **CPE** (standardowy identyfikator produktu),
  * **OS guesses** (czasami kilka propozycji z prawdopodobieństwami),
  * surowe dopasowanie fingerprinta (często na dole — „TCP sequence prediction”/„IP ID”/fingerprint).
* Jeśli Nmap nie ma wystarczających informacji, zgłosi, że nie może określić OS, lub poda słabe/niepewne dopasowania.

Typowy (symulowany) output:

```
$ sudo nmap -O 10.6.6.23

Starting Nmap 7.xx ( https://nmap.org ) at 2025-10-19 14:05 CEST
Nmap scan report for 10.6.6.23
Host is up (0.0010s latency).
Not shown: 997 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https

Device type: general purpose
Running: Linux 3.X|4.X
OS CPE: cpe:/o:linux:linux_kernel:3
OS details: Linux 3.2 - 4.9
Network Distance: 1 hop

OS detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 4.32 seconds
```

Rzeczy, o których warto pamiętać (praktyka)

* **Dokładność zależy od dostępnych portów i odpowiedzi hosta.** Jeżeli host ma tylko bardzo niewiele otwartych portów lub filtruje pakiety (firewall), wykrycie może być niemożliwe lub błędne.
* **Możesz zwiększyć szanse wykrycia**: otwarte porty (serwisy) pomagają; możesz też użyć `-A` (agresywny — włącza `-O`, `-sV`, skrypty NSE itp.), `--osscan-guess` (wypróbowuje mniej pewne dopasowania) lub `--osscan-limit` (skanuje tylko hosty, które wyglądają obiecująco).
* **Skan raw (sudo) jest szybciej i dokładniej** niż bez uprawnień (które zmuszają nmap do użycia `connect()` zamiast surowych pakietów).
* **Etyka i prawo**: OS fingerprinting jest technicznie inwazyjny — zawsze miej zgodę właściciela sieci/hosta przed skanowaniem produkcyjnych systemów.
* **Jeśli wynik jest „No OS matches for host”** — spróbuj `-sV` aby zebrać informacje o usługach, lub `-Pn` jeśli host nie odpowiada na discovery.

Chcesz, żebym przygotował polecenie z dodatkowymi flagami (np. `sudo nmap -A 10.6.6.23` lub `sudo nmap -O --osscan-guess -sV -Pn 10.6.6.23`) i wyjaśnił kiedy które użyć?

Świetne pytanie — to już bardziej precyzyjny i ukierunkowany skan.
Polecenie:

```
nmap -v -p21 -sV -T4 10.6.6.23
```

oznacza: **zeskanuj tylko port 21 (FTP) na hoście 10.6.6.23, w trybie wykrywania wersji usługi, z podwyższoną szybkością, pokazując więcej informacji**.

---

### 🔍 Rozbicie opcji:

* `-v` → **verbose mode** — pokazuje więcej informacji o postępach i szczegółach skanu (np. kiedy host jest up, jakie porty zostały sprawdzone, szczegóły sond).
* `-p21` → skanuje **tylko port 21/tcp**, który standardowo służy do **FTP (File Transfer Protocol)**.
* `-sV` → **service version detection** — Nmap próbuje nawiązać „inteligentną” komunikację z usługą (np. wysyła komendy FTP) i zidentyfikować oprogramowanie i wersję.
* `-T4` → **tempo skanowania: aggressive (4)** — skraca czasy oczekiwania i zwiększa równoległość. Szybciej, ale może powodować pominięcia w wolnych lub niestabilnych sieciach.
* `10.6.6.23` → adres celu.

---

### 🧾 Co otrzymasz w wyniku:

Nmap najpierw sprawdzi, czy host jest **up**, a potem wyświetli status portu 21 i — jeśli jest otwarty — spróbuje rozpoznać oprogramowanie serwera FTP.

Przykładowy (symulowany) output:

```
$ nmap -v -p21 -sV -T4 10.6.6.23

Starting Nmap 7.xx ( https://nmap.org ) at 2025-10-19 14:30 CEST
Initiating Ping Scan at 14:30
Scanning 10.6.6.23 [4 ports]
Completed Ping Scan at 14:30, 0.01s elapsed (1 total hosts)
Initiating Parallel DNS resolution of 1 host. at 14:30
Completed Parallel DNS resolution of 1 host. at 14:30, 0.01s elapsed
Initiating SYN Stealth Scan at 14:30
Scanning 10.6.6.23 [1 port]
Discovered open port 21/tcp on 10.6.6.23
Completed SYN Stealth Scan at 14:30, 0.02s elapsed (1 total ports)
Initiating Service scan at 14:30
Scanning 1 service on 10.6.6.23
Completed Service scan at 14:30, 6.01s elapsed (1 service on 1 host)

Nmap scan report for 10.6.6.23
Host is up (0.0010s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3

Service Info: OS: Unix; CPE: cpe:/o:linux:linux_kernel

Read data files from: /usr/share/nmap
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 6.48 seconds
           Raw packets sent: 10 (400B) | Rcvd: 8 (320B)
```

---

### 🧠 Interpretacja:

* **Port 21/tcp open** → port otwarty, czyli host nasłuchuje na FTP.
* **SERVICE VERSION** → zidentyfikowano serwer FTP (np. `vsftpd 3.0.3` lub `Microsoft ftpd`).
* **Service Info: OS: Unix** → próba określenia platformy na podstawie bannerów i odpowiedzi.
* Jeśli port byłby zamknięty:

  ```
  21/tcp closed ftp
  ```
* Jeśli filtrowany (firewall blokuje):

  ```
  21/tcp filtered ftp
  ```

---

### 📈 W skrócie:

Polecenie `nmap -v -p21 -sV -T4 10.6.6.23`:

* sprawdza czy host 10.6.6.23 odpowiada,
* bada tylko port 21/tcp,
* jeśli otwarty, identyfikuje oprogramowanie i wersję serwera FTP,
* zwraca pełny raport w stylu Nmap.

---

Chcesz, żebym pokazał przykład wyniku dla portu zamkniętego lub filtrowanego (firewall)?

Krótko: `nmap -p21 -sV -A 10.6.6.23` zrobi skan **tylko portu 21**, spróbuje wykryć wersję usługi (`-sV`) i uruchomi **agresywne wykrywanie** (`-A` → włącza m.in. OS detection, service-version, domyślne skrypty NSE oraz traceroute). Zwróci raport o stanie portu, wersji serwera FTP, ewentualnych wynikach NSE (np. banner, podatności, anon. dostęp), oraz (jeśli możliwe) zgadywane OS i trasę sieciową.

Co dokładnie się dzieje:

* `-p21` → skan tylko portu 21/tcp.
* `-sV` → wykrywanie wersji usługi (banner + testy protokołowe).
* `-A` → kombinuje: `-O` (OS fingerprinting), `-sV`, `-sC` (uruchamia domyślne skrypty NSE) i `--traceroute`.
* Jeśli chcesz dokładnego OS fingerprintingu, zwykle potrzeba uruchomić z `sudo` (raw packets). `-A` sam w sobie nie wymusza sudo — bez sudo niektóre części mogą być mniej dokładne.
* Domyślne skrypty NSE wobec FTP mogą sprawdzać m.in. anon. dostęp, banner, podstawowe podatności i zachowania serwera — mogą to być dodatkowe linie w output’cie.

Przykładowy (symulowany) output:

```
$ nmap -p21 -sV -A 10.6.6.23

Starting Nmap 7.xx ( https://nmap.org ) at 2025-10-19 15:20 CEST
Nmap scan report for 10.6.6.23
Host is up (0.0011s latency).

PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_  - drwxr-xr-x  2 ftp      ftp          4096 Jan 01 12:00 pub
| ftp-syst: 
|   STAT: UNIX Type: L8
|_  FTP server returns system type
| ftp-vsftpd-backdoor: 
|   VULNERABLE:
|     vsftpd backdoor detected
|     (hypothetical example — real output depends on server)
|_  Refer to script output for details
| smb-security-mode: ERROR: Script tried to use a SMB type on non-SMB port
|_ (other NSE script lines...)

Device type: general purpose
Running: Linux 3.X|4.X
OS CPE: cpe:/o:linux:linux_kernel:3
OS details: Linux 3.2 - 4.9
Network Distance: 1 hop
TRACEROUTE
HOP RTT     ADDRESS
1   0.98 ms 10.6.6.23

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 7.45 seconds
```

Możliwe warianty wyników:

* Jeśli port jest **zamknięty**: `21/tcp closed ftp` — bez wykrywania wersji ani skryptów (większość NSE nic nie zrobi).
* Jeśli port jest **filtrowany** (firewall): `21/tcp filtered ftp` — skrypty i wykrywanie wersji mogą nie dać wyników.
* Jeżeli serwer nie ujawnia bannera lub blokuje sondy, `-sV` i `-O` mogą zwrócić słabe/niepewne dopasowania lub „No OS matches”.

Uwagi praktyczne / bezpieczeństwo:

* `-A` uruchamia skrypty NSE — może być „agresywne” i generować dodatkowy ruch; zawsze miej zgodę właściciela sieci/hosta.
* Dla mniej hałaśliwego rozpoznania użyj tylko `-sV` (bez `-A`) lub dodaj `-v` żeby zobaczyć więcej postępu.
* Jeśli chcesz wycisnąć więcej informacji (np. pełne skanowanie portów lub dokładniejsze skrypty NSE), mogę przygotować polecenie (np. `sudo nmap -p21,1-65535 -sV -A 10.6.6.23` lub konkretny zestaw skryptów).

Chcesz, żebyśmy zasymulowali wariant, gdzie port jest zamknięty, filtrowany, albo żeby przygotować bezpieczne polecenie do użycia w Twojej sieci?

# Co zwróci `nmap -A -p139,445 10.6.6.23`?

Krótko: zrobi agresywne rozpoznanie (OS detection, service version, domyślne skrypty NSE i traceroute) **tylko** dla portów **139** (NetBIOS/SMB over NetBIOS) i **445** (SMB over TCP) na hoście `10.6.6.23`. W rezultacie zobaczysz status tych portów (open/closed/filtered), bannery/versiony serwera SMB (np. Samba lub Windows SMB), wyniki odpowiednich skryptów NSE (np. `smb-os-discovery`, `smb-enum-shares`, `smb-security-mode`, możliwe testy podatności), oraz — jeśli możliwe — zgadywany system operacyjny i trasę.

---

### Co dokładnie się dzieje

* `-p139,445` → skan tylko tych dwóch portów.
* `-A` → `-O` (OS detect) + `-sV` (service version) + `-sC` (domyślne skrypty NSE) + `--traceroute`.
* Przy skryptach SMB Nmap uruchomi kilka NSE skryptów domyślnych, które mogą:

  * pobrać banner SMB (`smb-protocols`, `smb-os-discovery`),
  * wylistować udziały (`smb-enum-shares`) — jeśli są dostępne bez uwierzytelnienia,
  * sprawdzić tryb bezpieczeństwa i protokoły (`smb-security-mode`, `smb-protocols`),
  * wykonać dodatkowe testy/podatności, jeśli skrypt domyślnie jest uruchamiany.
* `-O` (część `-A`) działa lepiej z `sudo` (raw packets) — bez uprawnień wyniki OS mogą być mniej dokładne.

---

### Przykładowy (symulowany) output — oba porty otwarte (np. Windows Server / Samba)

```
$ sudo nmap -A -p139,445 10.6.6.23

Starting Nmap 7.xx ( https://nmap.org ) at 2025-10-19 16:00 CEST
Nmap scan report for 10.6.6.23
Host is up (0.0008s latency).

PORT    STATE SERVICE  VERSION
139/tcp open  netbios-ssn Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Microsoft Windows Server 2019 Standard (workgroup: WORKGROUP)
| smb-os-discovery: 
|   OS: Windows Server 2019 Standard 17763 (Windows Server 2019)
|   Computer name: TARGET-SRV
|   NetBIOS computer name: TARGET-SRV
|   Domain name: WORKGROUP
|_  System time: 2025-10-19T14:59:10+00:00
| smb-security-mode: 
|   Message signing: required
|_  SMBv1 disabled
| smb-enum-shares: 
|   \\TARGET-SRV\IPC$  - no access
|   \\TARGET-SRV\Public  (S) 
|_  \\TARGET-SRV\Backups  (E)
Device type: general purpose
Running: Microsoft Windows 10|Windows Server 2016|2019
OS CPE: cpe:/o:microsoft:windows_server_2019::standard
OS details: Microsoft Windows Server 2019
Network Distance: 1 hop
TRACEROUTE
HOP RTT     ADDRESS
1   0.80 ms 10.6.6.23

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 3.72 seconds
```

---

### Przykładowy output — porty filtrowane / zamknięte

```
PORT    STATE    SERVICE
139/tcp filtered netbios-ssn
445/tcp filtered microsoft-ds

# Przy filtrowanym porcie skrypty NSE często nie zwrócą dodatkowych informacji,
# a wykrywanie wersji/OS może być niemożliwe lub bardzo niepewne.
```

---

### Dodatkowe uwagi / praktyka

* **Autoryzacja**: niektóre skrypty (np. pełne wylistowanie udziałów, listowanie użytkowników) wymagają uwierzytelnienia; bez poświadczeń zobaczysz tylko to, co serwer udostępnia anonimowo.
* **Ryzyko i etyka**: `-A` może być „agresywny” — generuje dużo ruchu i może być wykrywany przez IDS/IPS. Zawsze miej zgodę właściciela sieci/hosta.
* **Dokładność OS**: `-O` działa najlepiej z `sudo`. Jeśli nie masz sudo, pomyśl o `sudo nmap -A -p139,445 ...`.
* **Skan podatności**: `-A` uruchamia tylko domyślne NSE; nie wykona pełnego audytu podatności. Jeżeli chcesz sprawdzić np. MS17-010/EternalBlue, użyj dedykowanych skryptów (np. `--script smb-vuln*`).
* **Uwaga na SMBv1**: skrypty mogą ujawnić informacje o używanych wersjach protokołu (SMBv1/v2/v3) — ważne z punktu widzenia bezpieczeństwa.

---

Chcesz, żebym zasymulował wynik dla konkretnego scenariusza (np. Samba na Linuxie z anonimowym FTP/UD)? Albo przygotować polecenie które dodatkowo użyje autoryzacji SMB (user:pass) przy skryptach NSE?

Krótko: `nmap -sV -p8888 10.6.6.11` sprawdzi **port 8888/tcp** na hoście `10.6.6.11` i spróbuje rozpoznać **usługę i jej wersję** (banner + aktywne testy protokołowe). Wynik to raport z informacją czy port jest `open/closed/filtered` oraz — jeżeli otwarty — kolumna `VERSION` z przypuszczalnym oprogramowaniem.

Poniżej trzy realistyczne, symulowane warianty outputu (najczęściej spotykane scenariusze).

---

## 1) Port otwarty — serwer HTTP (np. Jupyter / Node / Gunicorn)

```
$ nmap -sV -p8888 10.6.6.11

Starting Nmap 7.xx ( https://nmap.org ) at 2025-10-19 17:00 CEST
Nmap scan report for 10.6.6.11
Host is up (0.0009s latency).

PORT     STATE SERVICE VERSION
8888/tcp open  http    Jupyter Notebook httpd 6.4.0 (or Apache httpd 2.4.46; depends on banner)
|_http-server-header: JupyterHub/1.2.0 (example)
|_http-title: Jupyter Notebook
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 2.34 seconds
```

Interpretacja: port 8888 nasłuchuje usługi HTTP; `-sV` rozpoznał typ (np. Jupyter) i zwrócił banner / tytuł strony, jeśli serwer je ujawnił.

---

## 2) Port otwarty — niestandardowy serwer (np. aplikacja TCP bez bannera)

```
$ nmap -sV -p8888 10.6.6.11

Starting Nmap 7.xx ( https://nmap.org ) at 2025-10-19 17:01 CEST
Nmap scan report for 10.6.6.11
Host is up (0.0011s latency).

PORT     STATE SERVICE VERSION
8888/tcp open  unknown
| fingerprint-strings: 
|   NULL:    Welcome to my custom service v1.0
|_  GET /:    HTTP/1.1 200 OK
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 2.59 seconds
```

Interpretacja: port jest otwarty, ale `-sV` nie dopasowało go do znanej usługi — nmap wyświetlił surowy banner lub fragmenty odpowiedzi, które znalazł.

---

## 3) Port zamknięty / filtrowany

```
$ nmap -sV -p8888 10.6.6.11

Starting Nmap 7.xx ( https://nmap.org ) at 2025-10-19 17:02 CEST
Nmap scan report for 10.6.6.11
Host is up (0.0013s latency).

PORT     STATE    SERVICE
8888/tcp closed   api2 (example)
# lub jeśli firewall blokuje:
# 8888/tcp filtered unknown

Nmap done: 1 IP address (1 host up) scanned in 0.60 seconds
```

Interpretacja: `closed` = port nie nasłuchuje; `filtered` = pakiety są blokowane i nmap nie może określić stanu.

---

## Dodatkowe uwagi / co możesz zrobić dalej

* Jeśli chcesz więcej danych (banners, tytuł strony): dodaj `-sV -sC -p8888` (`-sC` uruchamia domyślne NSE, np. `http-title`).
* Jeśli `-sV` nie rozpoznał wersji, spróbuj `--version-all` by wymusić agresywniejsze testy:
  `nmap -sV --version-all -p8888 10.6.6.11`
* Po wykryciu HTTP możesz użyć `curl` lub przeglądarki: `curl -I http://10.6.6.11:8888/` żeby zobaczyć banner/headers.
* Jeśli host nie odpowiada na ping, a chcesz mimo to wymusić skan: `-Pn`.

Jeżeli chcesz, symuluję teraz konkretny output dla wybranego serwera (np. Jupyter Notebook, Gunicorn/Flask, Node.js) z bardziej szczegółowym bannerem — podaj który scenariusz mam zasymulować.
