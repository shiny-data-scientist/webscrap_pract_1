import os

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
from datetime import datetime


def get_page_data_by_city(paths: list):
    """
    Recoge los datos de la calidad del aire de la página
    https://aqicn.org/city/
    Utiliza selenium para interactuar con la página y que muestre los datos
    de interés.
    :param paths: list of paths to get the data
    :return: None
    """
    base_path = 'https://aqicn.org/city/'

    # Initialize the drive and hides it.
    driver = webdriver.Chrome()
    # executable_path: argumento para seleccionar el driver
    driver.set_window_position(-10000, 0)

    # Se añaden 3 índices de calidad del aire. PM10, O3 y NO2
    df = pd.DataFrame()
    for path in paths:
        current_path = base_path + path
        driver.get(current_path)
        # busca el historic data block y espera unos segundos para que se
        # muestren los datos objetivo.
        historic_data_block = driver.find_element_by_id(
            'historic-aqidata-block'
        )
        actions = ActionChains(driver)
        actions.move_to_element(historic_data_block)
        actions.perform()
        find = False
        while not find:
            time.sleep(10)
            try:
                driver.find_element_by_xpath(
                    '//*[@id="historic-aqidata-inner"]/div[2]/div[2]/center/ul/li[1]'
                )
                find = True
            except:
                time.sleep(10)

        # El siguiente mapping apunta a cada xpath de cada una de las
        # partículas
        mapping_particulas = {
            'pm10':
                '//*[@id="historic-aqidata-inner"]/div[2]/div[2]/center/ul/li[1]',
            'o3':
                '//*[@id="historic-aqidata-inner"]/div[2]/div[2]/center/ul/li[2]',
            'no2':
                '//*[@id="historic-aqidata-inner"]/div[2]/div[2]/center/ul/li[3]',
        }

        for key, value in mapping_particulas.items():
            data = [] # datos para cada partícula
            # buscamos partícula por el xpath
            particula = driver.find_element_by_xpath(
                value
            )
            particula.click()

            # Comprobamos si existe la página
            try:
                table = driver.find_element_by_class_name('squares')
            except:
                print(f'Ha habido un error para generar los datos en la página:'
                      f'path: {current_path}, partícula: indice')
                return

            # hacemos una sopa con el código fuente
            soup = BeautifulSoup(driver.page_source, features='html.parser')

            # Buscamos la tabla que contiene los datos en la sopa HTML
            table_data = soup.find(
                id='historic-aqidata-inner'
            ).find('table').find('tbody')
            for row in table_data.find_all('tr'):
                # cuando el dato está lleno tiene table-row
                # el year-divider es para el relleno de la tabla
                if row.get('class') == ['year-divider']:
                    year = row.text
                # Se obtienen solo datos de 2019 y 2020
                # revisar si entra en el siguiente:
                if (
                        (
                                row['style'] == 'display: table-row;'
                                and
                                row.get('class') != ['year-divider']
                        )
                        and
                        (
                         year == '2020' or year == '2019'
                        )
                ):
                    month = None
                    for td in row.find_all('td'):
                        if month is None:
                            month = row.td.text
                        if td.get('class') == ['squares']:
                            # comenzamos con el día 1 cada mes
                            day = 1
                            for svg in td.find_all('svg'):
                                for rect in svg.find_all('text'):
                                    temp_data = {}
                                    timestamp = datetime.strptime(
                                        f'{day}-{month}-{year}',
                                        '%d-%b-%Y'
                                    )
                                    day += 1
                                    temp_data.update({
                                        'timestamp': timestamp,
                                        key: rect.text
                                    })
                                    data.append(temp_data)
            df_temp = pd.DataFrame(data)
            if df.empty:
                df = df_temp
                # FIXME: tengo que gestionar bien la ciudad cuando haya más
                df['ciudad'] = path.split('/')[-2]
            else:
                df = df.join(df_temp.set_index('timestamp'), on='timestamp')
    # print(data)
    from pprint import pprint
    # pprint(data)
    driver.close()
    # df = pd.DataFrame(data, columns=['timestamp', 'ciudad', 'pm10', 'o3', 'no2'])
    # crear dataframe y hacer un merge on timestamp and city
    df.to_csv('../data/air_contamination.csv', index=False)

    # TODO:
    #  [ ] Añadir una opción para extraer los datos por fechas (las
    #  recibimos por parámetros)

if __name__ == '__main__':
    get_page_data_by_city(['spain/catalunya/barcelona/'])
