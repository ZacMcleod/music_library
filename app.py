from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from marshmallow import post_load, fields, ValidationError
from dotenv import load_dotenv
from os import environ

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    album = db.Column(db.String(255))
    release_date = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'{self.year} {self.make} {self.model}'

# Schemas
class SongSchema(ma.Schema):
    id = fields.Integer(primary_key=True)
    title = fields.String(required=True)
    artist = fields.String(required=True)
    album = fields.String()
    release_date = fields.Date(required=True)
    genre = fields.String()

    class Meta:
        fields = ("id", "title", "artist", "album", "release_date", "genre")

    @post_load
    def create_song(self, data, **kwargs):
        return Song(**data)
    
song_schema = SongSchema()
song_schema = SongSchema(many=True)

# Resources
class SongListResource(Resource):
    def get(self):
        all_products = Song.query.all()
        return song_schema.dump(all_products)
    
    def post(self):
        form_data = request.get_json()
        try:
            new_product = song_schema.load(form_data)
            db.session.add(new_product)
            db.session.commit()
            return song_schema.dump(new_product), 201
        except ValidationError as err:
            return err.messages, 400

class SongResource(Resource):
    def get(self, product_id):
        song_from_db = Song.query.get_or_404(product_id)
        return song_schema.dump(song_from_db)
    
    def delete(self, product_id):
        song_from_db = Song.query.get_or_404(product_id)
        db.session.delete(song_from_db)
        db.session.commit()
        return '', 204

    def put(self, song_id):
        song_from_db = Song.query.get_or_404(song_id)
        
        if 'title' in request. json:
            song_from_db.name = request.json [ 'name' ]
        if 'artist' in request. json:
            song_from_db.description = request.json [ 'description' ]
        if 'albun' in request. json:
            song_from_db.price = request.json [ 'price' ]
        if 'release_date' in request. json:
            song_from_db.inventory_quantity = request.json [ 'inventory_quantity' ]
        if 'genre' in request. json:
            song_from_db.inventory_quantity = request.json [ 'inventory_quantity' ]

        db.session.commit()
        return song_schema.dump(song_from_db)

# Routes
api.add_resource(SongListResource, '/api/songs/')
api.add_resource(SongResource, '/api/songs/<int:song_id>/')
