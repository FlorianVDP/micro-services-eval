from fastapi import FastAPI, Response
from pydantic import BaseModel
from uuid import uuid4, UUID
from typing import Literal
from urllib import request

app = FastAPI()


class Dish(BaseModel):
    id: UUID | None
    name: str
    description: str
    type: Literal["aperitif", "entree", "plat", "dessert", "boisson"]
    price: float
    quantity: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = uuid4()


class Menu(BaseModel):
    dishes: list[Dish]

    def get_dish(self, dish_id: UUID) -> Dish | None:
        for dish in self.dishes:
            if dish.id == dish_id:
                return dish

    def post_dish(self, dish_datas):
        self.dishes.append(dish_datas)
        pass

    def remove_dish(self, dish_id: UUID):
        self.dishes.remove(self.get_dish(dish_id))


class Order(BaseModel):
    id: UUID | None
    table_number: int
    status: bool | None
    dishes: list[UUID | None]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = uuid4()
        self.status = False


class OrdersList(BaseModel):
    orders: list[Order]

    def get_order(self, order_id: UUID) -> Order | None:
        for order in self.orders:
            if order.id == order_id:
                return order

    def post_order(self, order_datas):
        self.orders.append(order_datas)

    def remove_order(self, order_id: UUID):
        self.orders.remove(self.get_order(order_id))

    def get_order_dishes(self, order_id: UUID):
        dish_list: list[Dish] = []
        for dish in self.get_order(order_id).dishes:
            link = f"http://127.0.0.1:8000/dishes/{dish}"
            f = request.urlopen(link)
            myfile = f.data_open()
            dish_list.append(myfile)

        return dish_list


menu: Menu = Menu(
    dishes=[
        Dish(id=UUID('7ab35298-c4e4-4899-9c52-8249cbaaf064'),
             name="Hamburger et ses frites",
             description="Un petit menu pour les enfants de moins de 10ans",
             type="plat",
             price=10,
             quantity=3
             ),
        Dish(id=UUID('242dd9b0-bd9a-4974-979e-df006fbc353a'),
             name="Plat gastronomique",
             description="Un petit plat pour une belle gastro",
             type="plat",
             price=50,
             quantity=10
             ),
    ]
)

ordersList: OrdersList = OrdersList(
    orders=[
        Order(id=UUID('7b14ad1d-ff74-435a-9a99-9ec11433f31a'),
              table_number=9,
              status=False,
              dishes=[UUID('242dd9b0-bd9a-4974-979e-df006fbc353a')]
              )
    ]
)


# get, put, delete

class payloadDish(BaseModel):
    quantity: int


class payloadOrder(BaseModel):
    status: bool
    dishes_id: list[UUID | None]


# get
@app.get("/dishes")
async def get_dishies(token: int = 0):
    if token:
        return menu
    else:
        menu_client = []
        for menu_item in menu.dishes:
            if menu_item.quantity != 0:
                menu_client.append(menu_item)
        return menu_client


@app.get("/orders")
async def get_orders():
    return ordersList if ordersList.orders else Response(status_code=404)


@app.get("/dishes/{dish_id}")
async def get_dish(dish_id: UUID):
    dish = menu.get_dish(dish_id)
    return dish if dish else Response(status_code=404)


@app.get("/orders/{order_id}")
async def get_order(order_id: UUID):
    order = ordersList.get_order(order_id)
    return order if order else Response(status_code=404)


@app.get("/orders/{order_id}/dishes")
async def get_orders_dishes(order_id: UUID):
    order = ordersList.get_order_dishes(order_id)
    return order if order else Response(status_code=404)


# patch
@app.patch("/dishes/{dish_id}")
async def patch_dish(dish_id: UUID, my_payload: payloadDish):
    menu.get_dish(dish_id).quantity = my_payload.quantity
    return menu.get_dish(dish_id)


@app.patch("/orders/{order_id}")
async def patch_order(order_id: UUID, my_payload: payloadOrder):
    ordersList.get_order(order_id).status = my_payload.status
    ordersList.get_order(order_id).dishes = my_payload.dishes_id
    return ordersList.get_order(order_id)


# delete
@app.delete("/dishes/{dish_id}")
async def delete_dish(dish_id: UUID):
    menu.remove_dish(dish_id)
    return dish_id


@app.delete("/orders/{order_id}")
async def delete_order(order_id: UUID):
    ordersList.remove_order(order_id)
    return order_id


# post
@app.post("/dishes")
async def post_dish(new_dish: Dish):
    menu.post_dish(new_dish)
    return menu


@app.post("/orders")
async def post_order(new_order: Order):
    ordersList.post_order(new_order)
    return ordersList


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
