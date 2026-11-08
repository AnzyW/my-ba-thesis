# Versuchsprotokoll V1

## 1. Ziel des Versuchs

Ziel des Versuchs ist der empirische Vergleich von PostgreSQL und MongoDB unter einem definierten E-Commerce-nahen Lastprofil. Der Fokus liegt auf der Datenbankebene. Es wird kein vollständiger Online-Shop umgesetzt.

## 2. Testumgebung

Der Versuch wird lokal auf einem Windows-11-Laptop durchgeführt.

Hardware:

- CPU: Intel Core i7-1165G7 @ 2.80 GHz
- RAM: 16 GB
- Speicher: Intel Optane H10 with SSD, ca. 512 GB, SSD RAID

Die Datenbanken werden voraussichtlich über Docker Compose in Containern betrieben. Pro Messlauf wird nur ein Datenbanksystem aktiv belastet, damit PostgreSQL und MongoDB nicht gleichzeitig um dieselben Ressourcen konkurrieren.

## 3. Geplante Software

- PostgreSQL: `postgres:18.4-bookworm`
- MongoDB: `mongodb/mongodb-community-server:8.0.23-ubi8-slim`
- Lastgenerator: Locust
- Ausführung: Docker Compose

## 4. Vorläufiges Datenmodell

Das Datenmodell bildet zentrale E-Commerce-nahe Datenbereiche ab:

- Produkte
- Bestände
- Kunden
- Warenkörbe
- Bestellungen
- Bestellpositionen

Das Modell bildet keinen vollständigen Online-Shop ab, sondern nur die für die untersuchten Datenbankzugriffe relevanten Datenstrukturen.

## 5. Vorläufiges Lastprofil

Das Lastprofil besteht aus mehreren Zugriffsmustern:

| Operation | Anteil |
|---|---:|
| Produktliste / Produktsuche | 35 % |
| Produktdetail abrufen | 25 % |
| Preis- und Bestandsabfrage | 15 % |
| Warenkorb lesen | 5 % |
| Warenkorb ändern | 15 % |
| Checkout | 5 % |

Damit ergibt sich ein überwiegend leselastiges Lastprofil mit relevanten Schreib- und Aktualisierungsanteilen.

## 6. Metriken

Erfasst werden:

- Median-Latenz
- p95-Latenz
- p99-Latenz
- Durchsatz
- Fehlerrate
- CPU-Auslastung
- RAM-Nutzung
- I/O-Aktivität

## 7. Abgrenzung

Nicht untersucht werden:

- vollständige Shop-Architektur
- Frontend
- Caching
- Load Balancing
- Sharding
- Clusterbetrieb
- eigene Monitoring-Dashboards

## 8. Ressourcenzuweisung

Für den Vergleich werden PostgreSQL und MongoDB unter möglichst identischen Ressourcenbedingungen betrieben. Die Datenbanksysteme werden nicht gleichzeitig belastet, sondern in getrennten Messläufen untersucht. Dadurch soll vermieden werden, dass sich beide Systeme gegenseitig durch konkurrierende CPU-, Arbeitsspeicher- oder I/O-Nutzung beeinflussen.

Für die Datenbankcontainer ist vorläufig folgende Ressourcenzuweisung vorgesehen:

| Komponente | CPU-Limit | RAM-Limit |
|---|---:|---:|
| PostgreSQL | 4 CPUs | 6 GB |
| MongoDB | 4 CPUs | 6 GB |
| Locust | 1 CPU | 1 GB |

Die genaue Ressourcenzuweisung wird im Rahmen der technischen Umsetzung überprüft und dokumentiert. Falls sich im Probelauf zeigt, dass die gewählten Limits auf dem lokalen Testsystem nicht stabil ausführbar sind, werden die Werte angepasst und die Anpassung im Versuchsprotokoll festgehalten.

## 9. Datensatzumfang

Für die erste Versuchsversion wird ein synthetischer Datensatz verwendet. Der Datensatz soll groß genug sein, um realistische datenbanknahe Zugriffsmuster zu erzeugen, aber zugleich auf dem lokalen Testsystem reproduzierbar ausführbar bleiben.

Vorgesehener Datensatzumfang:

| Datentyp | Anzahl |
|---|---:|
| Produkte | 200.000 |
| Kunden | 20.000 |
| aktive Warenkörbe | 20.000 |
| Kategorien | 50 |
| initiale Bestellungen | 0 |

Jedes Produkt erhält zusätzlich einen Bestand. Die Bestandswerte werden synthetisch erzeugt. Die Testdaten werden für beide Datenbanksysteme aus derselben fachlichen Datengrundlage generiert, damit PostgreSQL und MongoDB mit vergleichbaren Datenmengen untersucht werden.

## 10. Laststufen

Die Last wird schrittweise erhöht. Dadurch soll sichtbar werden, wie sich Latenz, Durchsatz, Fehlerrate und Ressourcennutzung bei zunehmender Parallelität entwickeln.

Vorläufig geplante Laststufen:

| Laststufe | Gleichzeitige Nutzer | Messdauer |
|---|---:|---:|
| L1 | 10 | 10 Minuten |
| L2 | 25 | 10 Minuten |
| L3 | 50 | 10 Minuten |
| L4 | 75 | 10 Minuten |
| L5 | 100 | 10 Minuten |
| L6 | 150 | 10 Minuten |
| L7 | 200 | 10 Minuten |

