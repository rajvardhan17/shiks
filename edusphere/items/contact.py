from dataclasses import dataclass
from typing import Any


@dataclass
class ContactItem:
    admission_email: str | None = None
    general_email: str | None = None
    phone_numbers: list[str] = None
    email_addresses: list[str] = None
    whatsapp_number: str | None = None
    admission_helpline: str | None = None
    fax: str | None = None
    principal_director_name: str | None = None
    social_media_links: dict[str, Any] = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    address: str | None = None
    pin_code: str | None = None

    def __post_init__(self) -> None:
        if self.phone_numbers is None:
            self.phone_numbers = []
        if self.email_addresses is None:
            self.email_addresses = []
        if self.social_media_links is None:
            self.social_media_links = {}
