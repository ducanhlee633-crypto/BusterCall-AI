from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base

class Pirate_Bounty(Base):
    __tablename__ = "pirate_bounty"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique = True, nullable = False)
    crew_name: Mapped[str] = mapped_column(String(100), unique = True, nullable = False)
    bounty: Mapped[int] = mapped_column(Integer, unique = True, nullable = False)
    