Vor den eigentlichen Messläufen wird ein kleiner Probelauf durchgeführt. Dieser dient dazu, die technische Funktionsfähigkeit der Datenbankverbindungen, der Testdaten, des Lastgenerators und der Messdatenerfassung zu überprüfen. Die Ergebnisse des Probelaufs werden nicht als finale Messergebnisse ausgewertet.

## 11. Messablauf

Für jedes Datenbanksystem wird derselbe Messablauf verwendet.

Geplanter Ablauf pro Datenbanksystem:

1. Datenbankcontainer starten.
2. Testdaten laden.
3. Indexe erstellen.
4. Kurzen Funktionstest ausführen.
5. Lastgenerator starten.
6. Warm-up-Phase durchführen.
7. Messphase durchführen.
8. Locust-Ergebnisse exportieren.
9. Ressourcenwerte erfassen.
10. Datenbankcontainer stoppen.
11. Ergebnisse im Ergebnisordner speichern.

Die Warm-up-Phase dient dazu, einmalige Starteffekte zu reduzieren. Sie wird nicht in die finale Auswertung einbezogen. Die Messphase wird anschließend separat betrachtet.

## 12. Wiederholungen

Um zufällige Schwankungen einzelner Messläufe zu reduzieren, soll jede Laststufe mindestens dreimal pro Datenbanksystem wiederholt werden. Aus den Wiederholungen können anschließend Mittelwerte oder repräsentative Vergleichswerte gebildet werden.

Falls sich im praktischen Verlauf zeigt, dass die vollständige Wiederholung aller Laststufen aufgrund der lokalen Hardware zu zeitaufwendig ist, wird dies dokumentiert. In diesem Fall werden mindestens ausgewählte Laststufen wiederholt, insbesondere niedrige, mittlere und hohe Lastbereiche.

## 13. Fehlerdefinition

Als fehlerhafte Anfrage gelten im Versuch insbesondere:

- fehlgeschlagene Datenbankoperationen
- Zeitüberschreitungen
- abgebrochene Verbindungen
- nicht erfolgreich abgeschlossene Transaktionen
- fachlich ungültige Checkout-Vorgänge aufgrund unzureichenden Bestands

Fehler werden über den Lastgenerator erfasst und in der Fehlerrate berücksichtigt. Fachlich erwartbare Ablehnungen, zum Beispiel ein Checkout bei nicht ausreichendem Bestand, müssen im Lasttest eindeutig von technischen Fehlern unterschieden werden.

## 14. Reproduzierbarkeit

Zur Reproduzierbarkeit des Versuchs werden folgende Punkte dokumentiert:

- verwendete Datenbankversionen
- verwendete Docker-Images
- Docker-Compose-Konfiguration
- Datenbankschema beziehungsweise Collection-Struktur
- Indexe
- Testdatenumfang
- Seed-Werte der Datengenerierung
- Lastprofil
- Laststufen
- Messdauer
- Locust-Konfiguration
- Ergebnisdateien

Ziel ist es, den Versuchsaufbau so zu dokumentieren, dass die Messläufe unter denselben Rahmenbedingungen nachvollzogen werden können.

## Zwischenstand der technischen Probeläufe

Nach der Einrichtung der Testumgebung wurden zunächst technische Probeläufe durchgeführt, um die grundsätzliche Funktionsfähigkeit der Versuchspipeline zu prüfen. Diese Probeläufe dienen nicht als finale Messergebnisse, sondern als technische Validierung des Versuchsaufbaus.

Die bisherige Pipeline umfasst:

- Erzeugung einer gemeinsamen synthetischen Datengrundlage als CSV-Dateien,
- Laden derselben Datengrundlage in PostgreSQL und MongoDB,
- Ausführung eines E-Commerce-nahen Lastprofils mit Locust,
- Speicherung der Locust-Ergebnisse als CSV-Dateien,
- Zusammenfassung der Ergebnisse in einer `summary.csv`,
- automatische Erzeugung erster Diagramme aus den CSV-Ergebnissen.

Die Probeläufe wurden mit 1, 5, 10 und 25 simulierten Locust-Usern durchgeführt. Beide Datenbanksysteme konnten die definierten Operationen grundsätzlich ausführen. Die Fehler- und Exception-Dateien enthielten nach Abschluss der Probeläufe keine relevanten Einträge. Damit ist die technische Funktionsfähigkeit der Lasttest- und Auswertungspipeline nachgewiesen.

Während des MongoDB-Probelaufs mit 25 simulierten Usern trat zunächst ein transienter `WriteConflict` in der checkoutnahen Transaktion auf. Dieser Fehler wurde als Nebenläufigkeitskonflikt bei konkurrierenden Schreiboperationen eingeordnet. Die MongoDB-Checkout-Logik wurde anschließend um eine begrenzte Retry-Strategie für transiente Transaktionsfehler erweitert. Nach dieser Anpassung konnte der 25-User-Probelauf ohne relevante Failures oder Exceptions abgeschlossen werden. Die durch mögliche Retries entstehende zusätzliche Ausführungszeit bleibt Bestandteil der gemessenen Checkout-Latenz und wird daher nicht aus der Messung herausgerechnet.

