#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Categoria, Base, Item

engine = create_engine('sqlite:///myCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

categoria = Categoria(nome="Games")
session.add(categoria)
session.commit()

categoria2 = Categoria(nome="Animes")
session.add(categoria2)
session.commit()

categoria3 = Categoria(nome="Mangas")
session.add(categoria3)
session.commit()

categoria4 = Categoria(nome="Livros")
session.add(categoria4)
session.commit()

categoria5 = Categoria(nome="Hqs")
session.add(categoria5)
session.commit()

print("Categorias criadas")
