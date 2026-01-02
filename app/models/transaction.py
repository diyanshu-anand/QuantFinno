# from sqlalchemy import Column, Integer, String, Float, Date, DateTime
# from sqlalchemy.sql import func
# from app.database import Base


# class Transaction(Base):
#     __tablename__ = "transactions"

#     id = Column(Integer, primary_key=True, index=True)

#     customer_id = Column(String, index=True, nullable=False)

#     invoice_id = Column(String, unique=True, index=True, nullable=False)

#     transaction_date = Column(Date,index=True, nullable=False)

#     amount_due = Column(Float, nullable=False)

#     amount_paid= Column(Float, nullable=False)

#     payment_mode = Column(String, nullable=False) #cash /upi/ bank

#     description = Column(String, nullable=True)

#     created_at = Column(DateTime(timezone=True), server_default=func.now())