Die erzeugten Diagramme zeigen, dass der Durchsatz mit steigender Nutzerzahl zunimmt und keine Fehler auftraten. Die Latenzwerte der Probeläufe werden jedoch nicht als finale Ergebnisse interpretiert, da die Testdauer kurz war, der Datensatz klein ist und Caching- sowie Zufallseffekte einen starken Einfluss haben können.

## Vorläufiger finaler Messplan

Für die finalen Messläufe soll ein standardisierter Ablauf verwendet werden. Ziel ist es, PostgreSQL und MongoDB unter vergleichbaren Bedingungen mit demselben fachlichen Lastprofil zu untersuchen.

Vor jedem Messlauf wird die jeweilige Datenbank auf denselben Ausgangszustand zurückgesetzt. Dadurch wird verhindert, dass vorherige `cart_update`- oder `checkout`-Operationen spätere Messläufe verfälschen. PostgreSQL und MongoDB werden getrennt getestet, sodass jeweils nur ein Datenbanksystem aktiv belastet wird.

Als zentrale Messgrößen werden erfasst:

- Durchsatz in Requests pro Sekunde,
- Median-Latenz,
- p95-Latenz,
- p99-Latenz,
- maximale Antwortzeit als ergänzende Kennzahl,
- Fehleranzahl und Fehlerrate,
- Exceptions während des Laufs.

Die finalen Diagramme sollen nicht aus Screenshots der Locust-Oberfläche erstellt werden. Die Locust-GUI dient nur zur Demonstration und Plausibilitätsprüfung. Die eigentliche Auswertung basiert auf den exportierten CSV-Dateien der Headless-Läufe.

Für die finalen Messläufe ist ein stufenweises Vorgehen vorgesehen. Die Last wird schrittweise erhöht, um zu beobachten, ab wann sich Latenzen, Durchsatz oder Fehlerverhalten sichtbar verändern. Die genaue Laststufung wird nach Abschluss der Probelaufphase festgelegt.

## Geplanter nächster technischer Schritt

Als nächster technischer Schritt soll ein zusätzliches Datensatzprofil `medium` in `scripts/generate_dataset.py` ergänzt werden. Dieses Profil dient als Zwischenstufe zwischen dem bisherigen kleinen Testdatensatz und einem optional größeren Hauptdatensatz.

Die Profile sollen vorläufig wie folgt eingeordnet werden:

| Profil | Zweck | Kategorien | Produkte | Kunden | Warenkörbe |
|---|---:|---:|---:|---:|---:|
| `small` | Smoke- und Probeläufe | 5 | 1.000 | 100 | 100 |
| `medium` | realistischere Testbasis für weitere Probeläufe | 25 | 50.000 | 5.000 | 5.000 |
| `full` | optionaler größerer Hauptdatensatz | 50 | 200.000 | 20.000 | 20.000 |

Das `medium`-Profil soll verwendet werden, um die Versuchspipeline mit einer deutlich größeren Datenbasis zu testen, ohne den lokalen Laptop sofort unnötig stark durch einen sehr großen Datensatz zu belasten. Erst nach erfolgreicher Prüfung dieses Zwischenprofils wird entschieden, ob das `full`-Profil für finale Messläufe geeignet ist oder ob die finale Datensatzgröße angepasst werden muss.


# Medium Zwischenstand

## Medium-Datensatz

Nach den technischen Smoke- und Probeläufen mit dem kleinen Datensatz wurde ein zusätzliches Datensatzprofil `medium` eingeführt. Dieses Profil dient als Zwischenstufe zwischen den initialen Funktionstests und einem optional größeren Hauptdatensatz. Ziel ist es, die Versuchspipeline mit einer deutlich größeren, aber für den lokalen Laptop weiterhin handhabbaren Datenbasis zu prüfen.

Der Medium-Datensatz wurde mit einem festen Seed erzeugt:

```text
Seed: 42
```

Die erzeugten CSV-Dateien im Ordner `data/` enthalten:

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

Der Medium-Datensatz ersetzt für die weiteren Probeläufe die zuvor verwendete kleine Datengrundlage. Da die Testdaten deterministisch erzeugt werden, kann der kleine Datensatz bei Bedarf jederzeit erneut über das Profil `small` erzeugt werden.

## Laden des Medium-Datensatzes

Der Medium-Datensatz wurde anschließend in beide Datenbanksysteme geladen.

Für PostgreSQL wurde geprüft:

```text
products: 50.000
cart_items: 10.032
```

Für MongoDB wurde geprüft:

```text
products: 50.000
cart_items eingebettet: 10.032
```

Damit ist sichergestellt, dass beide Datenbanksysteme mit derselben fachlichen Datengrundlage getestet wurden. Unterschiede in der physischen Speicherung ergeben sich aus dem jeweiligen Datenmodell: PostgreSQL nutzt relationale Tabellen, während MongoDB Warenkorbpositionen und Bestandsinformationen dokumentenorientiert einbettet.

## Medium-Probeläufe

Die Medium-Probeläufe wurden in einem separaten Ergebnisordner gespeichert:

```text
results/medium/
```

Dadurch werden die Ergebnisse des kleinen Smoke-Datensatzes nicht mit den Ergebnissen des Medium-Datensatzes vermischt.

