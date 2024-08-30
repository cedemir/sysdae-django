# knnproject
Sistema de gestão de comportamento de alunos

# 1. Baixe o repositório
   * git clone https://github.com/cedemir/sysdae-django.git

# 3. Crie o ambiente virtual
   * python3 -m venv venv
   * source venv/bin/activate

# 4. Instale as bibliotecas
   * pip install -r requirements.txt

# 5. Crie o banco de dados (SQLite3)
   * python3 ./manage.py makemigrations knnapp
   * python3 ./manage.py migrate

# 6. Crie um superusuário
   * python3 ./manage.py createsuperuser

# 7. Execute o serviço
   * python3 ./manage.py runserver
