from dataclasses import dataclass


@dataclass
class InfrastructureItem:
    hostel: bool = False
    library: bool = False
    wifi: bool = False
    labs: bool = False
    gym: bool = False
    auditorium: bool = False
    sports: bool = False
    swimming_pool: bool = False
    medical: bool = False
    bank: bool = False
    atm: bool = False
    mess: bool = False
    cafeteria: bool = False
    parking: bool = False
    transport: bool = False
    conference_hall: bool = False
    seminar_hall: bool = False
    created_at: str | None = None