Die Probeläufe wurden mit folgenden Laststufen durchgeführt:

| Laststufe | Spawn-Rate | Laufzeit |
|---|---:|---:|
| 5 User | 1 User/s | 3 Minuten |
| 10 User | 2 User/s | 3 Minuten |
| 25 User | 5 User/s | 3 Minuten |

Vor jedem Lauf wurde die jeweilige Datenbank neu aus den CSV-Dateien befüllt. Dadurch wurde sichergestellt, dass vorherige Schreiboperationen aus `cart_update` oder `checkout` den Ausgangszustand des nächsten Laufs nicht verfälschen.

Die folgenden Läufe wurden erfolgreich durchgeführt:

| System | Lauf | Ergebnis |
|---|---|---|
| MongoDB | `mongo_medium_u5` | keine relevanten Failures oder Exceptions |
| PostgreSQL | `postgres_medium_u5` | keine relevanten Failures oder Exceptions |
| MongoDB | `mongo_medium_u10` | keine relevanten Failures oder Exceptions |
| PostgreSQL | `postgres_medium_u10` | keine relevanten Failures oder Exceptions |
| MongoDB | `mongo_medium_u25` | keine relevanten Failures oder Exceptions |
| PostgreSQL | `postgres_medium_u25` | keine relevanten Failures oder Exceptions |

Damit ist die Versuchspipeline auch auf dem Medium-Datensatz bis 25 simulierte Locust-User technisch stabil.

## Auswertung der Medium-Probeläufe

Nach Abschluss der Läufe wurden die Locust-CSV-Dateien mit dem Auswertungsskript zusammengeführt:

```powershell
python scripts/analyze_locust_results.py --results-dir results/medium --output results/medium/summary.csv
```

Anschließend wurden Diagramme erzeugt:

```powershell
python scripts/plot_locust_summary.py --summary-file results/medium/summary.csv --plots-dir results/medium/plots
```

Die Diagramme wurden im folgenden Ordner gespeichert:

```text
results/medium/plots/
```

Erzeugt wurden unter anderem Diagramme zu:

- Durchsatz je Laststufe,
- Median-Latenz je Laststufe,
- p95-Latenz je Laststufe,
- p99-Latenz je Laststufe,
- maximaler Antwortzeit je Laststufe,
- Fehleranzahl je Laststufe.

## Vorläufige Beobachtungen

Die Medium-Probeläufe zeigen, dass der Durchsatz mit steigender Nutzerzahl zunimmt. Bei 5 Usern liegt der Durchsatz ungefähr bei 16 Requests pro Sekunde, bei 10 Usern ungefähr bei 32 Requests pro Sekunde und bei 25 Usern ungefähr bei 80 Requests pro Sekunde. PostgreSQL und MongoDB liegen beim Durchsatz in diesen Probeläufen nahezu gleichauf.

Die Fehleranzahl bleibt in allen Medium-Probeläufen bei 0. Dies bestätigt, dass das Lastprofil, der CSV-Export und die Auswertungspipeline auch mit der größeren Datengrundlage stabil funktionieren.

Bei den p95- und p99-Latenzen zeigt MongoDB in den Medium-Probeläufen höhere Werte als PostgreSQL. PostgreSQL zeigt in diesen Probeläufen teilweise sinkende p95- und p99-Werte bei steigender Nutzerzahl. Diese Beobachtung wird noch nicht als finales Ergebnis interpretiert, da es sich weiterhin um kurze Probeläufe handelt. Caching, Warm-up-Effekte, zufällige Operationsverteilungen und die kurze Laufzeit können die Werte beeinflussen.

## Einordnung

Die Medium-Probeläufe sind nicht als finale wissenschaftliche Messläufe zu interpretieren. Sie dienen der Stabilitätsprüfung der Versuchspipeline und der Plausibilisierung des geplanten Messaufbaus.

Der aktuelle Stand zeigt:

- Der Medium-Datensatz kann reproduzierbar erzeugt werden.
- Der Medium-Datensatz kann in PostgreSQL und MongoDB geladen werden.
- Das definierte E-Commerce-nahe Lastprofil läuft auf beiden Systemen.
- Die Headless-Ausführung mit Locust funktioniert.
- Der CSV-Export funktioniert.
- Die automatisierte Auswertung und Diagrammerzeugung funktionieren.
- Bis 25 simulierte User treten keine relevanten Failures oder Exceptions auf.

Auf Basis dieses Zwischenstands kann im nächsten Schritt der finale Messplan konkretisiert werden. Dabei sind insbesondere die finale Datensatzgröße, die Laststufen, die Laufzeit pro Messlauf, die Anzahl der Wiederholungen und die Auswertungskriterien festzulegen.


# Finaler Messplan

## 1. Ziel des finalen Messplans

Der finale Messplan legt fest, unter welchen Bedingungen PostgreSQL und MongoDB im empirischen Teil der Bachelorarbeit verglichen werden. Ziel ist ein kontrollierter, reproduzierbarer und auswertbarer Vergleich der Datenbankleistung unter einem definierten E-Commerce-nahen Lastprofil.

Der Fokus liegt weiterhin auf der Datenbankebene. Es wird kein vollständiger Online-Shop untersucht. Die Last wird synthetisch mit Locust erzeugt und besteht aus datenbanknahen Operationen, die typische Zugriffsmuster eines E-Commerce-Systems abstrahieren.

