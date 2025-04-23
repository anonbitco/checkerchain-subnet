from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    _id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    trust_score = Column(Float, default=0.0)
    check_chain_review_done = Column(Boolean, default=False)
    mining_done = Column(Boolean, default=False)
    rewards_distributed = Column(Boolean, default=False)

    predictions = relationship(
        "MinerPrediction", back_populates="product", cascade="all, delete-orphan"
    )


class MinerPrediction(Base):
    __tablename__ = "miner_predictions"
    __table_args__ = (
        UniqueConstraint("product_id", "miner_id", name="uix_product_miner"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, ForeignKey("products._id"), nullable=False)
    miner_id = Column(Integer, nullable=False)
    prediction = Column(Integer)

    product = relationship("Product", back_populates="predictions")
