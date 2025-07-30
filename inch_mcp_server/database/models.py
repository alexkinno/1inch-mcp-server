"""SQLAlchemy models for 1inch MCP Server."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LimitOrder(Base):
    """SQLAlchemy model for 1inch limit orders."""
    
    __tablename__ = "limit_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blockchain_id = Column(Integer, nullable=False)
    src_token_name = Column(String(255), nullable=False)
    src_token_address = Column(String(42), nullable=False)  # Ethereum address length
    dst_token_name = Column(String(255), nullable=False)
    dst_token_address = Column(String(42), nullable=False)  # Ethereum address length
    price = Column(Numeric(38, 18), nullable=False)  # High precision for token prices
    expiration = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(38, 18), nullable=False)  # High precision for token amounts
    
    # Audit fields
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    def __repr__(self) -> str:
        return (
            f"<LimitOrder(id={self.id}, "
            f"blockchain_id={self.blockchain_id}, "
            f"src_token={self.src_token_name}, "
            f"dst_token={self.dst_token_name}, "
            f"price={self.price}, "
            f"amount={self.amount})>"
        )
