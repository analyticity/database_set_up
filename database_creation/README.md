# README

## Prehľad

Tento projekt obsahuje:

- **Docker Compose** súbor pre spustenie viacerých PostgreSQL databáz v kontajneroch.
- **`init_db_central.sql`** – inicializačný SQL skript pre centrálnu databázu, ktorá uchováva meta-informácie o ostatných databázach.
- **`init.sql` súbory** pre jednotlivé databázy (napr. `init.sql` s tabuľkami jams, alerts, atď.)
- `update_coverage_area.py` - načíta správne geolokačné informácie do centrálnej db
---

## Obsah súborov

| Súbor              | Popis                                         |
|--------------------|-----------------------------------------------|
| `docker-compose.yml`| Definícia kontajnerov a sietí pre databázy    |
| `init_db_central.sql` | Inicializácia centrálnej DB s tabuľkou `data_sources` |
| `init.sql`          | Inicializácia špecifickej DB (jams, alerts, atď.) |

---

## Ako rozbehať Docker kontajnery s PostgreSQL

1. **Uisti sa, že máš nainštalovaný Docker**

2. **Priprav `.env` súbor**

V koreňovom adresári projektu vytvor súbor `.env` so všetkými potrebnými premennými, napríklad:

```env
POSTGRES_DB_CENTRAL=central_db
POSTGRES_USER_CENTRAL=<central_user>
POSTGRES_PASSWORD_CENTRAL=<central_password>

POSTGRES_DB_BRNO=traffic_brno
POSTGRES_USER_BRNO=<db_admin>
POSTGRES_PASSWORD_BRNO=<db_password>

# a ďalšie podľa potreby ...
```

3. **Spusti kontajnery**
   - V termináli v priečinku s docker-compose.yml spusti:
```bash
docker-compose up -d
```

## Ako sa pripojiť k PostgreSQL kontajnerom
- Príklad pripojenia k centrálnej databáze pomocou psql (môžeš použiť aj PGAdmin, DBeaver alebo iný klient):

```bash
psql -h localhost -p 5431 -U central_user central_db
```
- Pre ďalšie databázy sa pripojíš na ich definované porty (napr. 5433, 5434, ...), s príslušnými používateľmi a databázami.

## Ako dostať dáta z db do .csv súboru
- dáta sú uložené v `hypertables` - je potreba teda spraviť najskôr obyčajný select a potom dáta dostať do .csv súboru

1. Vytvorenie .csv súborov vo vnútri dockeru 
   - obsahujú iba samotné (raw) dáta, žiadne hypertables 
```shell
docker exec -i timescaledb_brno psql -U analyticity_brno -d traffic_brno -c "\COPY (SELECT * FROM jams) TO '/tmp/jams.csv' CSV HEADER"
docker exec -i timescaledb_brno psql -U analyticity_brno -d traffic_brno -c "\COPY (SELECT * FROM alerts) TO '/tmp/alerts.csv' CSV HEADER"
docker exec -i timescaledb_brno psql -U analyticity_brno -d traffic_brno -c "\COPY (SELECT * FROM nehody) TO '/tmp/nehody.csv' CSV HEADER"
```
2. Skopírovanie z dockeru na lokálne úložisko:
```shell    
docker cp timescaledb_brno:/tmp/jams.csv brno_jams.csv
docker cp timescaledb_brno:/tmp/alerts.csv brno_alerts.csv
docker cp timescaledb_brno:/tmp/nehody.csv brno_nehody.csv
```
3. Nahranie pomocou python scriptu do novej db. 

