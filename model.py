#!/usr/bin/env python3

# importacoes n
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# definicao da classe usuario
class Usuario(Base):

    __tablename__ = 'usuario'

    id = Column (Integer, primary_key=True)
    nome = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    imagem = Column(String(250), nullable=False)


class Categoria(Base):

    __tablename__ = 'categoria'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250), nullable=False)

    # retorna o objeto serializado no formato JSON
    @property
    def serialize(self):
        return{
            'id': self.id,
            'nome': self.nome
        }


class Item(Base):

    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    nome = Column(String(250), nullable=False)
    descricao = Column(String(250), nullable=False)
    categoria_id = Column(Integer, ForeignKey('categoria.id'))
    categoria = relationship(Categoria)

    @property
    def serialize(self):
        return{
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'categoria_id': self.categoria_id
        }


engine = create_engine('sqlite:///mycatalog.db')

Base.metadata.create_all(engine)
