# -*- encoding: utf-8 -*-
"""
Python Aplication Template
Licence: GPLv3
"""

from flask import url_for, redirect, render_template, flash, g, session
# from flask_login import login_user, logout_user, current_user, login_required
from app import app
from forms import ExampleForm, LoginForm
from app.models import *
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

@app.route('/terrain', methods=['GET'])
def get_all_terrain():
  terrain = Terrain
  output = []
  for t in terrain.objects:
    output.append({'name' : t['name'], 'height' : t['height'], 'width' : t['width']})
  return jsonify({'result' : output})

@app.route('/terrain_create', methods=['POST'])
def add_terrain():
  terrain = Terrain
  name = request.json['name']
  height = request.json['height']
  width = request.json['width']
  t_id = terrain.objects.create(name=name,height=height,width=width)
  output = {'CREATED' : t_id['name'], 'height' : t_id['height'], 'width' : t_id['width']}
  return jsonify({'result' : output})


@app.route('/')
def index():
    # As a list to test debug toolbar
    #Terrain.objects.create(width=1,
    #	height=2,
    #	name='Test2')
    # Todo.objects().delete()  # Removes
    # Todo(title="Simple todo A ПЫЩЬ!", text="12345678910").save()  # Insert
    # Todo(title="Simple todo B", text="12345678910").save()  # Insert
    # Todo.objects(title__contains="B").update(set__text="Hello world")  # Update
    # todos = Todo.objects.all()
    return 'APIRest - MongoDB WeatherTasks Collections'



