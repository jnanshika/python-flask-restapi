from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

#create an instance of Flask application
app = Flask(__name__) 

#specifies the databse, Tells SQLAlchemy where to store the data.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

#creates an instance of SQLAlchemy tied to flask app and allow to create tables, models and run queries.
db = SQLAlchemy(app) 

#instance of flask_restful api tied to flask app. 
#Enables you to define RESTful routes and resources using classes instead of manual route decorators.
api = Api(app)

#model represent table in database. Each instance will correspond to new row in the table UserModel.
class UserModel(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self): 
        return f"User(name = {self.name}, email = {self.email})"

#creates a new parser object to extract and validate incoming request data.
user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

#Declares a dictionary that maps the model fields to their output types.
#Used by marshal_with to serialize the model's data into a JSON-friendly format when sending API responses.
userFields = {
    'id':fields.Integer,
    'name':fields.String,
    'email':fields.String,
}

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all() 
        return users 
    
    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        userExists = UserModel.query.filter_by(name=args.name).first() 
        if userExists:
            abort(404, message="User already exists")
        user = UserModel(name=args["name"], email=args["email"])
        db.session.add(user) 
        db.session.commit()
        users = UserModel.query.all()
        return users, 201
    
class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first() 
        if not user: 
            abort(404, message="User not found")
        return user 
    
    #update user by id
    @marshal_with(userFields)
    def post(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first() 
        if not user: 
            abort(404, message="User not found")
        user.name = args["name"]
        user.email = args["email"]
        db.session.commit()
        return user 
    
    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first() 
        if not user: 
            abort(404, message="User not found")
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users

    
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')

# @app.route('/')
# def home():
#     return '<h1>Flask REST API</h1>'

if __name__ == '__main__':
    app.run(debug=True) 