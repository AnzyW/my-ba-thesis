# Finale Messergebnisse Medium

## 1. Zweck der Datei

Diese Datei dokumentiert den Abschluss der finalen Messläufe auf dem Datensatzprofil `medium` für die Bachelorarbeit „Datenbankleistung bei hoher Last im E-Commerce“. Sie dient als Zwischenbericht zwischen technischer Messdurchführung und späterer Auswertung in Kapitel 3 der Bachelorarbeit.

Die Messungen vergleichen PostgreSQL und MongoDB unter einem definierten E-Commerce-nahen Lastprofil auf Datenbankebene. Es wurde kein vollständiger Online-Shop getestet, sondern direkte datenbanknahe Operationen über Locust.

## 2. Datensatzprofil

Für die finalen Messläufe wurde das Datensatzprofil `medium` verwendet.

| Datenbereich | Anzahl |
|---|---:|
| Kategorien | 25 |
| Produkte | 50.000 |
| Bestände | 50.000 |
| Kunden | 5.000 |
| Warenkörbe | 5.000 |
| Warenkorbpositionen | 10.032 |
| Initiale Bestellungen | 0 |
| Initiale Bestellpositionen | 0 |

Der Datensatz wurde deterministisch mit festem Seed erzeugt und für PostgreSQL und MongoDB aus derselben fachlichen CSV-Datengrundlage geladen. Vor jedem Messlauf wurde die jeweilige Datenbank neu aus den CSV-Dateien befüllt, damit jeder Lauf mit demselben definierten Ausgangszustand startet.

Dieses Reset-Verfahren erhöht die Vergleichbarkeit der Messläufe, bildet jedoch keinen kontinuierlichen produktiven Langzeitbetrieb ab.

## 3. Lastprofil

In allen finalen Messläufen wurde dasselbe E-Commerce-nahe Lastprofil V1 verwendet.

| Operation | Anteil |
|---|---:|
| `product_list` | 35 % |
| `product_detail` | 25 % |
| `price_availability` | 15 % |
| `cart_read` | 5 % |
| `cart_update` | 15 % |
| `checkout` | 5 % |

Das Profil ist überwiegend leselastig, enthält jedoch relevante Schreib- und Aktualisierungsanteile über Warenkorbänderungen und checkoutnahe Transaktionen.

Bei MongoDB enthält die `checkout`-Operation eine begrenzte Retry-Logik für transiente Transaktionsfehler wie `TransientTransactionError` beziehungsweise `WriteConflict`. Erfolgreich wiederholte Operationen werden nicht als Failure gezählt. Die zusätzliche Ausführungszeit durch mögliche Retries bleibt jedoch Bestandteil der gemessenen Checkout-Latenz.

## 4. Finaler Messplan

Die finalen Messläufe wurden mit sechs Laststufen durchgeführt.

| Laststufe | Locust-User | Spawn-Rate | Laufzeit |
|---|---:|---:|---:|
| L1 | 5 | 1 User/s | 10 Minuten |
| L2 | 10 | 2 User/s | 10 Minuten |
| L3 | 25 | 5 User/s | 10 Minuten |
| L4 | 50 | 10 User/s | 10 Minuten |
| L5 | 75 | 15 User/s | 10 Minuten |
| L6 | 100 | 20 User/s | 10 Minuten |

Jede Laststufe wurde pro Datenbanksystem dreimal wiederholt.

Damit ergaben sich insgesamt:

```text
6 Laststufen × 2 Datenbanksysteme × 3 Wiederholungen = 36 finale Messläufe
```

## 5. Ergebnisdateien

Die finalen Rohdaten liegen unter:

```text
results/final/medium/raw/
```

Die zusammengefassten Ergebnisdateien liegen unter:

```text
results/final/medium/summary/
```

Erzeugte zentrale Dateien:

```text
summary_raw.csv
summary_aggregated.csv
summary_aggregated_backup.csv
```

Die finalen Diagramme liegen unter:

```text
results/final/medium/plots/
```

Erzeugte Diagramme:

```text
throughput_by_users.png
median_latency_by_users.png
p95_latency_by_users.png
p99_latency_by_users.png
failure_rate_by_users.png
operation_p95_u100.png
```

## 6. Status der finalen Messläufe

Alle 36 finalen Messläufe wurden abgeschlossen.

| System | Laststufe | Wiederholungen | Status |
|---|---:|---:|---|
| PostgreSQL | 5 User | r1–r3 | fehlerfrei |
| MongoDB | 5 User | r1–r3 | fehlerfrei |
| PostgreSQL | 10 User | r1–r3 | fehlerfrei |
| MongoDB | 10 User | r1–r3 | fehlerfrei |
| PostgreSQL | 25 User | r1–r3 | fehlerfrei |
| MongoDB | 25 User | r1–r3 | fehlerfrei |
| PostgreSQL | 50 User | r1–r3 | fehlerfrei |
| MongoDB | 50 User | r1–r3 | fehlerfrei |
| PostgreSQL | 75 User | r1–r3 | fehlerfrei |
| MongoDB | 75 User | r1–r3 | fehlerfrei |
| PostgreSQL | 100 User | r1–r3 | fehlerfrei |
| MongoDB | 100 User | r1–r3 | fehlerfrei |

Alle zugehörigen `failures.csv`- und `exceptions.csv`-Dateien enthielten nur Kopfzeilen. Die aggregierte Fehlerrate betrug in allen Laststufen und für beide Systeme 0,0000 %.

## 7. Besondere Vorkommnisse während der Messläufe

Während eines MongoDB-Laufs bei 50 Usern wurde versehentlich eine Terminaleingabe ausgelöst. Locust zeigte daraufhin eine abweichende Nutzerzahl beziehungsweise Spawn-Rate an. Dieser Lauf wurde abgebrochen, die zugehörigen Dateien wurden gelöscht und der Lauf `mongo_medium_u050_r1` wurde nach erneutem Seeding sauber wiederholt.

Während eines PostgreSQL-Laufs bei 75 Usern wurde ebenfalls ein Terminaleingriff durch versehentlichen Rechtsklick ausgelöst. Der betroffene Lauf wurde abgebrochen, die Dateien wurden gelöscht und `postgres_medium_u075_r2` wurde nach erneutem Seeding sauber wiederholt.

Beim letzten PostgreSQL-Lauf `postgres_medium_u100_r3` erschien beim Herunterfahren eine psycopg-Warnung zum Rollback einer bereits terminierten Transaktion. Locust beendete den Lauf jedoch mit Exit Code 0, und sowohl `failures.csv` als auch `exceptions.csv` enthielten nur Kopfzeilen. Die aggregierten Werte für PostgreSQL bei 100 Usern waren plausibel und zeigten keinen auffälligen Ausreißer. Der Lauf wurde daher als gültig eingeordnet.

## 8. Aggregierte Gesamtergebnisse

Die folgende Tabelle zeigt die aggregierten Werte über jeweils drei Wiederholungen pro System und Laststufe.

| System | Datensatz | User | n | Req/s | Median ms | p95 ms | p99 ms | Fail % |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| MongoDB | medium | 5 | 3 | 16,10 | 3,33 | 27,33 | 38,67 | 0,0000 |
| PostgreSQL | medium | 5 | 3 | 16,22 | 2,33 | 17,67 | 30,33 | 0,0000 |
| MongoDB | medium | 10 | 3 | 31,87 | 3,33 | 22,33 | 34,67 | 0,0000 |
| PostgreSQL | medium | 10 | 3 | 32,06 | 2,33 | 16,33 | 25,00 | 0,0000 |
| MongoDB | medium | 25 | 3 | 80,35 | 3,00 | 21,00 | 31,67 | 0,0000 |
| PostgreSQL | medium | 25 | 3 | 80,37 | 2,67 | 16,67 | 25,67 | 0,0000 |
| MongoDB | medium | 50 | 3 | 160,80 | 3,00 | 25,00 | 41,33 | 0,0000 |
| PostgreSQL | medium | 50 | 3 | 161,85 | 2,00 | 15,67 | 25,33 | 0,0000 |
| MongoDB | medium | 75 | 3 | 242,21 | 3,00 | 23,00 | 38,00 | 0,0000 |
| PostgreSQL | medium | 75 | 3 | 243,38 | 2,00 | 15,33 | 25,33 | 0,0000 |
| MongoDB | medium | 100 | 3 | 318,27 | 4,67 | 38,67 | 84,33 | 0,0000 |
| PostgreSQL | medium | 100 | 3 | 324,10 | 2,33 | 19,00 | 38,00 | 0,0000 |

