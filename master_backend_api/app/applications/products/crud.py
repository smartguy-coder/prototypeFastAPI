from applications.base_crud import BaseCRUD
from applications.products.models import Category, Product, Order, OrderProduct
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryDBManager(BaseCRUD):

    def __init__(self):
        self.model = Category


class ProductDBManager(BaseCRUD):

    def __init__(self):
        self.model = Product


class OrderDBManager(BaseCRUD):

    def __init__(self):
        self.model = Order


class OrderProductDBManager(BaseCRUD):

    def __init__(self):
        self.model = OrderProduct

    async def set_quantity_and_price(self, product: Product, order_id: int, quantity: int, session: AsyncSession):
        # todo use for decrease
        order_product: OrderProduct = await self.get_or_create(
            session=session, order_id=order_id, product_id=product.id
        )
        order_product.quantity += quantity
        order_product.price = product.price
        session.add(order_product)
        await session.commit()
        await session.refresh(order_product)


category_manager = CategoryDBManager()
product_manager = ProductDBManager()
order_manager = OrderDBManager()
order_product_manager = OrderProductDBManager()
