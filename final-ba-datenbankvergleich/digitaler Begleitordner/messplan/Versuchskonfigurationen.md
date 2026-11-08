# Final ausgewertete Versuchskonfigurationen

| Versuchsreihe | PostgreSQL `max_connections` | PostgreSQL-Clientstrategie | MongoDB-Clientstrategie | CPU-Limit je DB-Container | RAM-Limit je DB-Container |
|---|---:|---|---|---:|---:|
| Referenzreihe, 5–100 User | 200 | eine eigene Verbindung pro Locust-User | ein eigener `MongoClient` pro Locust-User | 4 CPUs | 6 GiB |
| Replizierter Hochlastbereich, 500–1.000 User | 6.000 | eine eigene Verbindung pro Locust-User | gemeinsamer `MongoClient`, `maxPoolSize=1000` | 4 CPUs | 6 GiB |
| Explorative Grenzlast, 2.500–5.000 User | 6.000 | eine eigene Verbindung pro Locust-User | gemeinsamer `MongoClient`, `maxPoolSize=1000` | 4 CPUs | 6 GiB |
| Datenmengen-Sensitivitätsanalyse | 6.000 | eine eigene Verbindung pro Locust-User | gemeinsamer `MongoClient`, `maxPoolSize=1000` | 4 CPUs | 6 GiB |

Hinweis: Die Tabelle beschreibt die final ausgewerteten Läufe. Frühere MongoDB-Hochlastvorläufe mit einem eigenen `MongoClient` pro Locust-User wurden nicht in die finale Hochlastauswertung aufgenommen.