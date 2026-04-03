import uuid
from sqlalchemy import Column, String, Date, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key = True, default= uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key = True, default= uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    date = Column(Date, nullable=False)

    amount_due = Column(Numeric(10,2), nullable=False)
    amount_paid = Column(Numeric(10,2), nullable=False)

    payment_mode = Column(String)
    note = Column(String)
    created_at = Column(DateTime, server_default = func.now())


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    invoice_number = Column(String,  unique=True)
    issued_at = Column(DateTime, server_default=func.now())


#  Date of transaction, payment mode, amount previously due, amount paid

# Rent based schema updation
class Rent(Base):
    __tablename__ = "rent"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(String, default="NayaRaipur")

    txn_id = Column(String, unique=True)
    note = Column(String)

    amount = Column(Numeric(10,2), default=3000)
    status = Column(String, default="pending")  # pending / confirmed
    confirmed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())