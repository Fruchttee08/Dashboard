from dataclasses import dataclass, field

@dataclass
class Semester:
    semester: int
    kurse: list["Kurs"] = field(default_factory=list)


@dataclass
class Kurs:
    # Speichert die Informationen zu einem Kurs, inklusive Klausuren
    
    kurscode: str = ""
    kursname: str = ""
    ects: int = 0
    kstatus: str = ""
    semester: int = 0
    klausur: list = field(default_factory=lambda: [None, None, None])


@dataclass
class Klausur:
    # Speichert Informationen zu einer Klausur, inklusive Datum und Ergebnis
    datum: str
    _ergebnis: float = 0.0

    @property
    def ergebnis(self) -> float:
        return self._ergebnis

    @ergebnis.setter
    def ergebnis(self, value: float):
        self._ergebnis = round(float(value), 2)        