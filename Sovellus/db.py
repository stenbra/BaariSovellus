from flask_sqlalchemy import SQLAlchemy
from app import app
from os import getenv
from flask import redirect, render_template, request, session

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")#"postgresql:///stenbras"
db = SQLAlchemy(app)
