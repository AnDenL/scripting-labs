# Лабораторна робота №2: Розробка консольних утиліт для задач кібербезпеки

## Варіант №11: Аудитор ARP-таблиць та виявлення ARP-Spoofing

Утиліта для аналізу зліпків ARP-кешу мережевих пристроїв, валідації синтаксису мережевих адрес (IPv4 та MAC) та виявлення дублювання MAC-адрес (ознака ARP-spoofing / Man-in-the-Middle атак).

---

## 1. Встановлення залежностей

Усі модулі проєкту (крім лінтера) базуються виключно на стандартній бібліотеці Python 3.14.
Для статичного аналізу коду використовується `ruff` який був вбудований в IDE і не скачувався окремо як залежність.

## 2. Структура файлів
```
labs/lab02/
├── __init__.py
├── main.py 
├── task1.py 
├── task2.py
├── README.md
└── data/(в .gitignore)
    ├── arp_table.csv
    ├── log.txt
    └── output.json
```
## 3. Запуск демо
### Завдання 1:
```bash
python -m labs.lab2.main demo
```
### Завдання 2:

**Опис параметрів CLI**

--arp-file=<path> (обов'язковий): шлях до вхідного файлу ARP-таблиці у форматі CSV/текст.

--detect-spoofing (прапорець): вмикає режим пошуку дубльованих MAC-адрес (виявлення Man-in-the-Middle аномалій).

--log-file=<path> (опціональний): шлях до файлу для збереження журналу подій безпеки (INFO, WARNING, CRITICAL).

--output-json=<path> (опціональний): шлях до файлу експорту виявлених інцидентів у форматі JSON.

Без флагів:
```bash
python -m labs.lab2.task2 --arp-file=шлях_до_arp_table.csv
```
Повний аналіз:
```bash
python -m labs.lab2.task2 --arp-file=шлях_до_arp_table.csv --detect-spoofing --log-file=шлях_до_log.txt --output-json=шлях_до_output.json
```

### Приклад застосування

Застосування на такій таблиці з vns:
```
IP Address,MAC Address,Interface,Type
192.168.1.1,00:11:22:33:44:55,eth0,dynamic
192.168.1.10,AA:BB:CC:DD:EE:01,eth0,dynamic
192.168.1.11,AA:BB:CC:DD:EE:02,eth0,dynamic
192.168.1.12,AA:BB:CC:DD:EE:03,eth0,static
192.168.1.20,DE:AD:BE:EF:00:01,eth0,dynamic
192.168.1.21,DE:AD:BE:EF:00:01,eth0,dynamic
192.168.1.22,DE:AD:BE:EF:00:01,wlan0,dynamic
10.0.0.5,12:34:56:78:9A:BC,eth1,dynamic
999.168.1.30,AA:BB:CC:DD:EE:30,eth0,dynamic
192.168.1.31,GG:11:22:33:44:55,eth0,dynamic
192.168.1.32,0011.2233.4455,eth0,dynamic
```
Команда:
```zsh
Scripting Labs on  main via 🐍 v3.14.7 (.venv)
❯ python -m labs.lab2.task2 --arp-file=labs/lab2/data/arp_table.csv --detect-spoofing --log-file=labs/lab2/data/log.txt --output-json=labs/lab2/data/output.json
```
Результат:
```
Parsing ARP table from labs/lab2/data/arp_table.csv
Validated 12 IP/MAC entries.

=== Validated Entries Summary ===
Valid IP/MAC Pairs : 8
Invalid Syntax     : 3

=== CRITICAL SECURITY ALERTS: ARP-SPOOFING DETECTED ===
[ALERT] MAC Address Duplicate Conflict!

MAC Address: de:ad:be:ef:00:01 associated with MULTIPLE IP addresses: 192.168.1.20 (eth0/dynamic), 192.168.1.21 (eth0/dynamic), 192.168.1.22 (wlan0/dynamic)
    - 192.168.1.20
    - 192.168.1.21
    - 192.168.1.22
    -> POSSIBLE MAN-IN-THE-MIDDLE / ARP-SPOOFING ATTACK IN PROGRESS!
[INFO] Security alerts exported to labs/lab2/data/output.json
```

### Поведінка при помилках

1. Відсутність або некоректний шлях до файлу (--arp-file):
Програма виводить повідомлення File not found: '<шлях>' і штатно завершує роботу з нульовим статусом без падіння трасування стеку.

2. Некоректний синтаксис адрес (биті рядки в CSV):
    * Якщо октет IP виходить за межі 0–255 або адреса не відповідає масці IPv4 — запис відкидається, додається до списку invalid_ips та фіксується як [WARNING] у лог-файл.
    
    * Якщо MAC-адреса містить нешістнадцяткові символи або має некоректний формат розділювачів — запис додається до списку invalid_macs та фіксується як [WARNING].
    
    * Загальна кількість невалідних записів виводиться в консолі у блоці Invalid Syntax.
