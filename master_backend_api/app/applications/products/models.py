from sqlalchemy import ForeignKey, String, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from applications.base_model_and_mixins.base_mixins import CreateUpdateAtMixin, PKMixin, UUIDMixin
from applications.base_model_and_mixins.base_models import Base


class Category(PKMixin, CreateUpdateAtMixin, Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    products = relationship("Product", back_populates="category")

    def __str__(self):
        return f"Category {self.name} - #{self.id}"


class Product(PKMixin, CreateUpdateAtMixin, UUIDMixin, Base):
    __tablename__ = "products"

    title: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(default="")
    images: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    main_image: Mapped[str] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)

    category = relationship("Category", back_populates="products")
    order_products = relationship("OrderProduct", back_populates="product")

    def __str__(self):
        return f"Product {self.title} - #{self.id}"


class Order(PKMixin, CreateUpdateAtMixin, UUIDMixin, Base):
    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_closed: Mapped[bool] = mapped_column(default=False)

    user = relationship("User", back_populates="orders")
    order_products = relationship(
        "OrderProduct",
        back_populates="order",
        # lazy=False,
        # lazy="joined",
        lazy="selectin",
    )

    @property
    def cost(self) -> float:
        _cost = sum([product.price * product.quantity for product in self.order_products])
        return _cost


class OrderProduct(PKMixin, CreateUpdateAtMixin, Base):
    __tablename__ = "order_products"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    price: Mapped[float] = mapped_column(default=0.0)
    quantity: Mapped[int] = mapped_column(default=0)

    product = relationship("Product", back_populates="order_products", lazy="selectin")
    order = relationship("Order", back_populates="order_products")

    __table_args__ = (UniqueConstraint("order_id", "product_id", name="uq_order_product"),)

    @property
    def total(self) -> float:
        return self.price * self.quantity

    def __str__(self):
        return f"OrderProduct {self.product.title} - #{self.id}, {self.quantity} >> {self.price} = {self.quantity * self.price}"

    __repr__ = __str__
