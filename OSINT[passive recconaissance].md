# OSINT[polecenia i opisy]

- spiderfoot -l 127.0.0.1:5001

---

- `sfp_dnsresolve` to **moduł w frameworku SpiderFoot**, który służy do rozwiązywania nazw DNS (czyli tłumaczenia nazw domenowych na adresy IP) w trakcie pasywnego i aktywnego rozpoznania.

---

### Kontekst:

SpiderFoot to narzędzie typu OSINT (Open Source Intelligence), używane do automatycznego zbierania informacji o celach — na przykład domenach, adresach IP, osobach czy organizacjach.

### Moduł `sfp_dnsresolve`:

* **Typ modułu**: Aktywny (Active) — wykonuje zapytania DNS.
* **Funkcja**: Rozwiązuje rekordy DNS dla wykrytych nazw domen lub subdomen (np. A, AAAA, CNAME).
* **Zastosowanie**: Pomaga ustalić, jaki adres IP jest przypisany do danej domeny, co może być krokiem do dalszej analizy np. geolokalizacji, przypisania do ASN, detekcji hostów itp.
* **Źródło danych**: System DNS — czyli publiczne serwery nazw.

### Typowy przebieg działania:

1. Inny moduł odkrywa domenę (np. `example.com`).
2. `sfp_dnsresolve` otrzymuje zadanie rozwiązania tej domeny.
3. Wysyła zapytanie DNS i zapisuje odpowiedź (np. `example.com -> 93.184.216.34`).
4. Wynik przekazywany jest dalej do kolejnych modułów, które np. analizują ten adres IP.

### Przykłady zastosowania:

* Ustalenie infrastruktury domeny.
* Wykrywanie hostów powiązanych z daną organizacją.
* Łączenie subdomen z konkretnymi adresami IP.

---

- `sfp_email` to **moduł SpiderFoot** odpowiedzialny za **wyszukiwanie adresów e-mail** związanych z celem (np. domeną, firmą, osobą). Należy do grupy **modułów pasywnych** — czyli takich, które **nie nawiązują bezpośredniego kontaktu z celem**, tylko szukają danych w dostępnych źródłach OSINT.

---

### 🔍 Co robi `sfp_email`?

* **Zbiera adresy e-mail** znalezione w źródłach publicznych powiązanych z danym celem (np. `@example.com`).
* Przeszukuje źródła typu:

  * strony internetowe,
  * przecieki danych (jeśli dostępne przez inne moduły),
  * wyniki wyszukiwarek,
  * dane WHOIS i inne metadane.

---

### 📥 Jakie dane wejściowe akceptuje?

* Domeny (np. `example.com`)
* Nazwy organizacji

---

### 📤 Jakie dane wyjściowe generuje?

* Typ: `EMAILADDR` — konkretne adresy e-mail (np. `john.doe@example.com`)
* Mogą być później używane przez inne moduły, np.:

  * `sfp_leak` — sprawdzenie, czy e-mail wystąpił w wyciekach danych,
  * `sfp_googlesearch` — szukanie więcej informacji o adresie e-mail.

---

### 🧠 Przykład zastosowania:

Jeśli analizujesz firmę `example.com`, `sfp_email` może wykryć e-maile takie jak:

* `admin@example.com`
* `jan.kowalski@example.com`
* `security@example.com`

To może posłużyć do dalszej analizy OSINT lub do wykrywania punktów kontaktowych, kont użytkowników, phishingu itp.

---

- `sfp_crossref` to **moduł korelacyjny (cross-referencing) SpiderFoot**, który pełni rolę **wewnętrznego „łącznika”** między różnymi danymi zebranymi przez inne moduły. Nie pobiera danych z zewnętrznych źródeł, ale **analizuje i porównuje już zebrane informacje**, aby znaleźć dodatkowe powiązania i zależności.

---

### 🔍 Co robi `sfp_crossref`?

* **Korelacja danych**: analizuje dane takie jak:

  * adresy e-mail,
  * nazwy domen i subdomen,
  * adresy IP,
  * dane WHOIS,
  * identyfikatory użytkowników,
  * itd.
* Szuka wzorców i powiązań między elementami w różnych kontekstach.
* Wykrywa, czy pewne dane występują w wielu miejscach, np. ten sam e-mail w różnych domenach.

---

### 📥 Dane wejściowe:

* Praktycznie wszystkie dane generowane przez inne moduły, np.:

  * `EMAILADDR`
  * `INTERNET_NAME`
  * `USERNAME`
  * `PHONE_NUMBER`
  * `IP_ADDRESS`
  * itp.

---

### 📤 Dane wyjściowe:

* Zależnie od kontekstu, ale często:

  * `AFFILIATE_INTERNET_NAME` – inna domena powiązana z e-mailem/IP itp.
  * `RELATED_ENTITY` – np. inna osoba lub organizacja powiązana z tym samym kontaktem
  * `CORRELATED_DATA` – uogólnione oznaczenie korelacji między różnymi obiektami

---

### 🧠 Przykładowe zastosowania:

* Jeśli adres e-mail `admin@example.com` pojawia się także przy `example.net`, moduł oznaczy te domeny jako potencjalnie **powiązane**.
* Jeśli kilka subdomen wskazuje na ten sam adres IP, może to oznaczać wspólny serwer — a więc **powiązaną infrastrukturę**.
* W śledztwach OSINT pomaga budować **pełniejszy obraz** organizacji, osoby czy infrastruktury na podstawie subtelnych zależności.

---

### 🔧 Cechy:

