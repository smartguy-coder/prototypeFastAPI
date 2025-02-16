from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from applications.base_model_and_mixins.base_mixins import (
    CreateUpdateAtMixin, PKMixin, UUIDMixin)
from applications.base_model_and_mixins.base_models import Base


class Category(PKMixin, CreateUpdateAtMixin, Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    products = relationship("Product", back_populates="category")

    def __str__(self):
        return f"Category {self.name} - #{self.id}"


class Product(PKMixin, CreateUpdateAtMixin, UUIDMixin, Base):
    __tablename__ = "products"

    title: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    images: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    main_image: Mapped[str] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )

    category = relationship("Category", back_populates="products")

    def __str__(self):
        return f"Product {self.title} - #{self.id}"
