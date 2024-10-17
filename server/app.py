#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code Challenge</h1>"


class Restaurants(Resource):
    def get(self):
        restaurants = db.session.query(Restaurant).all()
        restaurant_list = [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]
        return make_response(jsonify(restaurant_list), 200)


class RestaurantById(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            restaurant_data = restaurant.to_dict(rules=(
                'id',
                'name',
                'address',
                'restaurant_pizzas',
                'restaurant_pizzas.id',
                'restaurant_pizzas.price',
                'restaurant_pizzas.pizza_id',
                'restaurant_pizzas.restaurant_id',
                'restaurant_pizzas.pizza',
                'restaurant_pizzas.pizza.id',
                'restaurant_pizzas.pizza.name',
                'restaurant_pizzas.pizza.ingredients',
            ))
            return make_response(jsonify(restaurant_data), 200)
        else:
            return make_response(jsonify({'error': 'Restaurant not found'}), 404)

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response('', 204)
        else:
            return make_response(jsonify({'error': 'Restaurant not found'}), 404)


class Pizzas(Resource):
    def get(self):
        pizzas = db.session.query(Pizza).all()
        pizza_list = [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas]
        return make_response(jsonify(pizza_list), 200)


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        pizza = db.session.get(Pizza, pizza_id)
        restaurant = db.session.get(Restaurant, restaurant_id)

        if not pizza or not restaurant:
            return make_response(jsonify({'errors': ['Invalid pizza_id or restaurant_id']}), 400)

        try:
            restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(restaurant_pizza)
            db.session.commit()

            restaurant_pizza_data = restaurant_pizza.to_dict(rules=(
                'id',
                'price',
                'pizza_id',
                'restaurant_id',
                'pizza',
                'pizza.id',
                'pizza.name',
                'pizza.ingredients',
                'restaurant',
                'restaurant.id',
                'restaurant.name',
                'restaurant.address',
            ))

            return make_response(jsonify(restaurant_pizza_data), 201)
        except ValueError:
            return make_response(jsonify({'errors': ['validation errors']}), 400)


# Adding Resources to API
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
