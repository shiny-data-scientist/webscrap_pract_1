from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime
import pandas as pd
import re
import requests
import tabula

def webscraping():
    # Descargamos la página objetivo
    page = requests.get(
        'https://www.isciii.es/QueHacemos/Servicios/VigilanciaSaludPublicaRENAVE/'
        'EnfermedadesTransmisibles/Paginas/InformesCOVID-19.aspx'
    )
    if page.status_code == 200:
        print('Página descargada con éxito')
    else:
        print(f'Error al descargar la página status_code {page.status_code}')
        return None

    # creamos la sopa a traves de la página
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

    baselink = 'https://www.isciii.es'
    for pdf in pdfs:
        link = pdf['link']
        pdf.update({'link': baselink + link})
    datos_interes = []
    for pdf in pdfs:
        name = pdf['info']
        url = pdf['link']
        file = requests.get(url, allow_redirects=True)
        open('../data/' + name + '.pdf', 'wb').write(file.content)
        # extraemos el contenido del pdf
        contenido_pdf = tabula.read_pdf(
            '../data/' + name + '.pdf', pages='all', output_format='json'
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

        for top_level_element in contenido_pdf:
            for level_1_element in top_level_element['data']:
                comunidad = {}
                for i in range(0, len(level_1_element)):
                    if level_1_element[i]['text'] in comunidades:
                        comunidad['comunidad'] = level_1_element[i]['text']

                        # a veces tenemos los datos separados por espacios
                        # o en el siguiente diccionario, para extraerlos,
                        # generamos dos pattern para usar regular expression.
                        pattern_casos_separados = r'[0-9]+'
                        pattern_casos_juntos = r'[0-9]+\s[0-9]+'
                        if re.match(pattern_casos_separados,
                                    level_1_element[i + 1]['text']):
                            comunidad['casos'] = level_1_element[i + 1]['text']
                            try:
                                comunidad['casos_notificados'] = level_1_element[i + 2]['text']
                            except:
                                print(level_1_element)

                        elif re.match(pattern_casos_juntos,
                                      level_1_element[i + 1]['text']):
                            comunidad['casos'] = level_1_element[
                                i + 1]['text'].split(' ')[0]

                            comunidad['casos_notificados'] = level_1_element[
                                i + 1]['text'].split(' ')[1]

                        comunidad['datetime'] = timestamp
                        datos_interes.append(comunidad)

    datos_dataframe = pd.DataFrame(datos_interes)
    datos_dataframe.to_csv('../data/dataframe.csv')

if __name__ == '__main__':
    webscraping()