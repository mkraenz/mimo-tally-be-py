import uuid
from datetime import datetime
from enum import Enum

from pydantic import UUID4
from pydantic import Field as PdField
from sqlalchemy import TIMESTAMP, Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

# this must come BEFORE we set up our model classes
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = SQLModel.metadata
metadata.naming_convention = NAMING_CONVENTION


# Shared properties
class UserBase(SQLModel):
    # TODO replace by softdelete
    is_active: bool = True


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    clerk_user_id: str | None = Field(None, unique=True, index=True)
    owned_settlements: list["Settlement"] = Relationship(
        back_populates="owner",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "Settlement.owner_id"},
    )
    received_settlements: list["Settlement"] = Relationship(
        back_populates="receiving_party",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "Settlement.receiving_party_id"},
    )
    sent_settlements: list["Settlement"] = Relationship(
        back_populates="sending_party",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "Settlement.sending_party_id"},
    )
    owned_disbursements: list["Disbursement"] = Relationship(
        back_populates="owner",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "Disbursement.owner_id"},
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class Currency(Enum):
    JPY = "JPY"
    EUR = "EUR"


class Disbursement(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(
        back_populates="owned_disbursements",
        sa_relationship_kwargs={"foreign_keys": "Disbursement.owner_id"},
    )

    paying_party_id: uuid.UUID = Field(
        nullable=False, foreign_key="user.id", ondelete="CASCADE"
    )
    paying_party: User | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Disbursement.paying_party_id"}
    )
    on_behalf_of_party_id: uuid.UUID = Field(
        nullable=False, foreign_key="user.id", ondelete="CASCADE"
    )
    on_behalf_of_party: User | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Disbursement.on_behalf_of_party_id"}
    )
    amount: float
    currency: str
    comment: str | None
    created_at: datetime | None = Field(
        None,
        sa_column=Column(DateTime, server_default=func.now(), nullable=False),
    )
    updated_at: datetime | None = Field(
        None,
        sa_column=Column(
            DateTime,
            server_default=func.now(),
            onupdate=func.current_timestamp(),
            nullable=False,
        ),
    )
    deleted_at: datetime | None = None
    settlement_id: uuid.UUID | None = Field(
        None,
        foreign_key="settlement.id",
        nullable=True,
    )
    settlement: "Settlement" = Relationship(
        back_populates="settled_disbursements",
        sa_relationship_kwargs={"foreign_keys": "Disbursement.settlement_id"},
    )


class Money(SQLModel):
    amount: float = PdField(
        description="The amount paid in the specified currency.",
        examples=[1.0],
        # TODO decimal places=2
    )
    currency: Currency = Field(Currency.EUR)


class DisbursementCreate(SQLModel):
    paying_party_id: UUID4 = Field(
        description="The user who is making the disbursement payment."
    )
    on_behalf_of_party_id: UUID4 = Field(
        description="The user on whose behalf the disbursement is made."
    )
    comment: str | None = Field(max_length=512, default=None)
    amount_paid: Money


class DisbursementPublic(SQLModel):
    # replacing the explicit ref by using from __future__ import annotations did not work. Type system was happy but fastapi broke ¯\_(ツ)_/¯
    @staticmethod
    def make(d: Disbursement) -> "DisbursementPublic":
        return DisbursementPublic(**d.model_dump(), amount_paid=Money(**d.model_dump()))

    id: uuid.UUID
    owner_id: uuid.UUID
    paying_party_id: uuid.UUID
    on_behalf_of_party_id: uuid.UUID
    comment: str | None
    created_at: datetime
    updated_at: datetime
    amount_paid: Money


class DisbursementsPublic(SQLModel):
    data: list[DisbursementPublic]
    total: int = Field(int, description="The total count of resources.")


class SettlementCreate(SQLModel):
    settled_disbursement_ids: list[str] = Field(min_length=1, unique_items=True)
    receiving_party_id: UUID4
    sending_party_id: UUID4
    settled_at: datetime
    amount_paid: float
    currency: Currency


class Settlement(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(
        back_populates="owned_settlements",
        sa_relationship_kwargs={"foreign_keys": "Settlement.owner_id"},
    )

    receiving_party_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    receiving_party: User | None = Relationship(
        back_populates="received_settlements",
        sa_relationship_kwargs={"foreign_keys": "Settlement.receiving_party_id"},
    )
    sending_party_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        ondelete="CASCADE",
    )
    sending_party: User | None = Relationship(
        back_populates="sent_settlements",
        sa_relationship_kwargs={"foreign_keys": "Settlement.sending_party_id"},
    )

    settled_disbursements: list[Disbursement] = Relationship(
        back_populates="settlement",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "Disbursement.settlement_id"},
    )

    amount_paid: float
    currency: str

    settled_at: datetime
    created_at: datetime | None = Field(
        None,
        sa_column=Column(TIMESTAMP, server_default=func.now(), nullable=False),
    )
    updated_at: datetime | None = Field(
        None,
        sa_column=Column(
            TIMESTAMP,
            server_default=func.now(),
            onupdate=func.current_timestamp(),
            nullable=False,
        ),
    )
    deleted_at: datetime | None = None


class SettlementPublic(SQLModel):
    @staticmethod
    def make(s: Settlement) -> "SettlementPublic":
        return SettlementPublic(**s.model_dump())

    id: uuid.UUID
    owner_id: uuid.UUID
    receiving_party_id: uuid.UUID
    sending_party_id: uuid.UUID
    amount_paid: float
    currency: str
    settled_at: datetime
    created_at: datetime
    updated_at: datetime


class SettlementsPublic(SQLModel):
    data: list[SettlementPublic]
    total: int = Field(int, description="The total count of resources.")
