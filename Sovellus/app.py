from flask import Flask
from os import getenv
import os
from dotenv import  load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")#os.urandom(24)

import routes
