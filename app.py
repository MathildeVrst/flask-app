from flask import Flask, render_template, redirect, request
import json
import requests
import pypandoc
import os
import re
import links_from_header
import subprocess
import nbconvert
import nbformat
from nbconvert import HTMLExporter
from pybtex.database import BibliographyData, Entry
from pybtex.style.formatting.unsrt import Style
from pybtex.backends.html import Backend as HTMLBackend
from flask_frozen import Freezer

app = Flask(__name__, template_folder='./templates/') # lancement de l'application (qui va s'appeler app)

freezer = Freezer(app)

###############
### Accueil ### 
###############

@app.route('/') # turns a regular Python function into a Flask view function
def index():
    return render_template('index.html')

###########################
### Projet de recherche ###
###########################

# "def convert_markdown_to_html(markdown_file, html_file):" et "def render_markdown():" fonctionnent mais pas les images
def convert_markdown_to_html(markdown_file, html_file):
    # Convertir le fichier Markdown en HTML en utilisant Pandoc avec la bibliographie
    output = pypandoc.convert_file(markdown_file, 'html', extra_args=['--citeproc'])
    # Écrire le contenu HTML converti dans un fichier
    with open(html_file, 'w') as file:
        file.write(output)

@app.route({{ url_for('recherche')}})
def render_markdown():
    # Chemin d'accès au fichier Markdown
    markdown_file = 'static/md/recherche.md'
    # Chemin d'accès au fichier HTML de sortie
    html_file = 'static/md/recherche.html'
    # Convertir le fichier Markdown en HTML
    convert_markdown_to_html(markdown_file, html_file)
    # Lire le contenu HTML converti
    with open(html_file, 'r') as file:
        html_content = file.read()
    # Rendre le contenu HTML dans un template Flask
    return render_template('recherche.html', content=html_content)

#################
### Biblio DH ### 
#################

API_KEY = 'PC1qwUgWZ1E9d9scDZAUzVlx'
USER_ID = '8395018'
SUB_COLLECTION = 'RW3QWZDT' 
API_URL = 'https://api.zotero.org/users/'
bibstyle='chicago-fullnote-bibliography-fr'

def get_bibliographical_data():
    url = API_URL + USER_ID + '/collections/' + SUB_COLLECTION + '/items'
    params = {
        'key': API_KEY,
        'start': '0',
        'include':'citation,data',
        'style':bibstyle,
        'sort':'date'
    }
    pagination = True
    bibliographical_data = []  # Liste pour stocker les données bibliographiques
    start = 0  # Début de la pagination

    while True:
        params['start'] = str(start)  # Mettre à jour le paramètre 'start'
        data = requests.get(url, params)  # Effectuer une requête GET à l'API Zotero
        biblio_data = data.json()  # Convertir la réponse JSON en données exploitables

        if len(biblio_data) == 0:
            break  # Sortir de la boucle s'il n'y a plus d'éléments

        for bib_item in biblio_data:
            if bib_item['data']['itemType'] != 'attachment':
                bibliographical_data.append(bib_item)
                citation = bib_item['citation']
                print(citation)

        start += len(biblio_data)  # Mettre à jour le point de départ pour la prochaine itération
    return bibliographical_data
    
@app.route('/biblio')
def allitems():
    bibliographical_data = get_bibliographical_data()
    #save_to_json(bibliographical_data, 'biblio_data.json')
    return render_template('biblio.html', data=bibliographical_data)

#############
### Essai ### 
#############

@app.route('/essai')
def render_markdown_essai():
    # Chemin d'accès au fichier Markdown
    markdown_file = 'static/md/essai.md'
    # Chemin d'accès au fichier HTML de sortie
    html_file = 'static/md/essai.html'
    # Convertir le fichier Markdown en HTML
    convert_markdown_to_html(markdown_file, html_file)
    # Lire le contenu HTML converti
    with open(html_file, 'r') as file:
        html_content = file.read()
    # Rendre le contenu HTML dans un template Flask
    return render_template('essai.html', content=html_content)

########################
### Projet technique ###
########################

# Get toutes les données passages de l'API 

#def retrievedata():
#
#    data_from_API = []
#    pagination = True
#    c = 0 
#
#    while pagination == True: 
#        c = c+1
#        param = {'page': c,}
#        basic_url = 'https://anthologiagraeca.org/api/'
#        endpoint = "passages"
#        r = requests.get(basic_url + endpoint,param).json()
#        if r['next'] is None:
#            pagination = False
#        for item in r['results']:
#            data_from_API.append(item)
#    #return data_from_API
#    with open('data.json', 'w') as f:
#        json.dump(data_from_API, f)


# Path url 

@app.route('/technique')
def jupytertohtml():
    with open('static/ipynb/Panda.ipynb', 'r') as file:
        notebook_content = file.read()
        notebook = nbformat.reads(notebook_content, as_version=4)
        html_exporter = HTMLExporter()
        html_content, _ = html_exporter.from_notebook_node(notebook)
    return render_template('technique.html', data=html_content)

# What to do : Save the csv somewhere on the Web ; ask pandas to read the url ; write a git action to update it 
# ASYNC requests https://medium.com/@salimonov/asynchronous-background-tasks-in-flask-application-using-celery-1ba873d260d0



#@app.route('/technique')
#def jupytertohtml():
#    with open('static/ipynb/Panda.ipynb', 'r') as file:
#        monjupyter = file.read()
#        monhtml = pypandoc.convert_text(monjupyter, 'html', format='ipynb')
#    return render_template('technique.html', data=monhtml)

###########
### End ###
###########

if __name__ == '__main__':
  freezer.run(debug=True)
  #freezer.freeze()
  #app.run(debug=True)
