# -*- encoding: utf-8 -*-
"""
Python Aplication Template
Licence: GPLv3
"""

from flask import url_for, redirect, render_template, flash, g, session
# from flask_login import login_user, logout_user, current_user, login_required
from app import app
#, lm
from forms import ExampleForm, LoginForm
from app.models import Terrain

@app.route('/')
def index():
    # As a list to test debug toolbar
    Terrain.objects.create(width=1,
    	height=2,
    	name='Test2')
    # Todo.objects().delete()  # Removes
    # Todo(title="Simple todo A ПЫЩЬ!", text="12345678910").save()  # Insert
    # Todo(title="Simple todo B", text="12345678910").save()  # Insert
    # Todo.objects(title__contains="B").update(set__text="Hello world")  # Update
    # todos = Todo.objects.all()
    return 'Hi'

