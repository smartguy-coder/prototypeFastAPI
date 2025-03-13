from applications.base_crud import BaseCRUD
from applications.products.models import Category, Product, Order, OrderProduct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, delete, desc, func, or_, select, update, exists
from sqlalchemy.orm import selectinload


class CategoryDBManager(BaseCRUD):

    def __init__(self):
        self.model = Category


class ProductDBManager(BaseCRUD):

    def __init__(self):
        self.model = Product


class OrderDBManager(BaseCRUD):

    def __init__(self):
        self.model = Order

    async def get_order_with_product(self, order_id: int, session: AsyncSession):
        """
        Це стандартна поведінка SQLAlchemy при joinedload(), оскільки:

        Якщо використовується "один-до-багатьох" (Order -> OrderProduct), SQLAlchemy окремо витягує order_products,
        щоб уникнути дублювання рядків.

        """
        result = await session.execute(
            select(self.model)
            .options(selectinload(self.model.order_products).selectinload(OrderProduct.product))
            .filter(self.model.id == order_id)
            .filter(OrderProduct.quantity > 0)
        )

        order = result.scalars().first()
        order.order_products = [op for op in order.order_products if op.quantity > 0]
        return order


class OrderProductDBManager(BaseCRUD):

    def __init__(self):
        self.model = OrderProduct

    async def set_quantity_and_price(self, product: Product, order_id: int, quantity: int, session: AsyncSession):
        # todo use for decrease
        order_product: OrderProduct = await self.get_or_create(
            session=session, order_id=order_id, product_id=product.id
        )
        order_product.quantity += quantity
        if order_product.quantity < 0:
            order_product.quantity = 0  # we do not delete - leave it as a log
        order_product.price = product.price
        session.add(order_product)
        await session.commit()
        await session.refresh(order_product)


category_manager = CategoryDBManager()
product_manager = ProductDBManager()
order_manager = OrderDBManager()
order_product_manager = OrderProductDBManager()
