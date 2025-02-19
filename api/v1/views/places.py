#!/usr/bin/python3
"""Defines a view for Place objects"""
from flask import Flask, jsonify, abort, request
from models import storage
from models.place import Place
from models.city import City
from models.user import User
from api.v1.views import app_views


@app_views.route('/cities/<city_id>/places', methods=['GET'])
def get_places(city_id):
    """Retrieves the list of all Place objects of a City"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = [place.to_dict() for place in
              storage.all(Place).values() if place.city_id == city_id]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'])
def get_place(place_id):
    """Retrieves a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'])
def delete_place(place_id):
    """Deletes a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'])
def create_place(city_id):
    """Creates a Place"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    if 'user_id' not in request.get_json():
        abort(400, description="Missing user_id")
    if 'name' not in request.get_json():
        abort(400, description="Missing name")

    user_id = request.get_json()['user_id']
    user = storage.get(User, user_id)
    if user is None:
        abort(404)

    data = request.get_json()
    data['city_id'] = city_id
    new_place = Place(**data)
    storage.new(new_place)
    storage.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'])
def update_place(place_id):
    """Updates a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()
    ignore_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignore_keys:
            setattr(place, key, value)
    storage.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'])
def places_search():
    """Search for places based on JSON criteria"""
    if not request.get_json():
        abort(400, description="Not a JSON")

    json_data = request.get_json()
    states = json_data.get('states', [])
    cities = json_data.get('cities', [])
    amenities = json_data.get('amenities', [])
    places = storage.all(Place).values()

    if request.get_json == 0:
        places = storage.all(Place).values()

    if states:
        places = [place for place in places if place.city.state_id in states]

    if cities:
        city_places = [place for place in places if place.city_id in cities]
        places += city_places

    if amenities:
        amenities_set = set(amenities)
        places = [place for place in places
                  if amenities_set.issubset(place.amenity_ids)]

    return jsonify([place.to_dict() for place in places])
