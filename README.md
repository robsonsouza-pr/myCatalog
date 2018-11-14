# Log Analytics
Projeto para cadastro de itens de catálogo.


# Dependências
1. Ter o VirtualBox instalado;
1. Ter o Vagrant instalado;
1. Ter o Git Bash instalado.

# Instruções
**Terminal**:
1. Baixe a configuração do projeto [aqui](https://d17h27t6h515a5.cloudfront.net/topher/2017/June/5948287e_fsnd-virtual-machine/fsnd-virtual-machine.zip) ou clone diretamente do github <https://github.com/udacity/fullstack-nanodegree-vm>
1. Com o Git Bash, navegue até a pasta em que descompactou a configuração do projeto e entre na pasta vagrant
1. Digite os comandos `vagrant up` (pode demorar um pouco) e depois `vagrant ssh`
1. Digite o comando `cd /vagrant` para entrar no diretório compartilhado do vagrant
1. Clone o projeto <https://github.com/robsonsouza-pr/myCatalog.git>
1. Navegue até o diretório mycatalog
1. Digite `python mycatalog.py`

**Populando o Banco de dados**
1. Esteja logado no vagrant
1.  Digite `python model.py`
1.  Digite `python populabanco.py`