| Cecha          | Opis                                           |
| -------------- | ---------------------------------------------- |
| Rodzaj         | Moduł **analizy wewnętrznej (internal logic)** |
| Źródła danych  | Dane zgromadzone przez inne moduły             |
| Tryb działania | **Pasywny**, bez zapytań na zewnątrz           |
| Typ            | Analityczny, wspierający                       |

---

### 💡 Użycie:

`sfp_crossref` **nie wymaga konfiguracji** – działa automatycznie, o ile inne moduły dostarczą odpowiednio bogaty zestaw danych.

---

- `sfp_urlscan` to **moduł SpiderFoot**, który integruje się z zewnętrzną usługą **[urlscan.io](https://urlscan.io/)** — platformą do analizowania i wizualizacji stron internetowych. Umożliwia **pasywną analizę domeny lub URL-a**, bez bezpośredniego kontaktu z celem.

---

### 🔍 Co robi `sfp_urlscan`?

* Przeszukuje **publiczne archiwum skanów** dostępne w urlscan.io.
* Wyszukuje informacje związane z celem (np. domeną, adresem IP, URL-em), takie jak:

  * kiedy dana strona była skanowana,
  * jakie hosty z niej się ładują (np. zasoby z zewnętrznych domen),
  * jakie technologie są używane (np. WordPress, jQuery),
  * powiązane adresy IP i domeny.

> **Uwaga**: `sfp_urlscan` nie wysyła nowych skanów — korzysta tylko z **danych historycznych**, czyli jest **modułem pasywnym**.

---

### 📥 Dane wejściowe:

* `INTERNET_NAME` (domena, subdomena)
* `URL`
* `IP_ADDRESS` (w ograniczonym zakresie)

---

### 📤 Dane wyjściowe:

* `URL` – adresy URL powiązane z celem
* `INTERNET_NAME` – nowe subdomeny lub domeny trzecie odnalezione w źródle
* `IP_ADDRESS` – adresy IP zasobów ładowanych przez stronę
* `AFFILIATE_INTERNET_NAME` – np. skrypty z zewnętrznych domen
* `MALICIOUS_CONTENT` – jeśli strona została oznaczona jako podejrzana

---

### 🧠 Przykład zastosowania:

Analizujesz domenę `example.com`. `sfp_urlscan` może wykryć:

* że ładuje zasoby z `analytics.eviltracker.net`,
* że podstrona `example.com/login` była skanowana i widnieje w archiwum urlscan.io,
* że pojawiły się skrypty JS od podejrzanych podmiotów.

Można to wykorzystać w analizie phishingu, malware, czy po prostu do **mapowania infrastruktury webowej**.

---

### 🔧 Wymagania:

* Niektóre funkcje mogą wymagać **API Key** do urlscan.io, ale dla danych publicznych zazwyczaj nie jest to konieczne.
* Moduł pasywny – **nie kontaktuje się bezpośrednio z analizowaną stroną**.

---

- `sfp_hackertarget` to **moduł SpiderFoot**, który korzysta z zewnętrznego serwisu **[HackerTarget.com](https://hackertarget.com/)** w celu pobrania danych OSINT związanych z domeną, adresem IP lub siecią.

---

### 🧩 Co robi `sfp_hackertarget`?

Moduł wysyła zapytania do API HackerTarget i pobiera dane takie jak:

* **Reverse DNS lookup** – czyli jakie domeny są przypisane do danego IP,
* **Reverse IP lookup** – inne domeny hostowane na tym samym IP,
* **WHOIS lookup** – informacje o właścicielu domeny/IP,
* **Subnet scan** – aktywne hosty w danym zakresie IP,
* **DNS dump** – rekordy DNS domeny,
* **HTTP headers** – nagłówki HTTP odpowiedzi serwera,
* **Geolokalizacja IP** – kraj, region, ASN itd.

> Uwaga: zakres danych zależy od tego, jakie zapytanie jest wykonywane (i co jest dostępne w darmowej wersji API).

---

### 📥 Dane wejściowe:

* `IP_ADDRESS`
* `INTERNET_NAME` (czyli domena lub subdomena)
* `NETBLOCK` (zakres IP, np. /24)

---

### 📤 Dane wyjściowe (różne typy):

* `INTERNET_NAME` – np. nowe domeny z reverse IP
* `IP_ADDRESS` – znalezione w skanach podsieci
* `NETBLOCK_OWNER` – właściciel bloku adresów
* `GEOINFO` – lokalizacja IP
* `WEBSERVER_BANNER` – nagłówki HTTP
* `RAW_RIR_DATA`, `WHOIS` – dane z WHOIS
* `AFFILIATE_INTERNET_NAME` – inne strony współdzielące infrastrukturę

---

### 🧠 Zastosowania:

* Mapowanie infrastruktury sieciowej i hostingu,
* Wykrywanie **powiązanych domen** i hostów (np. dla analizy phishingu),
* Zbieranie metadanych o serwerach, np. nagłówków HTTP,
* Analiza **rejestracji i właścicieli** domen i IP.

---

### 🔧 Wymagania i ograniczenia:

| Cecha      | Wartość                                                                                        |
| ---------- | ---------------------------------------------------------------------------------------------- |
| Moduł      | Aktywny (wysyła zapytania HTTP do HackerTarget)                                                |
| API Key    | Nie jest wymagany, ale **limit rate'ów** dla zapytań publicznych                               |
| Widoczność | Właściciel celu nie jest bezpośrednio informowany (zapytania idą do HackerTarget, nie do celu) |

---

- `sfp_company` to **moduł SpiderFoot**, którego celem jest **analiza i rozpoznanie firm (company intelligence)** związanych z analizowanym celem — najczęściej poprzez nazwę firmy, domenę lub powiązane dane WHOIS.

---

### 🔍 Co robi `sfp_company`?

* Wyszukuje i agreguje dane o firmach (organizacjach) na podstawie:

  * nazw domen (np. `example.com`),
  * danych z rekordów WHOIS (np. `Registrant Organization`),
  * adresów e-mail z firmową domeną,
  * oraz innych danych wygenerowanych wcześniej przez inne moduły.

* Na tej podstawie:

  * Tworzy encję `COMPANY`.
  * Próbuje **skorelować wszystkie znalezione dane** z konkretną organizacją.
  * Przypisuje wykryte elementy (domeny, e-maile, hosty, IP) do firmy.

---

### 📥 Dane wejściowe:

* `DOMAIN_NAME`
* `EMAILADDR`
* `WHOIS` (np. `ORG_NAME`, `REGISTRANT_NAME`)
* `INTERNET_NAME`
* `PHONE_NUMBER`
* `PHYSICAL_ADDRESS`

---

### 📤 Dane wyjściowe:

* `COMPANY` – nazwa firmy
* `RELATED_COMPANY` – jeśli wykryje powiązane organizacje (np. podmioty zależne)
* `AFFILIATE_COMPANY` – firma powiązana przez wspólną domenę, adres, itp.

---

### 🧠 Przykład zastosowania:

Jeśli analizujesz domenę `examplecorp.com`, a w WHOIS pojawia się `Example Corp Ltd`, to `sfp_company`:

1. Zidentyfikuje firmę jako `COMPANY: Example Corp Ltd`.
2. Przypisze inne domeny, adresy e-mail czy IP do tej firmy, jeśli znajdzie spójne dane (np. `john.doe@examplecorp.com`).
3. Może też wykryć inne domeny używane przez tę firmę, np. `examplecorp.net`, i przypisać je jako `AFFILIATE_INTERNET_NAME`.

---

### 🔧 Cecha:

| Cecha         | Opis                                          |
| ------------- | --------------------------------------------- |
| Typ modułu    | **Analityczny / Korelacyjny**                 |
| Źródła danych | Dane wewnętrzne + dane z WHOIS                |
| Tryb          | Pasywny – nie kontaktuje się z celem          |
| Wymaga danych | z innych modułów (np. WHOIS, e-maile, domeny) |

---

### 📌 Podsumowanie:

`sfp_company` **łączy rozproszone dane w profil organizacji**, co pomaga w OSINT, analizie zagrożeń, badaniach nad phishingiem, analizie powierzchni ataku itp.

---

- `sfp_crt` to **moduł SpiderFoot**, który pobiera dane z serwisu **[crt.sh](https://crt.sh)** — publicznego rejestru certyfikatów SSL/TLS — w celu odnalezienia **domen i subdomen** związanych z analizowanym celem.

---

### 🧩 Co robi `sfp_crt`?

* Wysyła zapytania do **crt.sh**, przeszukując **publiczne certyfikaty TLS** (głównie Let's Encrypt, Digicert, GlobalSign itp.).
* Wyciąga z nich:

  * **nazwy domen i subdomen** (np. `sub.example.com`, `mail.example.com`)
  * **organizacje** i inne dane zapisane w certyfikatach (np. Common Name, Subject Alternative Name).

---

### 📥 Dane wejściowe:

* `DOMAIN_NAME`
* `INTERNET_NAME` (domena lub subdomena)

---

### 📤 Dane wyjściowe:

* `INTERNET_NAME` – nowe subdomeny znalezione w certyfikatach
* `SSL_CERTIFICATE` – dane o certyfikacie
* `COMPANY` – jeśli certyfikat zawiera nazwę firmy
* `AFFILIATE_INTERNET_NAME` – inne domeny powiązane z certyfikatem

---

### 🧠 Przykład zastosowania:

Analizujesz `example.com`, a `sfp_crt` znajduje w certyfikatach:

* `vpn.example.com`
* `dev.example.com`
* `*.test.example.com`

To pomaga:

* **odkryć ukryte subdomeny**,
* rozpoznać środowiska testowe, stagingowe lub wewnętrzne,
* określić **powiązania organizacyjne** (np. jeśli ten sam certyfikat występuje w wielu domenach).

---

### 🔧 Cechy:

| Cecha      | Wartość                                          |
| ---------- | ------------------------------------------------ |
| Typ modułu | Pasywny (nie kontaktuje się z celem)             |
| Źródło     | crt.sh (bazuje na Certificate Transparency logs) |
| API Key    | Nie jest wymagany                                |
| Widoczność | Całkowicie anonimowy i pasywny                   |

---

### 📌 Dlaczego to ważne?

Moduł `sfp_crt` jest jednym z najskuteczniejszych narzędzi do **wykrywania subdomen**, ponieważ:

* certyfikaty SSL są publiczne i zawierają pełne FQDN,
* wiele firm automatycznie generuje wildcardy i certyfikaty dla środowisk developerskich.

---

- `sfp_whois` to **moduł SpiderFoot**, który służy do pobierania i analizowania danych **WHOIS** dla domen i adresów IP. Jest jednym z podstawowych modułów pasywnych używanych do **identyfikacji właściciela domeny, dat rejestracji oraz innych metadanych**.

---

### 🔍 Co robi `sfp_whois`?

* Wysyła zapytania WHOIS dla:

  * **domen** (np. `example.com`)
  * **adresów IP** i **bloków IP (netblocków)**

* Parsuje odpowiedzi, wyciągając m.in.:

  * nazwę właściciela domeny (`Registrant Name`, `Org Name`),
  * daty rejestracji, wygaśnięcia i modyfikacji,
  * dane kontaktowe (e-mail, telefon, adres fizyczny),
  * informacje o serwerach DNS,
  * ASN i właściciela sieci (dla IP).

---

### 📥 Dane wejściowe:

* `DOMAIN_NAME`
* `INTERNET_NAME`
* `IP_ADDRESS`
* `NETBLOCK`

---

### 📤 Dane wyjściowe:

* `WHOIS` – surowe dane WHOIS
* `EMAILADDR` – e-maile właścicieli lub adminów
* `PHONE_NUMBER` – numery telefonów z WHOIS
* `PHYSICAL_ADDRESS` – adresy fizyczne
* `COMPANY` – nazwa właściciela domeny/IP
* `REGISTRAR` – firma rejestrująca domenę
* `DOMAIN_REGISTRATION_DATE`, `DOMAIN_EXPIRATION_DATE`
* `NETBLOCK_OWNER` – dla IP i ASN
* `RAW_RIR_DATA` – dane z rejestrów IP (RIR)

---

### 🧠 Przykład:

Analizujesz `example.com`, a `sfp_whois` pobiera dane:

* Registrant: **Example Corp**
* E-mail: **[admin@example.com](mailto:admin@example.com)**
* Created: **2014-03-22**
* Registrar: **Namecheap**

Dzięki temu możesz:

* ustalić **właściciela** domeny lub IP,
* sprawdzić, czy domena jest **aktywnie zarządzana** (czy nie wygasa),
* znaleźć **punkty kontaktowe** (e-mail, tel),
* **powiązać domeny lub IP** z tą samą osobą/firmą.

---

### 🔧 Cechy:

| Cecha         | Opis                                                                                 |
| ------------- | ------------------------------------------------------------------------------------ |
| Rodzaj modułu | **Pasywny**                                                                          |
| Widoczność    | Zapytania WHOIS nie są widoczne dla właściciela domeny                               |
| API           | Można używać z zewnętrznymi usługami WHOIS (np. WHOISXMLAPI) – opcjonalnie z API key |
| Obsługuje     | IPv4, IPv6, domeny                                                                   |

---

### 📌 Uwaga:

W związku z **RODO i politykami prywatności WHOIS**, dane kontaktowe mogą być ukryte (np. przez usługę ochrony prywatności domeny), ale `sfp_whois` i tak potrafi wydobyć wiele wartościowych informacji technicznych i organizacyjnych.

---

- `sfp_spider` to **moduł SpiderFoot** odpowiedzialny za **aktywny crawling (pełzanie) stron internetowych** — czyli **przeglądanie i analizowanie zawartości stron WWW** powiązanych z celem, podobnie jak robią to roboty Google’a czy innych wyszukiwarek.

---

### 🕸️ Co dokładnie robi `sfp_spider`?

* Odwiedza stronę główną celu (np. `example.com`) i **pobiera jej zawartość HTML**.
* Analizuje tę zawartość w poszukiwaniu:

  * linków do innych podstron,
  * **adresów e-mail**,
  * **adresów IP**, nazw domen,
  * **loginów**, **tokenów**, numerów telefonów itp.
* Może następnie **rekursywnie przeglądać kolejne podstrony** (zależnie od ustawień głębokości crawlowania).
* Wyszukuje **słowa kluczowe**, np. "admin", "login", "internal", itp., co może sugerować wewnętrzne zasoby.

---

### 📥 Dane wejściowe:

* `INTERNET_NAME` – domeny, subdomeny
* `URL` – konkretne adresy stron

---

### 📤 Dane wyjściowe:

* `EMAILADDR` – e-maile znalezione na stronie
* `URL` – linki do innych podstron
* `INTERNET_NAME` – nowe domeny, hosty
* `PHONE_NUMBER` – numery telefonów
* `SOCIAL_MEDIA` – linki do profili społecznościowych
* `CREDENTIALS` – możliwe dane logowania (np. w plikach `.env`, `.git`, backupach)
* `LEAKSITE_URL` – jeśli wykryto coś potencjalnie wrażliwego
* `RAW_CONTENT` – oryginalna zawartość strony

---

### 🔧 Główne cechy:

| Cecha            | Wartość                                                                |
| ---------------- | ---------------------------------------------------------------------- |
| Tryb działania   | **Aktywny** (odwiedza cel!)                                            |
| Widoczność       | **Tak** – właściciel celu może zauważyć ruch                           |
| Konfigurowalność | Tak – można ustawić maksymalną głębokość, ilość URL-i, user-agent itp. |
| Obsługa JS       | Nie – to klasyczny crawler, nie obsługuje dynamicznych treści JS       |
| Zachowanie       | Zgodne z `robots.txt` (domyślnie)                                      |

---

### ⚠️ Ostrzeżenie:

Moduł `sfp_spider` **nie jest anonimowy** – może ujawniać Twoje IP i user-agent właścicielowi strony. Nie powinien być używany do crawlowania celów bez zgody, jeśli zależy Ci na dyskrecji (np. w dochodzeniu OSINT lub pentestach bez autoryzacji).

---

### 🧠 Przykład użycia:

Analizując `targetcorp.com`, `sfp_spider` może znaleźć:

* ukryte subdomeny jak `admin.targetcorp.com`,
* adresy e-mail pracowników,
* link do panelu logowania (`/login.php`),
* pozostałości po backupach (`/db.sql.bak`, `/.git/`),
* treści HTML zawierające słowa kluczowe typu "confidential", "internal use only".

---

- `sfp_searchcode` to **moduł SpiderFoot**, który wykorzystuje serwis [**Searchcode.com**](https://searchcode.com/) do przeszukiwania publicznie dostępnego **kodu źródłowego**, skryptów i repozytoriów w celu wykrycia informacji związanych z analizowanym celem – najczęściej domeną, nazwą firmy, adresem e-mail itp.

---

### 🔍 Co robi `sfp_searchcode`?

* Wysyła zapytania do serwisu **Searchcode**, który indeksuje otwarty kod z:

  * publicznych repozytoriów (np. GitHub, Bitbucket, SourceForge),
  * plików konfiguracyjnych, `.env`, `.xml`, `.ini`,
  * skryptów w wielu językach programowania.

* Szuka m.in.:

  * **domen i subdomen**,
  * **adresów e-mail**, tokenów API, kluczy, haseł,
  * loginów użytkowników,
  * nazw firm i projektów,
  * wycieków danych konfiguracyjnych.

---

### 📥 Dane wejściowe:

* `DOMAIN_NAME`
* `INTERNET_NAME`
* `EMAILADDR`
* `USERNAME`
* `COMPANY`

---

### 📤 Dane wyjściowe:

* `LEAKSITE_URL` – linki do potencjalnie wyciekłych danych
* `CREDENTIALS` – wykryte hasła, tokeny itp.
* `EMAILADDR` – e-maile w kodzie
* `RAW_DATA` – surowe fragmenty kodu zawierające znalezione dane
* `INTERNET_NAME` – domeny i hosty wykryte w kodzie
* `AFFILIATE_INTERNET_NAME` – inne domeny użyte w kodzie, np. domeny testowe
* `SOURCE_CODE_URL` – repozytoria, w których znaleziono dane

---

### 🧠 Przykład użycia:

Dla domeny `examplecorp.com` moduł może znaleźć:

* skrypt `.env` w publicznym repozytorium zawierający:

  ```env
  SMTP_USER=support@examplecorp.com
  SMTP_PASS=supersecret123
  ```

* albo plik `.py` zawierający:

  ```python
  API_KEY = "AKIAIOSFODNN7EXAMPLE"
  ```

---

### 🔧 Cechy:

| Cecha          | Wartość                                                 |
| -------------- | ------------------------------------------------------- |
| Tryb działania | **Pasywny**                                             |
| Widoczność     | Nie – zapytania są kierowane do Searchcode, nie do celu |
| API Key        | Nie wymagany                                            |
| Zastosowanie   | OSINT, wykrywanie wycieków w kodzie źródłowym           |

---

### 📌 Dlaczego to ważne?

* Pomaga znaleźć **nieświadome wycieki danych** w publicznych repozytoriach.
* Może dostarczyć **danych uwierzytelniających**, dostępów do API, e-maili technicznych.
* Idealny do analizy własnych firm lub partnerów pod kątem bezpieczeństwa kodu.

---

- `sfp_bgpview` to **moduł SpiderFoot**, który wykorzystuje publiczne dane z serwisu [**BGPView.io**](https://bgpview.io) do zbierania informacji o **adresach IP, ASN (Autonomous System Numbers) i netblockach** związanych z analizowanym celem – najczęściej domeną lub adresem IP.

---

### 🌐 Co to jest BGPView?

**BGPView\.io** udostępnia dane routingowe z systemu BGP (Border Gateway Protocol), który zarządza globalnym ruchem internetowym. Dzięki temu można:

* dowiedzieć się, **który operator sieci (ISP)** odpowiada za dany IP,
* sprawdzić, **jaki blok adresów (netblock)** jest przypisany do IP,
* zidentyfikować **ASN i jego właściciela**.

---

### 🔍 Co robi `sfp_bgpview`?

* Dla danego **adresu IP** lub **ASN** pobiera:

  * przypisany numer ASN,
  * właściciela ASN (np. firma, uczelnia, operator),
  * pełny zakres IP (netblock),
  * powiązane IP, domeny, peerings i lokalizacje.

---

### 📥 Dane wejściowe:

* `IP_ADDRESS`
* `NETBLOCK`
* `DOMAIN_NAME` (pośrednio, gdy inne moduły znajdą IP)

---

### 📤 Dane wyjściowe:

* `ASN` – numer systemu autonomicznego
* `NETBLOCK_OWNER` – właściciel netblocka lub AS
* `NETBLOCK` – cały zakres adresów IP
* `RAW_RIR_DATA` – dane z Regional Internet Registry (np. RIPE, ARIN)
* `PHYSICAL_ADDRESS` – adres firmy zarządzającej siecią
* `COMPANY` – jeśli znany właściciel

---

### 🧠 Przykład:

Dla IP `8.8.8.8` (Google DNS) `sfp_bgpview` może zwrócić:

* ASN: **15169**
* Właściciel: **Google LLC**
* Netblock: **8.8.8.0/24**
* Lokalizacja: **USA**
* Inne IP w tym netblocku

---

### 🔧 Cechy:

| Cecha           | Wartość                                                       |
| --------------- | ------------------------------------------------------------- |
| Tryb działania  | **Pasywny**                                                   |
| Widoczność      | Nie – działa przez zewnętrzne API, nie kontaktuje się z celem |
| Wymaga API Key? | **Nie**                                                       |
| Szybkość        | Szybki i niezawodny                                           |
| Źródło danych   | bgpview\.io (dane z BGP i RIR)                                |

---

### 📌 Do czego to przydatne?

* **Identyfikacja operatora IP** – kto zarządza infrastrukturą?
* **Powiązania organizacyjne** – różne IP z tej samej klasy mogą należeć do tej samej firmy.
* **Analiza powierzchni ataku** – odkrycie dodatkowych IP w netblocku.
* **Geolokalizacja i analiza ryzyka** – np. czy IP należy do VPS w Rosji, Chinach, USA itp.

---

`sfp_ripe` to **moduł SpiderFoot**, który pobiera dane z rejestru **RIPE** (Réseaux IP Européens) – głównego Regional Internet Registry (RIR) dla Europy, Bliskiego Wschodu i części Azji. Umożliwia identyfikację właścicieli adresów IP, netblocków i systemów autonomicznych (ASN) na podstawie oficjalnych danych RIPE NCC.

---

### 🌍 Co to jest RIPE?

**RIPE** zarządza przydziałem adresów IP (IPv4 i IPv6) oraz numerów ASN w regionie EMEA. Ich baza danych zawiera szczegółowe informacje o:

* Właścicielach netblocków,
* Kontaktach technicznych i administracyjnych,
* Lokalizacji IP,
* Organizacjach zarządzających zasobami sieciowymi.

---

### 🔍 Co robi `sfp_ripe`?

* Wysyła zapytania do bazy danych [**RIPE DB**](https://www.ripe.net/) przez publiczne API.
* Odczytuje informacje o:

  * **IP**, **NETBLOCKACH** (np. `192.0.2.0/24`)
  * **ASN** (numery systemów autonomicznych)
  * właścicielu, organizacji, adresie fizycznym, osobach kontaktowych.

---

### 📥 Dane wejściowe:

* `IP_ADDRESS`
* `NETBLOCK`
* `ASN`

---

### 📤 Dane wyjściowe:

* `NETBLOCK_OWNER` – właściciel bloku adresów IP
* `PHYSICAL_ADDRESS` – adres organizacji
* `COMPANY` – nazwa właściciela
* `PHONE_NUMBER`, `EMAILADDR` – dane kontaktowe (jeśli dostępne)
* `RAW_RIR_DATA` – pełne dane z RIPE

---

### 🧠 Przykład:

Dla IP `193.0.6.135` moduł może znaleźć:

* Właściciel: **RIPE NCC**
* Adres: **Stationsplein 11, Amsterdam**
* Netblock: `193.0.0.0/21`
* ASN: `3333`
* Kontakt: [ripe-dbm@ripe.net](mailto:ripe-dbm@ripe.net)

---

### 🔧 Cechy:

| Cecha            | Wartość                                   |
| ---------------- | ----------------------------------------- |
| Tryb działania   | **Pasywny**                               |
| Widoczność       | Nie – zapytania do bazy RIPE, nie do celu |
| API Key          | **Nie wymagany**                          |
| Region działania | Europa, Bliski Wschód, część Azji         |
| Pokrycie         | IPv4, IPv6, ASN                           |

---

### 📌 Po co to stosować?

* Do **identyfikacji właścicieli IP/netblocków** w Europie i sąsiednich regionach.
* Pomaga zrozumieć, kto zarządza danym serwerem/IP.
* Przydaje się przy analizie **domen hostowanych w Europie**, wykrywaniu **podejrzanej infrastruktury** i mapowaniu powierzchni ataku.

---

- `sfp_strangeheaders` to **moduł SpiderFoot**, który analizuje **nagłówki HTTP** zwrócone przez serwery WWW celu (np. `example.com`) i wykrywa **nietypowe lub potencjalnie podejrzane nagłówki**, które mogą wskazywać na błędną konfigurację, wycieki informacji lub niestandardowe technologie.

---

### 📦 Co robi `sfp_strangeheaders`?

Moduł:

* Wysyła żądania HTTP (GET/HEAD) do celów (np. subdomen).
* Zbiera nagłówki HTTP z odpowiedzi serwera, np.:

  * `Server`, `X-Powered-By`, `X-AspNet-Version`, `X-Amz-Cf-Id`, `Set-Cookie`, `Via`, `X-Backend-Server`, itp.
* Analizuje je pod kątem:

  * **nietypowości** – nagłówki niestandardowe, rzadko spotykane,
  * **potencjalnych wycieków informacji** – np. nazwa używanej technologii, adresy wewnętrzne, ID sesji,
  * **niebezpiecznych konfiguracji** – np. brak `X-Frame-Options`, `Strict-Transport-Security`.

---

### 📥 Dane wejściowe:

* `INTERNET_NAME` – nazwy hostów
* `IP_ADDRESS` – adresy IP serwerów HTTP/HTTPS
* `URL` – konkretne adresy stron

---

### 📤 Dane wyjściowe:

* `WEBSERVER_BANNER` – identyfikacja serwera HTTP (np. Apache/2.4.29)
* `WEBSERVER_TECHNOLOGY` – technologie z nagłówków (np. PHP/7.4, Express.js)
* `RAW_DATA` – zrzut nagłówków
* `LEAKSITE_URL` – jeśli wykryto coś, co może prowadzić do wycieku informacji

---

### 🧠 Przykład:

Dla domeny `dev.insecure.com` serwer może zwrócić nagłówki:

```
Server: Apache/2.4.10 (Debian)
X-Powered-By: PHP/5.6.40
X-Internal-Host: internal-dev.insecure.com
```

Moduł rozpozna:

* **Stary PHP** → możliwe zagrożenie,
* `X-Internal-Host` → potencjalny **wyciek infrastruktury**,
* `X-Powered-By` → ujawnienie technologii (PHP 5.6),
* brak `Content-Security-Policy` → luka w konfiguracji bezpieczeństwa.

---

### 🔧 Cechy:

| Cecha          | Wartość                                    |
| -------------- | ------------------------------------------ |
| Tryb działania | **Aktywny**                                |
| Widoczność     | Tak – serwer zobaczy zapytanie HTTP        |
| API Key        | Niepotrzebny                               |
| Protokół       | HTTP / HTTPS                               |
| Analiza        | Głównie nagłówki HTTP z odpowiedzi serwera |

---

### 📌 Po co to używać?

* **Rozpoznanie technologii backendu** (np. Express, ASP.NET, Nginx, Tomcat).
* Wykrywanie **błędów w konfiguracji HTTP/Security**.
* Identyfikacja **wewnętrznych komponentów**, np. load balancerów, serwerów aplikacyjnych.
* Pomaga w **mapowaniu infrastruktury** i **analizie ryzyka**.

---

`sfp_portscan_tcp` to **moduł aktywnego skanowania portów TCP** w SpiderFoot. Umożliwia wykrycie **otwartych usług sieciowych** (np. HTTP, FTP, SSH) na danym hoście lub adresie IP poprzez wysyłanie rzeczywistych pakietów TCP.

---

### 🔍 Co robi `sfp_portscan_tcp`?

* Skanuje wybrany zakres portów TCP na celach (adresach IP, hostach).
* Ustalanie, które porty są **otwarte, filtrowane lub zamknięte**.
* Może identyfikować typy usług, jeśli baner serwera jest dostępny (np. `SSH-2.0-OpenSSH_7.4`).
* Wspiera proste rozpoznawanie usług, ale nie wykonuje pełnej identyfikacji jak np. Nmap z opcją `-sV`.

---

### 📥 Dane wejściowe:

* `IP_ADDRESS`
* `INTERNET_NAME` (np. `host.example.com`)

---

### 📤 Dane wyjściowe:

* `TCP_PORT_OPEN` – numer otwartego portu (np. `22`, `80`, `443`)
* `WEBSERVER_BANNER` – jeśli znaleziono baner HTTP/S
* `BANNER` – surowa informacja zwrócona przez usługę (np. SMTP, SSH)
* `RAW_DATA` – szczegóły skanu

---

### 🧠 Przykład:

Dla IP `203.0.113.5` moduł może wykryć:

| Port | Usługa | Wynik        |
| ---- | ------ | ------------ |
| 22   | SSH    | Open         |
| 80   | HTTP   | Open         |
| 443  | HTTPS  | Open         |
| 3306 | MySQL  | **Filtered** |

---

### ⚠️ Ważne:

* **To jest skan aktywny** – cel może zauważyć, że jest skanowany (np. w logach, firewallu).
* Może być **postrzegany jako atak rozpoznawczy**, szczególnie jeśli skanujesz duży zakres portów lub wiele hostów.
* **Nie używaj bez zgody**, jeśli nie masz uprawnień do testowania danego systemu.

---

### 🔧 Parametry konfiguracyjne (w GUI SpiderFoot):

* **Port range** – np. `1-1024`, `80,443,8080`
* **Timeout** – czas oczekiwania na odpowiedź (domyślnie kilka sekund)
* **Max threads** – liczba równoległych połączeń (uwaga na DoS!)
* **Scan depth** – jak dokładnie skanować (np. tylko „well-known ports”)

---

### 📌 Po co używać `sfp_portscan_tcp`?

* Do **mapowania usług** wystawionych na zewnątrz (np. serwer WWW, SSH, RDP).
* Do wykrywania **błędnych konfiguracji** (np. otwarty MySQL bez hasła).
* W analizie powierzchni ataku – co można osiągnąć przez dostępne porty?
* Uzupełnienie pasywnego OSINT (np. z Shodan), kiedy potrzebne są dane z pierwszej ręki.

---

- `sfp_keybase` to moduł **SpiderFoot**, który integruje się z platformą [**Keybase.io**](https://keybase.io) w celu wyszukiwania **tożsamości powiązanych z adresem e-mail, nazwą użytkownika lub domeną**. Wykorzystuje dane publiczne dostępne w Keybase, aby znaleźć powiązania między osobami, usługami online i kluczami kryptograficznymi.

---

### 🔍 Co robi `sfp_keybase`?

* Szuka użytkowników **Keybase**, którzy:

  * używają danego adresu e-mail,
  * mają podaną daną nazwę użytkownika,
  * powiązali się z określoną domeną (np. poprzez podpisaną tożsamość).

* Zbiera dane z profilu Keybase, takie jak:

  * imię i nazwisko (jeśli podano),
  * publiczny klucz PGP,
  * powiązane konta (np. GitHub, Twitter, Reddit),
  * linki do stron WWW,
  * zdjęcie profilowe.

---

### 📥 Dane wejściowe:

* `EMAILADDR` – adres e-mail
* `USERNAME` – login/nazwa użytkownika
* `DOMAIN_NAME` – opcjonalnie, jeśli używana w profilach Keybase

---

### 📤 Dane wyjściowe:

* `SOCIAL_MEDIA` – konta powiązane (np. GitHub, Twitter)
* `PGP_KEY` – publiczny klucz PGP
* `LINKED_URL` – strony powiązane z użytkownikiem
* `HUMAN_NAME` – imię i nazwisko
* `RAW_DATA` – szczegóły z API Keybase
* `EMAILADDR`, `USERNAME`, `DOMAIN_NAME` – jeśli powiązane z profilem

---

### 🧠 Przykład:

Dla e-maila `jan.kowalski@example.com` może znaleźć użytkownika Keybase:

* username: `jankowalski`
* linked: GitHub `jankowalski-dev`, Twitter `@kowalski_jan`
* public key: `PGP 0xDEADBEEF`
* strona: `https://jankowalski.dev`

---

### 🔧 Cechy:

| Cecha          | Wartość                                     |
| -------------- | ------------------------------------------- |
| Tryb działania | **Pasywny**                                 |
| Widoczność     | Nie – zapytania są kierowane do API Keybase |
| API Key        | **Niepotrzebny** (dane publiczne)           |
| Typ danych     | Tożsamości cyfrowe, konta, klucze           |
| Bezpieczny     | Tak, brak aktywnego kontaktu z celem        |

---

### 📌 Po co używać?

* **Łączenie tożsamości cyfrowych** na podstawie adresu e-mail lub loginu.
* Wyszukiwanie **konta GitHub lub Twitter**, których ktoś używa.
* Znajdowanie **powiązań personalnych**, np. między domeną a osobą.
* **Zbieranie kluczy PGP**, jeśli chcesz skontaktować się z kimś zaszyfrowanym kanałem.

---

- `sfp_pageinfo` to moduł SpiderFoot, który analizuje zawartość i metadane stron internetowych (HTML) danej domeny lub URL, aby wyciągnąć przydatne informacje o stronie.

---

### 🔍 Co robi `sfp_pageinfo`?

* Pobiera zawartość strony internetowej (HTML).
* Analizuje metadane takie jak:

  * tytuł strony (`<title>`),
  * opisy (`<meta name="description">`),
  * słowa kluczowe (`<meta name="keywords">`),
  * nagłówki (H1, H2, itp.),
  * linki wewnętrzne i zewnętrzne,
  * język strony,
  * inne metatagi (np. `robots`, `author`).
* Wykrywa technologie i CMS na podstawie treści strony.
* Może zbierać informacje o kontakcie, adresach e-mail i telefonach znalezionych w treści.

---

### 📥 Dane wejściowe:

* `URL`
* `INTERNET_NAME` (np. domena)

---

### 📤 Dane wyjściowe:

* `TITLE` – tytuł strony
* `DESCRIPTION` – meta opis
* `KEYWORDS` – meta słowa kluczowe
* `LANGUAGE` – język strony
* `HEADERS` – nagłówki H1, H2 itd.
* `LINKS_INTERNAL` – linki do tej samej domeny
* `LINKS_EXTERNAL` – linki do innych domen
* `EMAILADDR` – znalezione adresy e-mail
* `PHONE_NUMBER` – znalezione numery telefonów
* `CMS` – wykryty system zarządzania treścią (np. WordPress)

---

### 🧠 Przykład:

Dla `https://example.com` moduł może wyciągnąć:

* Tytuł: "Example Domain"
* Opis: "This domain is for use in illustrative examples in documents."
* Język: "en"
* Linki: `https://www.iana.org/domains/example`

---

### 🔧 Cechy:

| Cecha          | Wartość                           |
| -------------- | --------------------------------- |
| Tryb działania | Aktywny (pobieranie stron)        |
| Widoczność     | Tak – serwer strony widzi żądanie |
| API Key        | Niepotrzebny                      |
| Protokół       | HTTP / HTTPS                      |

---

### 📌 Do czego służy?

* Szybka analiza zawartości strony i metadanych.
* Pomoc w ocenie jakości strony i jej celu.
* Wykrywanie technologii i CMS.
* Zbieranie danych kontaktowych dostępnych publicznie.
* Budowanie profilu OSINT na temat witryny.

---

- `sfp_webframework` to moduł SpiderFoot, który służy do **identyfikacji technologii i frameworków webowych** używanych przez daną stronę internetową lub serwer [WWW](http://WWW).

---

### 🔍 Co robi `sfo_webframework`?

* Analizuje różne elementy strony, takie jak:

  * nagłówki HTTP,
  * strukturę HTML,
  * pliki JavaScript,
  * cookies,
  * wzorce URL,
  * specyficzne sygnatury w odpowiedziach serwera,

  aby wykryć, czy dana strona używa popularnych frameworków webowych, np.:

  * **Django**
  * **Ruby on Rails**
  * **Laravel**
  * **Express.js**
  * **ASP.NET**
  * **Angular**
  * **React**
  * **Vue.js**

* Ułatwia rozpoznanie technologii backendu i frontendowych bibliotek.

---

### 📥 Dane wejściowe:

* `URL`
* `INTERNET_NAME`

---

### 📤 Dane wyjściowe:

* `WEB_FRAMEWORK` – nazwa wykrytego frameworka lub technologii
* `WEB_FRAMEWORK_VERSION` – jeśli wykryto wersję
* `RAW_DATA` – szczegóły wykrycia (np. nagłówki, wzorce)

---

### 🧠 Przykład:

Dla strony `example.com` moduł może wykryć:

* Framework: **Django**
* Wersja: **3.2**
* Wzorce: np. obecność cookie `csrftoken`, nagłówek `X-Frame-Options`

---

### 🔧 Cechy:

| Cecha               | Wartość                             |
| ------------------- | ----------------------------------- |
| Tryb działania      | Aktywny                             |
| Widoczność          | Tak – generuje zapytania do serwera |
| API Key             | Niepotrzebny                        |
| Techniki wykrywania | Analiza HTTP, HTML, JS, cookies     |

---

### 📌 Po co używać?

* Poznanie technologii używanej przez cel.
* Przydatne w testach bezpieczeństwa (np. wykrycie podatności specyficznych dla frameworka).
* Pomaga w planowaniu dalszej analizy i ataków.
* Ułatwia zrozumienie struktury i architektury aplikacji webowej.

---

# Pozostałe

- `recon-ng`
- `recon-web` [uruchamia stronę na porcie 5000]
- `workspace create`
- `workspaces load`
- `back`
- `recon-ng-marketplace`
- `marketplace install`
- `modules load`
- `options set source websitename`
- `run`
- `info`
- `dasboard`