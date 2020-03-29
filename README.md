# README

Este repositorio contiene tres directiorios: 

 - data: Se encuentran los ficheros generados con los scripts.
 - scripts: Los scripts para extraer los dataframes.
 - notebooks: Notebooks donde se realiza un primer análisis de las páginas objetivo para extraer sus datos.
 
Para ejecutar los diferentes scripts o notebooks de este repositorio es necesario instalar las 
dependencias que se encuentran en el fichero requirements.txt. Para instalarlas, sigo los sigueintes pasos:

1. Crea una entorno virtual de python:
    ````shell script
        $ python3 -m venv venv
    ````
1. Activa el entorno de python.
    ````shell script
        # windows
        venv\Scripts\activate
        # ubuntu
        source venv/bin/activate
    ````
1. Instala las dependencias.
    ````shell script
     $ pip install -r requirements.txt
    ````
Ahora puedes ejecutar jupyter en local o simplemente probar el script en la carpeta scrips con el comando:
````shell script
$ python scripts/script_webscrapping.py
````