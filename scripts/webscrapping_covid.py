from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime
import pandas as pd
import re
import requests
import tabula
import tempfile
import os
import shutil

def webscraping(output_path_dataframe: str = None, output_path_pdfs: str = None):
    """
    Realiza web scraping en la página objetivo para descargar los pdfs,
    luego realiza pdf scrapping para extraer los datos deseados.
    :param output_path_dataframe: Path de salida del dataframe
    :param output_path_pdfs: Path para guardar los pdfs, si no,
    se eliminan después de extraer los datos.
    """
    # Descargamos la página objetivo

    using_tmp_dir = output_path_pdfs is None

    if output_path_pdfs is None:
        output_path_pdfs = tempfile.mkdtemp(dir='../data/')

    output_path_dataframe = output_path_dataframe or '../data/'

    page = requests.get(
        'https://www.isciii.es/QueHacemos/Servicios/VigilanciaSaludPublicaRENAVE/'
        'EnfermedadesTransmisibles/Paginas/InformesCOVID-19.aspx'
    )
    if page.status_code == 200:
        print('Página descargada con éxito')
    else:
        print(f'Error al descargar la página status_code {page.status_code}')
        return None

    # creamos la sopa html
    soup = BeautifulSoup(page.content, features="html.parser")

    # buscamos bajo el id donde están los links de interés
    id_links = soup.find(id='ctl00_PlaceHolderMain_ctl02__ControlWrapper_RichHtmlField')

    # para cada hijo buscamos a y guardamos su enlace
    pdfs = []
    for child in id_links.children:
        pdf = {}
        a_tag = child.find('a')
        if isinstance(a_tag, Tag):
            pdf['link'] = a_tag.get('href')
            pdf['info'] = a_tag.text
            pdfs.append(pdf)

    # completamos los enlaces añadiendo el baselink https://www.isciii.es
    baselink = 'https://www.isciii.es'
    for pdf in pdfs:
        link = pdf['link']
        pdf.update({'link': baselink + link})

    # realizamos el proceso de pdf scrapping para recolectar los datos objetivo
    datos_interes = []
    for pdf in pdfs:
        name = pdf['info']
        url = pdf['link']
        # descargamos el pdf
        file = requests.get(url, allow_redirects=True)
        open(output_path_pdfs + '/' + name + '.pdf', 'wb').write(file.content)
        # extraemos el contenido del pdf
        contenido_pdf = tabula.read_pdf(
            output_path_pdfs + '/' + name + '.pdf', pages='all', output_format='json', silent=True
        )

        comunidades = ['Andalucía', 'Aragón', 'Asturias', 'Baleares',
                       'Canarias', 'Cantabria', 'Castilla La Mancha',
                       'Castilla y León', 'Cataluña',
                       'Comunitat Valenciana', 'Extremadura',
                       'Galicia', 'Madrid', 'Murcia', 'Navarra',
                       'País Vasco', 'La Rioja', 'Ceuta', 'Melilla'
        ]

        # generamos el pattern para extraer la fecha con formato:
        # a 27 de marzo de 2020
        pattern_date = r'\s[a]\s([0-9]+)\s[a-z]+\s([a-z]+)\s[a-z]+\s([0-9]+)'
        time_text = name.split('España')[1]
        day, month, year = re.match(pattern_date, time_text).groups()

        months_mapping = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5,
            'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9,
            'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }

        timestamp = datetime.strptime(
            f'{day}-{str(months_mapping.get(month))}-{year}',
            '%d-%m-%Y'
        )

        # buscamos dentro del pdf los datos de interés
        for top_level_element in contenido_pdf:
            for level_1_element in top_level_element['data']:
                comunidad = {}
                for i in range(0, len(level_1_element)):
                    if level_1_element[i]['text'] in comunidades:
                        comunidad['comunidad'] = level_1_element[i]['text']

                        # a veces tenemos los datos separados por espacios
                        # o en el siguiente diccionario, para extraerlos,
                        # generamos un pattern para usar regular expression.
                        pattern_casos_juntos = r'[0-9]+\s[0-9]+'
                        if re.match(pattern_casos_juntos,
                                      level_1_element[i + 1]['text']):
                            comunidad['casos'] = level_1_element[
                                i + 1]['text'].split(' ')[0]

                            comunidad['casos_notificados'] = level_1_element[
                                i + 1]['text'].split(' ')[1]

                        else:
                            comunidad['casos'] = level_1_element[i + 1]['text']
                            comunidad['casos_notificados'] = level_1_element[i + 2]['text']

                        comunidad['datetime'] = timestamp
                        datos_interes.append(comunidad)

    datos_dataframe = pd.DataFrame(datos_interes)
    datos_dataframe.to_csv(
        output_path_dataframe + 'casos_covid19.csv',
        encoding='latin1',
        index=False
    )

    if using_tmp_dir and os.path.exists(output_path_pdfs):
        shutil.rmtree(output_path_pdfs)

if __name__ == '__main__':
    webscraping()