## 2. Finaler Hauptdatensatz

Für die finalen Messläufe wird das Datensatzprofil `medium` als Hauptdatensatz verwendet. Dieses Profil wurde bereits erfolgreich erzeugt, in PostgreSQL und MongoDB geladen und in mehreren Probeläufen geprüft.

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

Der Datensatz wird deterministisch mit einem festen Seed erzeugt und für beide Datenbanksysteme aus derselben fachlichen CSV-Datengrundlage geladen. Dadurch wird sichergestellt, dass PostgreSQL und MongoDB mit vergleichbaren Daten getestet werden.

Der größere Datensatz `full` wird nicht als Hauptdatensatz der finalen Evaluation verwendet. Der Grund dafür liegt in der begrenzten lokalen Testumgebung. Für den wissenschaftlichen Vergleich ist ein vollständig reproduzierbarer und mehrfach wiederholbarer Messaufbau wichtiger als ein größerer Datensatz, der auf der vorhandenen Hardware nur eingeschränkt stabil oder mit unverhältnismäßig hoher Laufzeit getestet werden kann. Der `full`-Datensatz kann optional als ergänzender Ausblick oder explorativer Zusatztest betrachtet werden, ist jedoch nicht Bestandteil des finalen Hauptvergleichs.

## 3. Finales Lastprofil

Für alle finalen Messläufe wird dasselbe E-Commerce-nahe Lastprofil V1 verwendet.

| Operation | Anteil |
|---|---:|
| Produktliste beziehungsweise Produktsuche | 35 % |
| Produktdetail abrufen | 25 % |
| Preis- und Bestandsabfrage | 15 % |
| Warenkorb lesen | 5 % |
| Warenkorb ändern | 15 % |
| Checkout | 5 % |

Damit ergibt sich ein überwiegend leselastiges Lastprofil mit relevanten Schreib- und Aktualisierungsanteilen. Die Operationen werden für PostgreSQL und MongoDB fachlich gleich abgebildet, aber systemspezifisch umgesetzt. PostgreSQL verwendet ein relationales Tabellenmodell, MongoDB verwendet dokumentenorientierte Collections und eingebettete Strukturen.

Für MongoDB bleibt die begrenzte Retry-Logik bei `TransientTransactionError` beziehungsweise `WriteConflict` Bestandteil des Messaufbaus. Die durch mögliche Retries entstehende zusätzliche Zeit wird nicht aus der Messung herausgerechnet, sondern bleibt Bestandteil der gemessenen Checkout-Latenz.

## 4. Finale Laststufen

Die Last wird in sechs Stufen schrittweise erhöht. Dadurch soll sichtbar werden, wie sich Durchsatz, Latenzen und Fehlerverhalten bei zunehmender Parallelität entwickeln.

| Laststufe | Locust-User | Spawn-Rate | Laufzeit |
|---|---:|---:|---:|
| L1 | 5 | 1 User/s | 10 Minuten |
| L2 | 10 | 2 User/s | 10 Minuten |
| L3 | 25 | 5 User/s | 10 Minuten |
| L4 | 50 | 10 User/s | 10 Minuten |
| L5 | 75 | 15 User/s | 10 Minuten |
| L6 | 100 | 20 User/s | 10 Minuten |

Die Laststufen 5, 10 und 25 User wurden bereits in den Medium-Probeläufen technisch geprüft. Die finalen Messläufe erweitern diese Reihe kontrolliert auf 50, 75 und 100 User.

Höhere Laststufen wie 150 oder 200 User werden nicht als Bestandteil des finalen Hauptplans festgelegt. Sie können nur dann explorativ ergänzt werden, wenn die Laststufe mit 100 Usern bei beiden Systemen stabil und ohne relevante Störungen durch die lokale Testumgebung ausgeführt werden kann.

## 5. Laufzeit pro Messlauf

Jeder finale Messlauf dauert 10 Minuten. Die Locust-Ausführung erfolgt im Headless-Modus und exportiert die Messergebnisse als CSV-Dateien.

Eine separate Warm-up-Phase wird für die finale Auswertung nicht ausgewiesen, solange sie technisch nicht eindeutig aus den exportierten Locust-Daten ausgeschlossen wird. Stattdessen werden identische Laufzeit, identische Spawn-Rate und identischer Ablauf für beide Datenbanksysteme verwendet.

Die Locust-GUI wird nicht zur finalen Messdatenerhebung verwendet. Sie kann höchstens zur Plausibilitätsprüfung oder Demonstration genutzt werden. Die wissenschaftliche Auswertung basiert ausschließlich auf den exportierten CSV-Dateien.

## 6. Wiederholungen

Jede Laststufe wird pro Datenbanksystem dreimal wiederholt.

Damit ergeben sich:

```text
6 Laststufen × 2 Datenbanksysteme × 3 Wiederholungen = 36 finale Messläufe
```

Die Wiederholungen dienen dazu, zufällige Schwankungen einzelner Messläufe zu reduzieren. Für die Ergebnisdarstellung werden die Einzelmessungen dokumentiert und zusätzlich aggregierte Werte über die Wiederholungen gebildet.

## 7. Reset-Regel vor jedem Messlauf

