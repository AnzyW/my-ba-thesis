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
