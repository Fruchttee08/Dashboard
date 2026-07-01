import logging
import sys
from pathlib import Path
import os
from PySide6.QtCore import QFile, Qt
from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader
from lib.controller_class import Studiengang
from lib.service_class import Dashboard




class MainWindow:
    # Verbindung zwischen GUI und Geschäftslogik
    def __init__(self, studiengang):
        # GUI laden und Datenbank initialisieren
        self.meinStudiengang = studiengang
        self.semester_liste = self.meinStudiengang.lade_json()
        self.kurse = []
        for semester in self.semester_liste:
            for kurs in semester.kurse:
                kurs.semester = semester.semester
                self.kurse.append(kurs)

        ui_path = os.path.join(os.path.dirname(__file__), "IU_dash.ui")
        ui_file = QFile(ui_path)
        if not ui_file.open(QFile.ReadOnly):
            logging.error(f"Fehler: Kann {ui_path} nicht öffnen. Existiert die Datei?")
            sys.exit(-1)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        if not self.window:
            logging.error("UI konnte nicht geladen werden")
            sys.exit(-1)
        
        # UI-Elemente referenzieren
        self.kursauswahl = self.window.comboBoxCourseSelect
        self.exam_auswahl = self.window.comboBoxExamSelect
        self.noteneingabe = self.window.doubleSpinBoxGradeExam
        self.klausur_datum_eingabe = self.window.dateEditCourseExam
        self.button__klausur_buchen = self.window.pushButtonExamadd
        self.button_klausur_ergebnisupdate = self.window.pushButtonExamresultupdate
        self.button__klausur_stornieren = self.window.pushButtonExamdelete
        self.tableWidgetKurse = self.window.tableWidgetCourses
        self.zielnote = self.window.doubleSpinBoxGradeGoal
        self.gridlayout = self.window.gridLayout
        self.gridlayout_2 = self.window.gridLayout_2
        self.gridlayout_3 = self.window.gridLayout_3
        self.gridlayout_4 = self.window.gridLayout_4

        # Signal-Slot-Verbindungen herstellen
        self.kursauswahl.currentTextChanged.connect(self._kurs_auswaehlen)
        self.button__klausur_buchen.clicked.connect(self._klausur_buchen)
        self.button_klausur_ergebnisupdate.clicked.connect(self._ergebnis_aktualisieren)
        self.button__klausur_stornieren.clicked.connect(self._klausur_stornieren)
        self.zielnote.valueChanged.connect(self._update_dashboard)
       

        for kurs in self.kurse:
            # Kurs als userData in ComboBox speichern
            self.kursauswahl.addItem(kurs.kursname, kurs)

        # Tabelleninhalt aktualisieren
        self._tabelle_aktualisieren()
        self._update_dashboard()
            

    # Event-Handler für Benutzerinteraktionen
    def _kurs_auswaehlen(self, text=None):
        # Text-Parameter wird vom Signal currentTextChanged übergeben
        selected_kurs = self.kursauswahl.currentData()
        if selected_kurs:
            logging.info(f"Ausgewählter Kurs: {selected_kurs.kursname} ({selected_kurs.kurscode})")


    def _klausur_buchen(self):
        # Klausur des aktuell gewählten Kurses buchen
        try: 
            selected_kurs = self.kursauswahl.currentData()
        except ValueError:
            logging.error("Ungültigen Kurs ausgewaehlt")
            return

        try:
            selected_klausur = int(self.exam_auswahl.currentText())
        except ValueError:
            logging.error("Ungültige Klausur ausgewaehlt")
            return

        # Prüfdatum im ISO-Format auslesen
        datum = self.klausur_datum_eingabe.date().toString(Qt.ISODate)

        logging.info(f"Kurs: {selected_kurs.kursname}, Klausur: {selected_klausur}, Datum: {datum}")

        erfolg = self.meinStudiengang.klausur_buchen(selected_kurs, selected_klausur, datum, self.semester_liste)

        if erfolg:
            logging.info("Klausur erfolgreich gebucht.")
        else:   
            logging.error("Fehler bei der Klausurbuchung.")
        self._tabelle_aktualisieren()
        self._update_dashboard()

    def _klausur_stornieren(self):
        # Klausur des aktuell ausgewählten Kurses stornieren
        try: 
            selected_kurs = self.kursauswahl.currentData()
        except ValueError:
            logging.error("Ungültigen Kurs ausgewaehlt")
            return
        try:
            selected_klausur = int(self.exam_auswahl.currentText())
        except ValueError:
            logging.error("Ungültige Klausur ausgewaehlt")
            return
        erfolg = self.meinStudiengang.klausur_stornieren(selected_kurs, selected_klausur, self.semester_liste)
        if erfolg:
            logging.info("Klausur erfolgreich storniert.")
        else:   
            logging.error("Fehler bei der Klausurstornierung.")
        self._tabelle_aktualisieren()
        self._update_dashboard()

    def _ergebnis_aktualisieren(self):
        # Aktualisiert das Ergebnis der ausgewählten Klausur des aktuell gewählten Kurses
        selected_kurs = self.kursauswahl.currentData()

        # Validierung: Kurs muss ausgewählt sein
        if not selected_kurs:
            logging.error("Kein Kurs ausgewählt.")
            return

        try:
            selected_klausur = int(self.exam_auswahl.currentText())
        except ValueError:
            logging.error("Ungültige Klausur-Auswahl.")
            return

        # Note aus dem Eingabefeld abrufen
        neue_note = self.noteneingabe.value()

        # Prüfung durchführen und Ergebnis aktualisieren
        erfolg = self.meinStudiengang.ergebnis_aktualisieren(selected_kurs, selected_klausur, neue_note, self.semester_liste)

        if erfolg:
            logging.info(f"Note {neue_note} für Klausur {selected_klausur} in {selected_kurs.kursname} gesetzt.")
        else:
            logging.error(f"Fehler: Klausur {selected_klausur} wurde für diesen Kurs noch nicht gebucht!")

        self._tabelle_aktualisieren()
        self._update_dashboard()

    def _tabelle_aktualisieren(self):
        # Tabelle mit Kursinformationen und Klausurdaten aktualisieren
        self.tableWidgetKurse.setRowCount(len(self.kurse))
        for row, kurs in enumerate(self.kurse):
            self.tableWidgetKurse.setItem(row, 0, QTableWidgetItem(str(kurs.semester)))
            self.tableWidgetKurse.setItem(row, 1, QTableWidgetItem(str(kurs.kurscode)))
            self.tableWidgetKurse.setItem(row, 2, QTableWidgetItem(str(kurs.kursname)))
            self.tableWidgetKurse.setItem(row, 3, QTableWidgetItem(str(kurs.ects)))
            self.tableWidgetKurse.setItem(row, 4, QTableWidgetItem(str(kurs.kstatus)))

            # Klausurdaten in Tabellenzeile eintragen (3 Spalten pro Klausur)
            for i, k in enumerate(kurs.klausur):
                base_col = 5 + i * 3
                if k is not None:
                    self.tableWidgetKurse.setItem(row, base_col, QTableWidgetItem("1"))
                    self.tableWidgetKurse.setItem(row, base_col + 1, QTableWidgetItem(str(k.datum)))
                    self.tableWidgetKurse.setItem(row, base_col + 2, QTableWidgetItem(f"{k.ergebnis:.2f}" if k.ergebnis > 0 else ""))
                else:
                    self.tableWidgetKurse.setItem(row, base_col, QTableWidgetItem(""))
                    self.tableWidgetKurse.setItem(row, base_col + 1, QTableWidgetItem(""))
                    self.tableWidgetKurse.setItem(row, base_col + 2, QTableWidgetItem(""))

    def _update_dashboard(self):
        # Aktualisiert die Dashboard-Diagramme basierend auf den aktuellen Kursdaten und der Zielnote
        _dashboard = Dashboard()

        chart_view = _dashboard.update_chart_gesamtfortschritt(self.kurse)
        self.gridlayout.addWidget(chart_view, 0, 0)
        chart_view_2 = _dashboard.update_chart_studienverlauf(self.kurse)
        self.gridlayout_2.addWidget(chart_view_2, 0, 0)
        chart_view_3 = _dashboard.update_chart_notendifferenz(self.kurse, self.zielnote.value())
        self.gridlayout_3.addWidget(chart_view_3, 0, 0)
        chart_view_4 = _dashboard.update_chart_notenentwicklung(self.kurse)
        self.gridlayout_4.addWidget(chart_view_4, 0, 0)
        


if __name__ == "__main__":
    class Applikation():
        def run(self):
            app = QApplication(sys.argv)
            # Stelle sicher, dass die Logdatei im Verzeichnis der Anwendung liegt.
            if getattr(sys, "frozen", False):
                base_dir = Path(sys.executable).resolve().parent
            else:
                base_dir = Path(__file__).resolve().parent
            base_dir.mkdir(parents=True, exist_ok=True)
            log_path = base_dir / "app.log"
            logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(str(log_path)), logging.StreamHandler()])
    
            #Erstelle Logik und übergieb sie an die Logik
            meinStudiengang = Studiengang()

            #Starte und schließe Anwendung
            mainwindow = MainWindow(meinStudiengang)
            mainwindow.window.showMaximized()
            sys.exit(app.exec())

    myApp = Applikation()
    myApp.run()