Vor jedem einzelnen Messlauf wird das jeweils getestete Datenbanksystem auf denselben Ausgangszustand zurückgesetzt und aus den gemeinsamen CSV-Dateien neu befüllt.

Der Reset ist notwendig, weil die Operationen `cart_update` und `checkout` den Datenbestand verändern. Ohne Reset würden spätere Messläufe mit veränderten Warenkörben, veränderten Beständen und zusätzlichen Bestellungen ausgeführt werden. Dadurch wären die Messläufe nicht mehr direkt vergleichbar.

Der Ablauf vor jedem Messlauf lautet:

1. Nur das zu testende Datenbanksystem starten.
2. Datenbank auf den Ausgangszustand zurücksetzen.
3. Medium-Datensatz aus den CSV-Dateien neu laden.
4. Indexe beziehungsweise Collection-Strukturen herstellen.
5. Kurzen Funktionstest durchführen.
6. Locust-Lauf im Headless-Modus starten.
7. Locust-CSV-Dateien speichern.
8. Fehler- und Exception-Dateien prüfen.
9. Datenbanksystem stoppen oder für den nächsten Reset vorbereiten.

PostgreSQL und MongoDB werden weiterhin getrennt getestet. Es wird immer nur ein Datenbanksystem aktiv belastet, damit sich beide Systeme nicht gegenseitig durch CPU-, RAM- oder I/O-Nutzung beeinflussen.

## 8. Ergebnisordner

Die finalen Messergebnisse werden getrennt von Smoke- und Medium-Probeläufen gespeichert.

Vorgesehene Ordnerstruktur:

```text
results/
  final/
    medium/
      raw/
      summary/
      plots/
      resources/
      notes/
```

Die Unterordner haben folgende Bedeutung:

| Ordner | Inhalt |
|---|---|
| `raw/` | Rohdaten der einzelnen Locust-Läufe |
| `summary/` | zusammengeführte und aggregierte CSV-Auswertungen |
| `plots/` | erzeugte Diagramme für die Bachelorarbeit |
| `resources/` | optionale Ressourcenmessungen wie CPU, RAM und I/O |
| `notes/` | Notizen zu Auffälligkeiten während einzelner Messläufe |

Die Dateinamen der finalen Locust-Exporte sollen System, Datensatz, Laststufe und Wiederholung enthalten.

Beispiele:

```text
postgres_medium_u005_r1_stats.csv
postgres_medium_u005_r2_stats.csv
postgres_medium_u005_r3_stats.csv

mongo_medium_u005_r1_stats.csv
mongo_medium_u005_r2_stats.csv
mongo_medium_u005_r3_stats.csv
```

Für die weiteren Laststufen werden entsprechende Bezeichnungen verwendet:

```text
u005
u010
u025
u050
u075
u100
```

## 9. Zentrale Metriken

Für die Bewertung des Leistungs- und Stabilitätsverhaltens werden folgende Hauptmetriken verwendet:

| Metrik | Bedeutung |
|---|---|
| Requests/s | erfolgreicher Durchsatz |
| Median-Latenz | typisches Antwortzeitverhalten |
| p95-Latenz | obere Latenzbereiche |
| p99-Latenz | Tail-Latenz |
| Failure Count | absolute Fehleranzahl |
| Failure Rate | Anteil fehlgeschlagener Anfragen |

Diese Metriken bilden die Grundlage für die Beantwortung der Forschungsfragen. Der Durchsatz zeigt, wie viele Operationen erfolgreich verarbeitet werden. Median, p95 und p99 zeigen das Antwortzeitverhalten unter steigender Last. Fehleranzahl und Fehlerrate zeigen, ob das System unter höherer Last stabil bleibt oder Anfragen nicht mehr zuverlässig verarbeitet.

## 10. Ergänzende Metriken

Folgende Werte werden ergänzend betrachtet:

| Metrik | Verwendung |
|---|---|
| Average Response Time | zusätzliche Einordnung, aber keine zentrale Bewertungsmetrik |
| Max Response Time | Hinweis auf Ausreißer |
| Failures/s | ergänzende Betrachtung des Fehlerverhaltens |
| Exceptions | Prüfung technischer Fehler während des Laufs |
| CPU-Auslastung | ergänzende Interpretation möglicher Sättigung |
| RAM-Nutzung | ergänzende Interpretation des Ressourcenverhaltens |
| I/O-Aktivität | ergänzende Interpretation speicherbezogener Engpässe |

Ressourcenbezogene Werte dienen nicht als alleinige Bewertungskriterien. Sie werden genutzt, um beobachtete Latenzanstiege, Durchsatzgrenzen oder Fehlerverhalten besser einordnen zu können.

## 11. Auswertung über Wiederholungen

Für die finale Auswertung werden zwei Arten von Zusammenfassungen erzeugt.

```text
summary_raw.csv
summary_aggregated.csv
```

`summary_raw.csv` enthält die Werte jedes einzelnen Messlaufs.

`summary_aggregated.csv` enthält pro System und Laststufe aggregierte Werte über die drei Wiederholungen. Dazu gehören insbesondere Mittelwerte und Streuungswerte der zentralen Metriken.

Dadurch kann die Ergebnisdarstellung in der Bachelorarbeit auf aggregierten und damit stabileren Vergleichswerten basieren, während die Einzelmessungen weiterhin nachvollziehbar dokumentiert bleiben.

