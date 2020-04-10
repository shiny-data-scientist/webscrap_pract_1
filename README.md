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

Para ejecutar el script que recoge los datos de contaminación del arire es necesario tener descargado el chrome driver
ya que es la página objetivo solo muestras los datos históricos cuando se interactúa con ella. Por lo tanto, es 
necesario tenerlo descargado previamente. Por ahora es necesario tenerlo en el mismo directorio desde el cual se 
ejecute (ej. scripts/ para el caso indicado a continuación). 
Puedes descargarlo en el siguiente enlace:
    https://chromedriver.chromium.org/

Más adelante se añadirá como variable de entorno del sistema para facilitar su gestión.

Ahora puedes ejecutar jupyter en local o simplemente probar el script en la carpeta scrips con el comando:
````shell script
$ python scripts/webscrapping_covid.py
$ python scripts/webscrapping_aircontamination.py
````
