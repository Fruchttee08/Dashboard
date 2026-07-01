import os
import json
import logging
from .domain_class import Semester, Kurs, Klausur
from dataclasses import asdict

class JsonRepository():
    # Verwaltet das Laden und Speichern der Kursdaten in einer JSON-Datei
    def __init__(self):
        self.pfad = os.path.join(os.path.dirname(__file__), "database.json")

    def speichern(self, semester_liste):
        dict_kurse = [asdict(s) for s in semester_liste]

        with open(self.pfad, "w", encoding="utf-8") as f:
            json.dump(dict_kurse, f, indent=4, ensure_ascii=False)

        logging.info("Datenbank erfolgreich aktualisiert.")

    @staticmethod
    def _kurs_aus_dict(kurs_data):
        # Erstellt ein Kurs-Objekt aus einem Dictionary, das die Kursinformationen enthält
        kurs = Kurs(
            kurscode=kurs_data.get("kurscode", ""),
            kursname=kurs_data.get("kursname", ""),
            ects=kurs_data.get("ects", 0),
            kstatus=kurs_data.get("kstatus", "")
        )
        kurs.klausur = [None, None, None]
        for i, klausur_data in enumerate(kurs_data.get("klausur", [])):
            if i < 3 and klausur_data is not None:
                kurs.klausur[i] = Klausur(
                    datum=klausur_data.get("datum", ""),
                    _ergebnis=klausur_data.get("_ergebnis", 0.0)
                )
        return kurs

    @classmethod
    def _semester_aus_dict(cls, item):
        # Erstellt ein Semester-Objekt aus einem Dictionary, das die Semesterinformationen enthält
        semester_nr = item.get("semester", 0)
        kurse_roh = item.get("kurse", [])

        if isinstance(kurse_roh, dict):
            kurse = [cls._kurs_aus_dict(kurse_roh)]
        else:
            kurse = [cls._kurs_aus_dict(k) for k in kurse_roh]

        for kurs in kurse:
            kurs.semester = semester_nr

        return Semester(semester_nr, kurse)

    @staticmethod
    def _semester_gruppieren(semester_liste):
        # Gruppiert die Kurse nach Semester, falls sie nicht bereits gruppiert sind
        gruppiert = {}
        reihenfolge = []
        for semester in semester_liste:
            if semester.semester not in gruppiert:
                gruppiert[semester.semester] = []
                reihenfolge.append(semester.semester)
            gruppiert[semester.semester].extend(semester.kurse)
        return [Semester(nr, gruppiert[nr]) for nr in reihenfolge]

    def lade_kurse(self):
        # Lädt die Kursdaten aus der JSON-Datei und erstellt eine Liste von Semester-Objekten
        try:
            with open(self.pfad, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.info("Datenbank nicht gefunden oder ungültig. Standardkursliste wird geladen.")
            return self._hole_kursliste()

        if not data:
            return self._hole_kursliste()

        semester_liste = [self._semester_aus_dict(item) for item in data]
        if not isinstance(data[0].get("kurse"), list):
            semester_liste = self._semester_gruppieren(semester_liste)

        logging.info("Datenbank erfolgreich geladen.")
        return semester_liste

    @staticmethod
    def _hole_kursliste():
        # Gibt eine Standardliste von Kursen zurück, falls die Datenbank nicht gefunden oder ungültig ist
        return [
            Semester(1, [
                Kurs("DLBDSEAIS01-01_D", "Artificial Intelligence", 5, "aktiv"),
                Kurs("DLBDSIPWP01_D", "Einführung in die Programmierung mit Python", 5, "aktiv"),
                Kurs("DLBBIMD01", "Mathematik: Analysis", 5, "aktiv"),
            ]),
            Semester(2, [
                Kurs("DLBWIRITT01", "Einführung in das wissenschaftliche Arbeiten für IT und Technik", 5, "aktiv"),
                Kurs("DLBDSOOFPP01_D", "Projekt: Objektorientierte und funktionale Programmierung mit Python", 5, "aktiv"),
                Kurs("WAHLPFLICHTBEREICH D", "Kollaboratives Arbeiten", 5, "aktiv"),
            ]),
            Semester(3, [
                Kurs("DLBBIM01", "Mathematik: Lineare Algebra", 5, "aktiv"),
                Kurs("DLBDSSPDS01_D", "Statistik - Wahrscheinlichkeit und deskriptive Statistik", 5, "aktiv"),
                Kurs("DLBDSSIS01_D", "Statistik - Induktive Statistik", 5, "aktiv"),
            ]),
            Semester(4, [
                Kurs("DLBAIINLP01_D", "Einführung in NLP", 5, "aktiv"),
                Kurs("DLBAIPNLP01_D", "Projekt: NLP", 5, "aktiv"),
                Kurs("WAHLPFLICHTBEREICH D", "Digitale Business-Modelle", 5, "aktiv"),
            ]),
            Semester(5, [
                Kurs("DLBDSMLSL01_D", "Maschinelles Lernen - Supervised Learning", 5, "aktiv"),
                Kurs("DLBDSMLUSL01_D", "Maschinelles Lernen - Unsupervised Learning und Feature Engineering", 5, "aktiv"),
                Kurs("DLBDSNNDL01-01_D", "Neuronale Netze und Deep Learning", 5, "aktiv"),
            ]),
            Semester(6, [
                Kurs("DLBAIICV01_D", "Einführung in Computer Vision", 5, "aktiv"),
                Kurs("DLBAIPCV01_D", "Projekt: Computer Vision", 5, "aktiv"),
                Kurs("WAHLPFLICHTBEREICH D", "Projekt: Digitale Business-Modelle", 5, "aktiv"),
            ]),
            Semester(7, [
                Kurs("DLBAIIRL01_D", "Einführung in das Reinforcement Learning", 5, "aktiv"),
                Kurs("DLBISIC01", "Einführung in Datenschutz und IT-Sicherheit", 5, "aktiv"),
                Kurs("DLBDSCC01-01_D", "Cloud Computing", 5, "aktiv"),
            ]),
            Semester(8, [
                Kurs("DLBAIBESEI01_D", "Seminar: Ethische Innovation", 5, "aktiv"),
                Kurs("DLBSEPCP01_D", "Projekt: Cloud Programming", 5, "aktiv"),
                Kurs("WAHLPFLICHTBEREICH D", "Projekt: KI-Exzellenz mit kreativen Prompt-Techniken", 5, "aktiv"),
            ]),
            Semester(9, [
                Kurs("DLBAIPEAI01_D", "Projekt: Edge AI", 5, "aktiv"),
                Kurs("WAHLPFLICHTBEREICH A", "Augmented, Mixed und Virtual Reality", 10, "aktiv"),
                Kurs("WAHLPFLICHTBEREICH B", "Human-Computer Interaction", 10, "aktiv"),
                Kurs("WAHLPFLICHTBEREICH D", "Projekt: Generative KI im Unternehmenskontext", 5, "aktiv"),
            ]),
            Semester(10, [
                Kurs("WAHLPFLICHTBEREICH C", "Advanced Data Analysis", 10, "aktiv"),
                Kurs("DLBDSME01_D", "Model Engineering", 5, "aktiv"),
            ]),
            Semester(11, [
                Kurs("WAHLPFLICHTBEREICH D", "Project: Digitalization and Automation Hackathon", 5, "aktiv"),
            ]),
            Semester(12, [
                Kurs("BBAK01", "Bachelorarbeit", 9, "aktiv"),
                Kurs("BBAK02", "Kolloquium", 1, "aktiv"),
            ]),
        ]