## 12. Diagramme für die Bachelorarbeit

Für die Bachelorarbeit werden vor allem aggregierte Diagramme über die Laststufen verwendet.

Geplante Hauptdiagramme:

| Diagramm | Inhalt |
|---|---|
| Durchsatz je Laststufe | PostgreSQL und MongoDB im Vergleich |
| Median-Latenz je Laststufe | typisches Antwortzeitverhalten |
| p95-Latenz je Laststufe | obere Latenzbereiche |
| p99-Latenz je Laststufe | Tail-Latenz |
| Fehlerrate je Laststufe | Stabilität unter steigender Last |
| p95-Latenz je Operation bei hoher Last | operationsbezogene Betrachtung, zum Beispiel bei 100 Usern |

Im Hauptteil der Bachelorarbeit sollen nicht alle Detaildiagramme gezeigt werden. Die zentrale Ergebnisdarstellung soll sich auf diejenigen Diagramme konzentrieren, die direkt zur Beantwortung der Forschungsfragen beitragen. Detailtabellen und operationsbezogene Zusatzwerte können bei Bedarf im Anhang dokumentiert werden.

## 13. Einordnung des finalen Messplans

Der finale Messplan ist bewusst so gewählt, dass er auf der vorhandenen lokalen Testumgebung realistisch ausführbar bleibt. Die Entscheidung für den `medium`-Datensatz und für sechs Laststufen bis 100 User soll einen reproduzierbaren Hauptvergleich ermöglichen.

Der Messplan erhebt keinen Anspruch darauf, produktive E-Commerce-Systeme vollständig nachzubilden. Er bildet vielmehr ein kontrolliertes, E-Commerce-nahes Belastungsszenario auf Datenbankebene ab. Dadurch können PostgreSQL und MongoDB unter identischen Rahmenbedingungen hinsichtlich Durchsatz, Latenzverhalten, Fehlerrate und Degradationsverlauf verglichen werden.


# Abschluss der finalen Medium-Messläufe

Nach Abschluss der technischen Probeläufe wurde das Datensatzprofil `medium` als finale Datengrundlage für den Hauptversuch verwendet. Der Datensatz umfasst 25 Kategorien, 50.000 Produkte, 50.000 Bestände, 5.000 Kunden, 5.000 aktive Warenkörbe und 10.032 Warenkorbpositionen. Initiale Bestellungen und initiale Bestellpositionen wurden nicht erzeugt, da Bestellungen erst während der checkoutnahen Lasttestoperationen entstehen.

Für die finalen Messläufe wurden PostgreSQL und MongoDB unter demselben E-Commerce-nahen Lastprofil V1 getestet. Das Lastprofil bestand aus den Operationen `product_list`, `product_detail`, `price_availability`, `cart_read`, `cart_update` und `checkout`. Die Gewichtung betrug 35 % für `product_list`, 25 % für `product_detail`, 15 % für `price_availability`, 5 % für `cart_read`, 15 % für `cart_update` und 5 % für `checkout`.

Die finalen Laststufen wurden auf 5, 10, 25, 50, 75 und 100 simulierte Locust-User festgelegt. Die zugehörigen Spawn-Rates betrugen 1, 2, 5, 10, 15 und 20 User pro Sekunde. Jeder Messlauf wurde 10 Minuten lang ausgeführt. Jede Laststufe wurde pro Datenbanksystem dreimal wiederholt. Insgesamt ergaben sich damit 36 finale Messläufe:

```text
6 Laststufen × 2 Datenbanksysteme × 3 Wiederholungen = 36 finale Messläufe
```

Vor jedem einzelnen Messlauf wurde die jeweilige Datenbank neu aus den gemeinsamen CSV-Dateien befüllt. Dadurch wurde sichergestellt, dass jeder Lauf mit demselben definierten Ausgangszustand startet. Dieses Vorgehen erhöht die Vergleichbarkeit der Messläufe, bildet jedoch keinen kontinuierlichen produktiven Langzeitbetrieb mit dauerhaft fortgeschriebenem Datenbestand ab.

Die finalen Rohdaten wurden im folgenden Ordner gespeichert:

```text
results/final/medium/raw/
```

Die zusammengefassten Ergebnisdateien wurden im folgenden Ordner gespeichert:

```text
results/final/medium/summary/
```

Erzeugte zentrale Dateien:

```text
summary_raw.csv
summary_aggregated.csv
summary_aggregated_backup.csv
```

Die finalen Diagramme wurden im folgenden Ordner erzeugt:

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

## Status der finalen Messläufe

Alle 36 finalen Messläufe wurden abgeschlossen. Die zugehörigen `failures.csv`- und `exceptions.csv`-Dateien enthielten bei allen gültigen Läufen nur Kopfzeilen. Damit wurden von Locust keine endgültig fehlgeschlagenen Operationen registriert. Die aggregierte Fehlerrate betrug in allen Laststufen und für beide Systeme 0,0000 %.

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

## Besondere Vorkommnisse während der finalen Messläufe

