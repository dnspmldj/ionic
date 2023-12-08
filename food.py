import streamlit as st

from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

if __name__ == '__main__':
    app.run(debug=True)

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))
    calories = db.Column(db.Float)

from flask import Flask
from flask_restful import Api
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app)
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from flask_restful import Resource, reqparse
from models import Food, db

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Name of the food')
parser.add_argument('category', type=str)
parser.add_argument('calories', type=float)

class FoodResource(Resource):
    def get(self, food_id):
        food = Food.query.get_or_404(food_id)
        return {'id': food.id, 'name': food.name, 'category': food.category, 'calories': food.calories}

    def put(self, food_id):
        args = parser.parse_args()
        food = Food.query.get_or_404(food_id)
        food.name = args['name']
        food.category = args['category']
        food.calories = args['calories']
        db.session.commit()
        return {'message': 'Food updated successfully'}

    def delete(self, food_id):
        food = Food.query.get_or_404(food_id)
        db.session.delete(food)
        db.session.commit()
        return {'message': 'Food deleted successfully'}

class FoodListResource(Resource):
    def get(self):
        foods = Food.query.all()
        return [{'id': food.id, 'name': food.name, 'category': food.category, 'calories': food.calories} for food in foods]

    def post(self):
        args = parser.parse_args()
        new_food = Food(name=args['name'], category=args['category'], calories=args['calories'])
        db.session.add(new_food)
        db.session.commit()
        return {'message': 'Food added successfully'}

api.add_resource(FoodListResource, '/foods')
api.add_resource(FoodResource, '/foods/<int:food_id>')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