## 9. Sanity-Checks PostgreSQL

Nach dem letzten PostgreSQL-Lauf wurden Plausibilitätsprüfungen auf dem Datenbankzustand durchgeführt.

| Prüfung | Ergebnis |
|---|---:|
| Orders | 9.856 |
| Order Items | 29.367 |
| Aktive Warenkörbe | 5.000 |
| Negative Bestände | 0 |
| Produkte | 50.000 |
| Bestandsdatensätze | 50.000 |

Einordnung:

- Es wurden Bestellungen erzeugt.
- Es wurden Bestellpositionen erzeugt.
- Die Anzahl aktiver Warenkörbe blieb bei 5.000.
- Es existieren keine negativen Bestände.
- Produkt- und Bestandsanzahl blieben unverändert.

Die PostgreSQL-Sanity-Checks sind damit plausibel.

## 10. Sanity-Checks MongoDB

Nach dem letzten MongoDB-Lauf wurden Plausibilitätsprüfungen auf dem Datenbankzustand durchgeführt.

| Prüfung | Ergebnis |
|---|---:|
| Orders | 9.554 |
| Eingebettete Order Items | 28.435 |
| Aktive Warenkörbe | 5.000 |
| Negative Bestände | 0 |
| Produkte | 50.000 |
| Warenkörbe gesamt | 14.554 |
| Checked-out-Warenkörbe | 9.554 |

Einordnung:

- Es wurden Bestellungen erzeugt.
- Die Bestellungen enthalten eingebettete Positionen.
- Die Anzahl aktiver Warenkörbe blieb bei 5.000.
- Es existieren keine negativen Bestände.
- Die Produktanzahl blieb unverändert.
- Die Gesamtzahl der Warenkörbe ist plausibel, da sie sich aus den initialen 5.000 aktiven Warenkörben und den 9.554 abgeschlossenen Checkouts ergibt.
- Die Anzahl der `checked_out`-Warenkörbe entspricht der Anzahl der Orders.

Die MongoDB-Sanity-Checks sind damit plausibel.

## 11. Erste Beobachtungen

### Durchsatz

Der Durchsatz steigt über die Laststufen hinweg nahezu linear an. Beide Systeme liegen beim Durchsatz sehr nah beieinander.

Bei 100 Usern erreicht PostgreSQL im Mittel 324,10 Requests pro Sekunde, MongoDB erreicht 318,27 Requests pro Sekunde. Der Unterschied im Durchsatz ist damit sichtbar, aber nicht sehr groß.

### Fehlerrate

Die Fehlerrate beträgt in allen Laststufen und bei beiden Systemen 0,0000 %. Das bedeutet, dass Locust keine endgültig fehlgeschlagenen Operationen registriert hat.

Für MongoDB ist dabei zu berücksichtigen, dass transiente Transaktionskonflikte im Checkout durch eine begrenzte Retry-Strategie behandelt werden. Erfolgreich wiederholte Operationen erscheinen nicht als Failure, ihre zusätzliche Ausführungszeit bleibt jedoch in den gemessenen Latenzen enthalten.

### Median-Latenz

PostgreSQL zeigt über alle Laststufen hinweg niedrigere Median-Latenzen als MongoDB. Besonders bei 100 Usern steigt die Median-Latenz von MongoDB auf 4,67 ms, während PostgreSQL bei 2,33 ms liegt.

