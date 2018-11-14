#!/usr/bin/env python3

# imports
from flask import Flask, request, url_for, redirect,\
    flash, jsonify, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Categoria, Item, Base, Usuario

# importacoes para oauth
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# carregando o arquivo com a chave secreta do oauth
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']

# instanciando o flask
app = Flask(__name__)

# conexao com o banco de dados
engine = create_engine('sqlite:///mycatalog.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# secao do login
@app.route('/login')
def login():
    # gera uma combinacao de 32  misturando
    # letras maiusculas e numeros
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits
    ) for x in xrange(32))
    # guarda na sessao de login com nome de state/estado
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    print("chamei o gnconect")
    # Valida o token gerado no login
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # pega o codigo de autorizacao
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps(
                'Failed to upgrade the authorization code.'
            ), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
            'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
            % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps(
                "Token's user ID doesn't match given user ID."
            ), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps(
                "Token's client ID does not match app's."
            ), 401
        )
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        print("Ja esta logado essa porra")
        login_session['user_id'] = get_user_id(login_session['email'])
        response = make_response(
            json.dumps(
                'Current user is already connected.'
            ), 200
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = get_user_id(login_session['email'])
    print("loguei e o user_id eh %s") % user_id
    if user_id is not None:
        login_session['user_id'] = user_id
    else:
        id = create_user(login_session)
        login_session['user_id'] = id
    flash("you are now logged in as %s" % login_session['username'])
    print("logou")
    response = make_response(
        json.dumps(
            'Current user is already connected.'
        ), 200
    )
    response.headers['Content-Type'] = 'application/json'
    return response


# login facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("access token received %s " % access_token)

    app_id = json.loads(
        open(
            'fb_client_secrets.json', 'r'
        ).read()
    )['web']['app_id']

    app_secret = json.loads(
        open(
            'fb_client_secrets.json', 'r'
        ).read()
    )['web']['app_secret']

    url = "https://graph.facebook.com/oauth/access_token?" \
          "grant_type=fb_exchange_token&client_id=%s&client_secret=%s" \
          "&fb_exchange_token=%s" % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"

    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?' \
          'access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?' \
          'access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    flash("Now logged in as %s" % login_session['username'])
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


def create_user(login_session):
    new_user = Usuario(nome=login_session['username'], email=login_session[
        'email'], imagem=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(Usuario).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    user = session.query(Usuario).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(Usuario).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/logout')
def logout():
    access_token = login_session.get('access_token')
    # se o codigo de acesso for nulo, o usuario
    # ja esta desconectado, retorna erro 401
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps(
                'Current user not connected.'
            ), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    if login_session['provider'] == 'facebook'in login_session:
        facebook_id = login_session['facebook_id']
        # The access token must me included to successfully logout
        access_token = login_session['access_token']
        url = 'https://graph.facebook.com/%s/permissions?access_token=%s'\
              % (facebook_id, access_token)
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    clean_login_session(login_session)
    return redirect('/categorias')


# deslogar
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    # se o codigo de acesso for nulo, o usuario
    # ja esta desconectado, retorna erro 401
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps(
                'Current user not connected.'
            ), 401
        )
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    clean_login_session(login_session)
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s'\
          % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


def clean_login_session(login_session):
    if login_session['provider'] == 'google':
        del login_session['gplus_id']
    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    del login_session['picture']


# metodos da navegacao
@app.route('/')
@app.route('/categorias')
def categorias():
    categorias = session.query(Categoria).order_by(Categoria.nome).all()
    return render_template('public-categorias.html', categorias=categorias)


@app.route('/categoria/<int:categoria_id>')
def detalhar_categoria(categoria_id):
    categoria = session.query(Categoria).filter_by(
        id=categoria_id
    ).one()
    items = session.query(Item).filter_by(
        categoria_id=categoria.id
    ).order_by(Item.nome).all()
    if 'username' in login_session:
        return render_template(
            'detalhar-categoria.html', categoria=categoria, items=items
        )
    else:
        return render_template(
            'public-detalhar-categoria.html', categoria=categoria, items=items
        )


@app.route('/categoria/<int:categoria_id>/item/criar',
           methods=['GET', 'POST'])
def criar_item(categoria_id):
    if 'username' not in login_session:
        return redirect('/login')

    categoria = session.query(Categoria).filter_by(id=categoria_id).one()
    if request.method == 'POST':
        item = Item(
            nome=request.form["nome"],
            descricao=request.form["descricao"],
            categoria_id=categoria.id
        )
        session.add(item)
        session.commit()
        flash("Item criado com sucesso!")
        return redirect(
            url_for(
                'detalhar_categoria', categoria_id=categoria.id
            )
        )
    else:
        print("entrei no get")
        return render_template(
            'criar-item.html', categoria_id=categoria.id
        )


@app.route('/categoria/<int:categoria_id>/item/<int:item_id>/editar',
           methods=['GET', 'POST'])
def editar_item(categoria_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form["nome"]:
            item.nome = request.form["nome"]
        if request.form["descricao"]:
            item.descricao = request.form["descricao"]
        session.add(item)
        session.commit()
        flash("Item alterado com sucesso!")
        return redirect(
            url_for(
                'detalhar_categoria', categoria_id=categoria_id
            )
        )
    else:
        return render_template(
            'editar-item.html', categoria_id=categoria_id, item=item
        )


@app.route('/categoria/<int:categoria_id>/item/<int:item_id>/deletar',
           methods=['GET', 'POST'])
def deletar_item(categoria_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item excluido com sucesso!")
        return redirect(
            url_for(
                'detalhar_categoria', categoria_id=categoria_id
            )
        )
    else:
        return render_template(
            'deletar-item.html', categoria_id=categoria_id, item=item
        )


# endpoint json
@app.route('/categorias/JSON')
def categorias_json():
    categorias = session.query(Categoria).all()
    return jsonify(Categoria=[c.serialize for c in categorias])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
