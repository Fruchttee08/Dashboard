import logging
import os
from lib.domain_class import Semester, Kurs, Klausur
from lib.repository_class import Datenbank


class Studiengang:
    # Hauptklasse, die die Logik für die Verwaltung der Kurse und Klausuren enthält
    def __init__(self):
        self.NAME = "Angewandte Künstliche Intelligenz"
        self.db = Datenbank()
        self.BESTANDEN = "bestanden"
        self.NICHT_BESTANDEN = "nicht bestanden"
        self.STORNIERT = "storniert"
        self.GEBUCHT = "gebucht"


    def klausur_buchen(self,kurs: Kurs, knr: int, kdat: str, semester_liste: list[Semester]) -> bool:
    # Bucht eine Klausur für einen Kurs, unter Berücksichtigung der sequentiellen Buchungsregeln
        idx = knr - 1
        if idx < 0 or idx > 2:
            logging.error(f"Fehler: ungültige Klausurnummer {knr}")
            return False

        # Für Klausur 1 gelten die normalen Regeln
        if idx == 0:
            if kurs.klausur[idx] is None:
                kurs.kstatus = self.GEBUCHT
                kurs.klausur[idx] = Klausur(datum=kdat, _ergebnis=0.0)
                self.db.speichern(semester_liste)
                return True
            else:
                logging.error(f"Fehler: Klausur {knr} wurde bereits gebucht.")
                return False

        # Für Klausur 2 und 3 muss die vorherige Klausur vorhanden und nicht bestanden sein
        prev = kurs.klausur[idx - 1]
        if prev is None:
            logging.error(f"Fehler: Klausur {knr} kann nicht gebucht werden. Vorherige Klausur {knr-1} fehlt.")
            return False

        # Warten auf Bewertung: ergebnis == 0.0 bedeutet noch nicht bewertet
        if prev.ergebnis == 0.0:
            logging.error(f"Fehler: Klausur {knr} kann nicht gebucht werden. Klausur {knr-1} ist noch nicht bewertet.")
            return False

        # Wenn vorherige bestanden wurde, darf die nächste nicht gebucht werden
        if prev.ergebnis < 4.1:
            logging.error(f"Fehler: Klausur {knr} kann nicht gebucht werden. Klausur {knr-1} wurde bestanden.")
            return False

        # Nun prüfen, ob die gewünschte Klausur bereits existiert
        if kurs.klausur[idx] is None:
            kurs.kstatus = self.GEBUCHT
            kurs.klausur[idx] = Klausur(datum=kdat, _ergebnis=0.0)
            self.db.speichern(semester_liste)
            return True
        else:
            logging.error(f"Fehler: Klausur {knr} wurde bereits gebucht.")
            return False
        

    def ergebnis_aktualisieren(self, kurs: Kurs, knr: int, knote: float, semester_liste: list[Semester]) -> bool:
        # Aktualisiert das Ergebnis einer Klausur und setzt den Kursstatus entsprechend
        idx = knr - 1
        if idx < 0 or idx > 2:
            logging.error(f"Fehler: ungültige Klausurnummer {knr}")
            return False
        if kurs.klausur[idx] is not None:
            kurs.klausur[idx].ergebnis = knote
            # Einfache Statuslogik: Note >= 4.1 => Nicht bestanden
            if knote >= 4.1:
                kurs.kstatus = self.NICHT_BESTANDEN
            else:   
                kurs.kstatus = self.BESTANDEN
            self.db.speichern(semester_liste)
            return True
        else:
            logging.error(f"Fehler: Ergebnis {knote} für Klausur {knr} konnte nicht gebucht werden.")
            return False

    def klausur_stornieren(self, kurs, knr, semester_liste) -> bool:
        # Storniert eine Klausur und setzt den Kursstatus auf "storniert"
        idx = knr - 1
        if idx < 0 or idx > 2:
            logging.error(f"Fehler: Klausur {knr} existiert nicht.")
            return False
        if kurs.klausur[idx] is not None:
            # Status setzen und die Klausur entfernen
            kurs.kstatus = self.STORNIERT
            kurs.klausur[idx] = None
            self.db.speichern(semester_liste)
            return True
        else:
            logging.error(f"Fehler: Klausur {knr} existiert nicht oder wurde bereits storniert.")
            return False

    def lade_datenbank(self):
        # Lädt die Kursdatenbank und gibt eine Liste von Semester-Objekten zurück
        return self.db.lade_kurse()