### p95-Latenz

Auch bei der p95-Latenz liegt PostgreSQL über alle Laststufen hinweg niedriger als MongoDB. Bei 100 Usern beträgt die p95-Latenz bei MongoDB 38,67 ms, bei PostgreSQL 19,00 ms.

### p99-Latenz

Der Unterschied wird bei der p99-Latenz besonders deutlich. Bei 100 Usern liegt MongoDB bei 84,33 ms, PostgreSQL bei 38,00 ms. Damit zeigt MongoDB im oberen Latenzbereich eine deutlich stärkere Streuung beziehungsweise höhere Tail-Latenzen.

### Operationsbezogene p95-Latenz bei 100 Usern

Das Diagramm `operation_p95_u100.png` zeigt, dass insbesondere die checkoutnahe Operation bei MongoDB deutlich höhere p95-Latenzen aufweist als bei PostgreSQL. Auch `cart_update` ist bei MongoDB höher. Das deutet darauf hin, dass die schreibenden beziehungsweise transaktionsnahen Operationen im gewählten MongoDB-Modell stärker zur erhöhten Tail-Latenz beitragen.

## 12. Vorläufige Einordnung

Die Ergebnisse zeigen, dass beide Systeme im untersuchten Lastbereich stabil bleiben und keine endgültigen Failures aufweisen. Beim Durchsatz skalieren PostgreSQL und MongoDB im getesteten Bereich ähnlich. Die zentrale Differenz liegt weniger im erfolgreichen Durchsatz, sondern stärker im Latenzverhalten.

PostgreSQL zeigt über die Laststufen hinweg niedrigere Median-, p95- und p99-Latenzen. MongoDB zeigt insbesondere bei 100 Usern und bei checkoutnahen Operationen höhere Tail-Latenzen. Diese Beobachtung ist für die spätere Interpretation im Kontext der Architekturprinzipien relevant.

Eine endgültige Bewertung erfolgt erst im Ergebniskapitel der Bachelorarbeit. Dabei müssen insbesondere Datenmodellierung, Transaktionsverhalten, MongoDB-Retry-Logik, Indexierung und die lokale Testumgebung berücksichtigt werden.

## 13. Methodische Hinweise und Limitationen

Die Ergebnisse beziehen sich ausschließlich auf den definierten Messaufbau:

- lokaler Laptop als Testumgebung,
- getrennte Ausführung von PostgreSQL und MongoDB,
- Datensatzprofil `medium`,
- E-Commerce-nahes Lastprofil V1,
- direkte datenbanknahe Locust-Operationen,
- keine vollständige Shop-Architektur,
- kein Caching,
- kein Load Balancing,
- kein Clusterbetrieb,
- keine Replikations- oder Sharding-Untersuchung.

Das Neu-Seeden vor jedem Messlauf erhöht Vergleichbarkeit und Reproduzierbarkeit, bildet aber keinen fortlaufenden Realbetrieb mit dauerhaft wachsendem Datenbestand ab.

Die Fehlerrate beschreibt endgültig fehlgeschlagene Locust-Operationen. Erfolgreich wiederholte MongoDB-Checkout-Operationen werden nicht als Failure gezählt, ihre zusätzliche Laufzeit bleibt jedoch in den Latenzmetriken enthalten.

## 14. Nächste Schritte

Nach Abschluss der Messläufe und Sanity-Checks sind die nächsten Schritte:

1. Finale Ergebnisdateien und Diagramme sichern.
2. Versuchsprotokoll um den finalen Messabschluss ergänzen.
3. Kapitel 3.1 „Testdurchführung und Laststufen“ ausarbeiten.
4. Kapitel 3.2 „Ergebnisse und Gegenüberstellung“ anhand der finalen Diagramme schreiben.
5. Kapitel 3.3 „Interpretation im Kontext der Architekturprinzipien“ ausarbeiten.
6. Kapitel 3.4 „Limitationen der Untersuchung“ formulieren.
7. Fazit und Ausblick vorbereiten.