Während eines MongoDB-Laufs bei 50 Usern wurde versehentlich eine Terminaleingabe ausgelöst. Locust zeigte daraufhin eine abweichende Nutzerzahl beziehungsweise Spawn-Rate an. Dieser Lauf wurde abgebrochen, die zugehörigen Dateien wurden gelöscht und `mongo_medium_u050_r1` wurde nach erneutem Seeding sauber wiederholt. Nur der wiederholte Lauf wurde als gültiger Messlauf berücksichtigt.

Während eines PostgreSQL-Laufs bei 75 Usern wurde ebenfalls ein Terminaleingriff durch versehentlichen Rechtsklick ausgelöst. Der betroffene Lauf wurde abgebrochen, die zugehörigen Dateien wurden gelöscht und `postgres_medium_u075_r2` wurde nach erneutem Seeding sauber wiederholt. Nur der wiederholte Lauf wurde als gültiger Messlauf berücksichtigt.

Beim letzten PostgreSQL-Lauf `postgres_medium_u100_r3` erschien beim Herunterfahren eine psycopg-Warnung zum Rollback einer bereits terminierten Transaktion:

```text
another command is already in progress
```

Locust beendete den Lauf jedoch mit Exit Code 0. Die zugehörigen `failures.csv`- und `exceptions.csv`-Dateien enthielten nur Kopfzeilen. Die aggregierten Werte für PostgreSQL bei 100 Usern waren plausibel und zeigten keinen auffälligen Ausreißer. Der Lauf wurde daher als gültig eingeordnet.

## Aggregierte Gesamtergebnisse

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

## Sanity-Checks PostgreSQL

Nach dem letzten PostgreSQL-Lauf wurden Plausibilitätsprüfungen auf dem Datenbankzustand durchgeführt.

| Prüfung | Ergebnis |
|---|---:|
| Orders | 9.856 |
| Order Items | 29.367 |
| Aktive Warenkörbe | 5.000 |
| Negative Bestände | 0 |
| Produkte | 50.000 |
| Bestandsdatensätze | 50.000 |

Die Werte sind plausibel. Es wurden Bestellungen und Bestellpositionen erzeugt, die Anzahl aktiver Warenkörbe blieb bei 5.000, es existieren keine negativen Bestände, und die Produkt- sowie Bestandsanzahl blieb unverändert.

## Sanity-Checks MongoDB

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

Die Werte sind plausibel. Es wurden Bestellungen und eingebettete Bestellpositionen erzeugt, die Anzahl aktiver Warenkörbe blieb bei 5.000, es existieren keine negativen Bestände, und die Produktanzahl blieb unverändert. Die Gesamtzahl der Warenkörbe ergibt sich plausibel aus den initialen 5.000 aktiven Warenkörben und den 9.554 abgeschlossenen Checkouts. Die Anzahl der `checked_out`-Warenkörbe entspricht der Anzahl der Orders.

## Erste Beobachtungen

Der Durchsatz steigt über die Laststufen hinweg nahezu linear an. PostgreSQL und MongoDB liegen beim Durchsatz sehr nah beieinander. Bei 100 Usern erreicht PostgreSQL im Mittel 324,10 Requests pro Sekunde, MongoDB erreicht 318,27 Requests pro Sekunde.

Die Fehlerrate beträgt in allen Laststufen und bei beiden Systemen 0,0000 %. Für MongoDB ist dabei zu berücksichtigen, dass transiente Transaktionskonflikte im Checkout durch eine begrenzte Retry-Strategie behandelt werden. Erfolgreich wiederholte Operationen erscheinen nicht als Failure, ihre zusätzliche Ausführungszeit bleibt jedoch in den gemessenen Latenzen enthalten.

PostgreSQL zeigt über alle Laststufen hinweg niedrigere Median-, p95- und p99-Latenzen als MongoDB. Besonders deutlich wird der Unterschied bei 100 Usern. Dort liegt MongoDB bei einer p99-Latenz von 84,33 ms, während PostgreSQL bei 38,00 ms liegt.

Das operationsbezogene p95-Diagramm bei 100 Usern zeigt, dass insbesondere die checkoutnahe Operation bei MongoDB deutlich höhere p95-Latenzen aufweist als bei PostgreSQL. Auch `cart_update` ist bei MongoDB höher. Diese Beobachtung deutet darauf hin, dass die schreibenden beziehungsweise transaktionsnahen Operationen im gewählten MongoDB-Modell stärker zur erhöhten Tail-Latenz beitragen.

## Methodische Hinweise

Die Ergebnisse beziehen sich ausschließlich auf den definierten Messaufbau mit lokalem Laptop, getrennt ausgeführten Datenbanksystemen, Datensatzprofil `medium`, E-Commerce-nahem Lastprofil V1 und direkten datenbanknahen Locust-Operationen. Es wurden keine vollständige Shop-Architektur, kein Caching, kein Load Balancing, kein Clusterbetrieb und keine Replikations- oder Sharding-Szenarien untersucht.

Das Neu-Seeden vor jedem Messlauf erhöht Vergleichbarkeit und Reproduzierbarkeit, bildet aber keinen fortlaufenden Realbetrieb mit dauerhaft wachsendem Datenbestand ab.

Die Fehlerrate beschreibt endgültig fehlgeschlagene Locust-Operationen. Erfolgreich wiederholte MongoDB-Checkout-Operationen werden nicht als Failure gezählt, ihre zusätzliche Laufzeit bleibt jedoch in den Latenzmetriken enthalten.
