# Waze Data Aggregator To One File  (example JMK)

Tento Python skript spracováva JSON výstupy z Waze feedu pre oblasť **Juhomoravského kraja (JMK)** a konsoliduje údaje o **dopravných upozorneniach (alerts)** a **zápchach (jams)**.

---

## Funkcionalita

- Načíta všetky súbory z priečinka `data_JMK/`, ktoré obsahujú timestamp v názve.
- Pre každú `alert` a `jam`:
  - detekuje nové, pokračujúce alebo zaniknuté udalosti.
  - vypočíta agregované hodnoty (`avg`, `max`, `min`) podľa typu atribútu.
- Vyhľadáva časové medzery (> 1 hodina) medzi súbormi a na ich základe označuje `alerts` a `jams` ako ukončené.
- Výstupy obsahujú len údaje pre mesto **Brno**.
- Zaznamenáva všetky zmeny do log súboru `loading_data_to_one_file.log`.

---

##  Štruktúra priečinkov

```
.
├── data_JMK/               # Vstupné Waze JSON súbory - Priklad
├── outputs_full/          # Výstupy po spracovaní
├── loading_data_to_one_file.log         # Log aktualizácií
├── data_aggregator_to_one_file.py       # Hlavný skript
└── README.md               # Tento popis
```

---

## ️ Požiadavky

- Python 3.9 alebo vyšší
- Nainštalované knižnice:
  - `pandas`

Inštalácia:

```bash
pip install pandas
```

---

## Spustenie

1. Skopíruj vstupné súbory do `data_JMK/`.
2. Spusti skript:

```bash
python data_aggregator_to_one_file.py
```

3. Skript vygeneruje:
   - `outputs_full/alerts_full.json`
   - `outputs_full/jams_full.json`
   - `loading_data_to_one_file.log`

---

## Výstupné dáta

### `alerts_full.json`

Každý alert (napr. nehoda, uzávierka) obsahuje:

- Identifikáciu: `uuid`, `type`, `subtype`, `reportDescription`
- Lokalitu: `city`, `street`, `location`, `country`
- Metadáta: `confidence`, `reliability`, `pubMillis`, `lastupdated`, `finished`

| Pole                   | Spracovanie                      |
|------------------------|----------------------------------|
| `uuid`                 | nemení sa                        |
| `country`, `city`      | posledná známa hodnota           |
| `type`, `subtype`      | posledná hodnota                 |
| `reportDescription`    | posledná hodnota                 |
| `street`               | posledná hodnota                 |
| `reportRating`         | maximum                          |
| `confidence`           | maximum                          |
| `reliability`          | maximum                          |
| `roadType`, `magvar`   | posledná hodnota                 |
| `reportByMunicipalityUser` | nemení sa                  |
| `location`             | posledná hodnota                 |
| `pubMillis`            | nemení sa                        |
| `lastupdated`          | posledný výskyt                  |
| `finished`             | nastaví sa, keď zmizne zo zdroja |

---

###  `jams_full.json`

Zápchy zahŕňajú okrem identifikátorov aj dynamické metriky (rýchlosť, dĺžka, zdržanie) s výpočtom priemerov.

| Pole                   | Spracovanie                            |
|------------------------|----------------------------------------|
| `id`, `uuid`           | nemení sa                              |
| `country`, `city`      | nemení sa                              |
| `turnType`             | nemení sa                              |
| `line`                 | najdlhší zo všetkých výskytov          |
| `segments`             | pridávajú sa nové segmenty             |
| `startNode`, `endNode` | posledná známa hodnota                 |
| `blockingAlertUuid`    | posledná hodnota                       |
| `roadType`             | posledná hodnota                       |
| `street`               | posledná hodnota                       |
| `level`                | maximum, priemer (avg)                 |
| `speedKMH`             | minimum, priemer (avg)                 |
| `length`               | maximum, priemer (avg)                 |
| `speed`                | maximum, priemer (avg)                 |
| `delay`                | maximum, priemer (avg)                 |
| `pubMillis`            | nemení sa                              |
| `lastupdated`          | posledný výskyt                        |
| `finished`             | nastaví sa, keď zápcha zmizne          |
| `updateCount`          | počet zaznamenaných výskytov           |

---

##  Ako to funguje?

1. Skript načíta súbor (napr. `data_JMK_2023-07-04_14-00-00.json`) a určí čas.
2. Pre každý alert/jam identifikuje, či:
   - je nový → uloží ako nový záznam,
   - už existuje → aktualizuje hodnoty podľa pravidiel (viď tabuľky vyššie).
3. Zaznamená metriky a ich vývoj:
   - max / min / priemer sa počíta cez `updateCount`, aby bol výpočet presný.
4. Na konci skontroluje, či medzi dvoma súbormi nie je výpadok dát (> 1 hodina). V takom prípade sa aktívne udalosti ukončia (`finished = True`).
5. Výsledky sa uložia vo forme JSON súborov pre ďalšiu analýzu (napr. cez Pandas,...).

---

## Logovanie

Zmeny v dátach (napr. vyššia rýchlosť, nová linka, nové segmenty) sa zapisujú do súboru `loading_data_to_one_file.log`. Môžeš tak spätne sledovať vývoj každej udalosti.

---

## Kontakt

V prípade otázok, bugov alebo návrhov na zlepšenie ma neváhaj kontaktovať.
