Polecenia i ich zastosowania:

---

## 🧭 1. Uruchomienie Wiresharka (interfejs graficzny)

```bash
wireshark
```

lub z określonym interfejsem:

```bash
sudo wireshark -i eth0
```

> 🔹 Uruchamia graficzny interfejs Wiresharka i od razu otwiera kartę z przechwytywaniem z interfejsu `eth0`.

---

## 🧰 2. Tryb tekstowy – `tshark`

Wireshark ma konsolowy odpowiednik: **tshark**
To narzędzie wiersza poleceń, które używa tego samego silnika co Wireshark, ale bez GUI.

### Najczęstsze polecenia `tshark`:

#### 🔹 Lista dostępnych interfejsów:

```bash
tshark -D
```

#### 🔹 Przechwytywanie pakietów z interfejsu:

```bash
sudo tshark -i eth0
```

#### 🔹 Zapisywanie przechwyconych pakietów do pliku:

```bash
sudo tshark -i eth0 -w capture.pcap
```

#### 🔹 Wczytanie pliku `.pcap` i analiza w terminalu:

```bash
tshark -r capture.pcap
```

#### 🔹 Filtrowanie przechwytywanych pakietów (np. tylko HTTP):

```bash
sudo tshark -i eth0 -f "tcp port 80"
```

#### 🔹 Wyświetlanie tylko wybranych pól (np. adres źródłowy i docelowy):

```bash
tshark -r capture.pcap -T fields -e ip.src -e ip.dst
```

#### 🔹 Limit liczby pakietów:

```bash
sudo tshark -i eth0 -c 100
```

---

## 🧩 3. Przydatne opcje (zarówno `wireshark`, jak i `tshark`)

| Opcja            | Znaczenie                                |
| ---------------- | ---------------------------------------- |
| `-i <iface>`     | Wybór interfejsu (np. `eth0`, `wlan0`)   |
| `-f "<filter>"`  | Filtr BPF (np. `"tcp port 443"`)         |
| `-r <plik.pcap>` | Wczytaj plik do analizy                  |
| `-w <plik.pcap>` | Zapisz przechwytywanie do pliku          |
| `-c <n>`         | Przechwyć tylko n pakietów               |
| `-V`             | Szczegółowe informacje o każdym pakiecie |

---

## 📦 Przykładowe zastosowania

🔹 **Uruchomienie Wiresharka GUI na konkretnym pliku:**

```bash
wireshark packetdump.pcap &
```

🔹 **Podgląd 10 pierwszych HTTP pakietów w terminalu:**

```bash
sudo tshark -i eth0 -f "tcp port 80" -c 10
```

🔹 **Analiza istniejącego pliku bez GUI:**

```bash
tshark -r packetdump.pcap | less
```

---

Jeśli chcesz, mogę Ci pokazać **praktyczny mini-scenariusz** (np. przechwytywanie HTTP, filtrowanie po IP i analiza w terminalu krok po kroku) — chcesz taki przykład?
