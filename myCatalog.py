#!/usr/bin/env python3

# imports
from flask import Flask, request, url_for, redirect, flash, jsonify, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, MenuItem, Base, User

# importacoes para oauth
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# carregando o arquivo com a chave secreta do oauth
"""CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']"""

# instanciando o flask
app = Flask(__name__)

# conexao com o banco de dados
engine = create_engine('sqlite:///restaurantmenuwithusers.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/categorias')
def categorias():
    return render_template('public-categorias.html')


# caso esteja executando via linha de comando, define ip e porta, alem de ligar o debug mode o secret
# key eh pra usar as mensagens do flash
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
