from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtCharts import (
    QChart,
    QChartView,
    QPieSeries,
    QBarSet,
    QBarSeries,
    QBarCategoryAxis,
    QValueAxis,
    QLineSeries,
    QCategoryAxis,
)

class Dashboard():
    # Serviceklasse für die Erstellung und Aktualisierung von Diagrammen im Dashboard
    # Zentrale Farbpalette für ein einheitliches Dashboard-Design (PySide6 QColor)
    COLOR_BESTANDEN = QColor("#27ae60")  # Angenehmes Grün
    COLOR_GEBUCHT = QColor("#2980b9")    # Blau für "Aktiv" / "Gebucht" / "Geplant"
    COLOR_STORNIERT = QColor("#c0392b")   # Rot für "Nicht bestanden" / "Storniert"
    COLOR_NEUTRAL = QColor("#7f8c8d")    # Grau für neutrale Werte
    

    def update_chart_gesamtfortschritt(self, kurse):
        # Erstellt ein Tortendiagramm, das den Gesamtfortschritt in ECTS-Punkten nach Kursstatus darstellt.
        chart = QChart()
        chart.setTitle("Gesamtfortschritt (ECTS nach Status)")

        series = QPieSeries()

        # Dictionaries zum Sammeln der ECTS pro Status
        status_ects = {
            "bestanden": 0,
            "gebucht": 0,
            "nicht bestanden/storniert": 0,
            "aktiv": 0
        }

        # ECTS-Punkte aufgrund des Kursstatus summieren
        for kurs in kurse:
            status_lower = kurs.kstatus.lower() 
            if status_lower == "bestanden":
                status_ects["bestanden"] += kurs.ects
            elif status_lower == "gebucht":
                status_ects["gebucht"] += kurs.ects
            elif status_lower == "nicht bestanden" or status_lower == "storniert":
                status_ects["nicht bestanden/storniert"] += kurs.ects
            else:
                status_ects["aktiv"] += kurs.ects

        # Die berechneten Anteile in die PieSeries einfügen
        for status_bezeichnung, ects in status_ects.items():
            if ects > 0: # Nur Segmente erstellen, die auch ECTS-Punkte haben
                slice_segment = series.append(f"{status_bezeichnung} ({ects} ECTS)", ects)
                
                # Einheitliche Farbzuweisung via Klassenattribute
                # Enumerationen wurden beim Speichern eingeführt, daher wird hier der Status in Kleinbuchstaben nur noch verglichen
                if status_bezeichnung == "bestanden":
                    slice_segment.setBrush(self.COLOR_BESTANDEN)
                elif status_bezeichnung == "gebucht":
                    slice_segment.setBrush(self.COLOR_GEBUCHT)
                elif status_bezeichnung == "nicht bestanden/storniert":
                    slice_segment.setBrush(self.COLOR_STORNIERT)
                else:
                    slice_segment.setBrush(self.COLOR_NEUTRAL)
                
                slice_segment.setLabelVisible(True)

        chart.addSeries(series)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing) # Kantenglättung für PySide6
        
        return chart_view

    def update_chart_studienverlauf(self, kurse):
        # Erstellt ein Balkendiagramm, das den Studienverlauf in ECTS-Punkten nach Semester darstellt.
        chart = QChart()
        chart.setTitle("Studienverlauf: ECTS nach Semester")

        semester_ects_geplant = {}
        semester_ects_erreicht = {}

        for kurs in kurse:
            sem = kurs.semester
            if sem not in semester_ects_geplant:
                semester_ects_geplant[sem] = 0
                semester_ects_erreicht[sem] = 0
            
            # Alle ECTS des Semesters summieren
            semester_ects_geplant[sem] += kurs.ects
            
            # Nur bestanden Kurse als erreicht werten
            if kurs.kstatus.lower() == "bestanden":
                semester_ects_erreicht[sem] += kurs.ects

        sorted_semesters = sorted(semester_ects_geplant.keys())
        
        # Daten-Sets für das Diagramm erstellen
        set_geplant = QBarSet("Geplant")
        set_erreicht = QBarSet("Erreicht")
        
        # Farben an die Farbpalette anpassen
        set_geplant.setBrush(self.COLOR_NEUTRAL)
        set_erreicht.setBrush(self.COLOR_BESTANDEN)
        
        categories = []
        for sem in sorted_semesters:
            categories.append(f"Sem {sem}")
            set_geplant.append(semester_ects_geplant[sem])
            set_erreicht.append(semester_ects_erreicht[sem])

        series = QBarSeries()
        series.append(set_geplant)
        series.append(set_erreicht)
        chart.addSeries(series)

        # X-Achse (Semester)
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        # Y-Achse (ECTS Punkte) dynamisch anhand des Maximums anpassen
        max_ects = max(semester_ects_geplant.values()) if semester_ects_geplant else 30
        axis_y = QValueAxis()
        axis_y.setRange(0, max_ects + 5)
        axis_y.setTickCount(int((max_ects + 5) / 5) + 1)
        axis_y.setTitleText("ECTS Punkte")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        # Labels auf den Balken anzeigen und Legende konfigurieren
        series.setLabelsVisible(True)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        return chart_view

    def update_chart_notendifferenz(self, kurse, zielnote):
        # Erstellt ein Balkendiagramm, das die Notendifferenz zur Zielnote pro Semester und insgesamt darstellt.
        chart = QChart()
        chart.setTitle(f"Notendifferenz zur Zielnote ({zielnote:.1f})")

        semester_noten = {}
        alle_noten = []

        # 1. Noten pro Semester und für Gesamt sammeln
        for kurs in kurse:
            letzte_note = None
            for k in kurs.klausur:
                if k is not None and k.ergebnis > 0.0:
                    letzte_note = k.ergebnis

            if letzte_note is not None:
                sem = kurs.semester
                if sem not in semester_noten:
                    semester_noten[sem] = []
                semester_noten[sem].append(letzte_note)
                alle_noten.append(letzte_note)

        # 2. Balken-Set für die Differenz erstellen
        set_delta = QBarSet("Δ (Schnitt - Zielnote)")
        set_delta.setBrush(self.COLOR_BESTANDEN)
        
        kategorien = []

        # Pro Semester Schnitt und Differenz berechnen
        for sem in sorted(semester_noten.keys()):
            noten = semester_noten[sem]
            schnitt = sum(noten) / len(noten)
            delta = schnitt - zielnote

            delta = round(delta, 2)
            kategorien.append(f"Sem {sem}")
            set_delta.append(delta)

        # Gesamtschnitt berechnen und hinzufügen
        if alle_noten:
            gesamt_schnitt = sum(alle_noten) / len(alle_noten)
            delta_gesamt = round(gesamt_schnitt - zielnote, 2)
            kategorien.append("Gesamt")
            set_delta.append(delta_gesamt)

            #Füge Gesamtschnitt als Label hinzu
            set_delta.setLabel(f"Δ (Schnitt - Zielnote) | Gesamtschnitt: {gesamt_schnitt:.2f}")
        else:
            kategorien.append("Keine Noten")
            set_delta.append(0.0)

        series = QBarSeries()
        series.append(set_delta)
        chart.addSeries(series)

        # X-Achse (Kategorien)
        axis_x = QBarCategoryAxis()
        axis_x.append(kategorien)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        # Y-Achse (Notenpunkte Differenz)
        axis_y = QValueAxis()
        axis_y.setRange(-2.0, 2.0)
        axis_y.setTitleText("Abweichung (Negativ = Besser)")
        axis_y.setLabelFormat("%.2f")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        # Darstellung optimieren
        series.setLabelsVisible(True)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        return chart_view

    def update_chart_notenentwicklung(self, kurse):
        # Erstellt ein Liniendiagramm, das die Notenentwicklung der letzten 5 Prüfungen darstellt.
        chart = QChart()
        chart.setTitle("Notenentwicklung (letzte 5 Prüfungen)")

        exams = []
        for kurs in kurse:  # Iteriert durch die übergebenen Kurse
            for k in kurs.klausur:
                if k is not None and getattr(k, "ergebnis", 0.0) > 0.0 and getattr(k, "datum", ""):
                    date = QDate.fromString(k.datum, Qt.DateFormat.ISODate)
                    if not date.isValid():
                        date = QDate.fromString(k.datum, "dd.MM.yyyy")
                    if not date.isValid():
                        continue

                    # Wir speichern das QDate-Objekt für die Sortierung und den String für die Anzeige
                    exams.append({
                        "kursname": kurs.kursname,
                        "kurscode": kurs.kurscode,
                        "qdate": date,
                        "datum_str": date.toString("dd.MM.yyyy"),
                        "note": float(k.ergebnis),
                    })

        series = QLineSeries()
        series.setName("Klausurergebnisse")
        pen = QPen(self.COLOR_BESTANDEN)
        pen.setWidth(3)
        series.setPen(pen)

        if not exams:
            chart.addSeries(series)
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            return chart_view

        # Sortiert die Prüfungen aufsteigend nach Datum
        exams.sort(key=lambda x: x["qdate"])
        # Schneidet die letzten 6 Prüfungen ab, um die Übersichtlichkeit zu wahren (Labels werden nur für 5 Prüfungen angezeigt)
        exams = exams[-6:]

        chart.addSeries(series)

        # X-Achse für Kategorien (Kurs & Datum)
        axis_x = QCategoryAxis()
        axis_x.setTitleText("Kurse (sortiert nach Prüfungsdatum)")
        
        #Drehung der Labels für bessere Lesbarkeit
        axis_x.setLabelsAngle(-45)  
        chart.margins().setBottom(60)

        for i, exam in enumerate(exams):
            series.append(i, exam["note"])
            label = f'{exam["kursname"]}'
            axis_x.append(label, i)

        # Bereich der X-Achse dynamisch anpassen
        axis_x.setRange(0, max(0, len(exams) - 1))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        # Y-Achse für die Notenskala (1.0 bis 5.0)
        axis_y = QValueAxis()
        axis_y.setRange(1.0, 5.0)
        axis_y.setTickCount(5)
        axis_y.setLabelFormat("%.1f")
        axis_y.setTitleText("Note")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        # Werte direkt an den Datenpunkten einblenden
        series.setPointsVisible(True)
        series.setPointLabelsVisible(True)
        series.setPointLabelsFormat("@yPoint")  # Zeigt die Note direkt am Punkt an

        # Legende am unteren Rand positionieren
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        return chart_view
