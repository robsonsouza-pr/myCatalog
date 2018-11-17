#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Categoria, Base, Item, Usuario

engine = create_engine('sqlite:///meucatalogo.db')
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

usuario = Usuario(nome="Admin",
                  email="admin@mycatalog.com",
                  imagem="")
session.add(usuario)
session.commit()

item = Item(nome="Resident Evil",
            descricao="Voce deve sobreviver a uma cidade cheia de  de zumbis",
            categoria_id=1,
            usuario_id=1
            )
session.add(item)
session.commit()

item2 = Item(nome="Dragon Ball",
             descricao="Goku e Bulma partem em busca das esferas do dragao",
             categoria_id=2,
             usuario_id=1
             )
session.add(item2)
session.commit()

item3 = Item(nome="One Punch Man",
             descricao="Siga o dram de Saitama, um heroi que vence seus " +
                       "oponentes com um so golpe",
             categoria_id=3,
             usuario_id=1
             )
session.add(item3)
session.commit()

item4 = Item(nome="Senhor dos aneis",
             descricao="Frodo deve ir a mordor destruir o Um anel",
             categoria_id=4,
             usuario_id=1
             )
session.add(item4)
session.commit()

item5 = Item(nome="Spider man",
             descricao="Pedro Prado foi mordido por uma aranha" +
                       " radioativa. E agora?",
             categoria_id=5,
             usuario_id=1
             )
session.add(item5)
session.commit()

print("Categorias criadas")
