import os

from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
from datetime import datetime


def aqi_air_pollution_level(aqi_level: int):
    """"
    Returns the label that indicates the air pollution level.
    """
    if aqi_level < 51:
        return 'Good'
    elif aqi_level > 50 and aqi_level < 101:
        return 'Moderate'
    elif aqi_level > 100 and aqi_level < 151:
        return 'Unhealthy for Sensitive Groups'
    elif aqi_level > 150 and aqi_level < 201:
        return 'Unhealthy'
    elif aqi_level > 200 and aqi_level < 301:
        return 'Very Unhealthy'
    elif aqi_level > 301:
        return 'Hazardous'


def int_or_none(x: str):
    """
    Returns int or None from str.
    """
    try:
        return int(x)
    except:
        return None


def get_page_data_by_city(paths: dict):
    """
    Recoge los datos de la calidad del aire de la página
    https://aqicn.org/city/
    Utiliza selenium para interactuar con la página y que muestre los datos
    de interés.
    :param paths: dictionaries of paths to get the data
    :return: None
    """
    base_path = 'https://aqicn.org/city/'

    # Initialize the drive and hides it.
    driver = webdriver.Chrome()
    # executable_path: argumento para seleccionar el driver
    driver.set_window_position(-10000, 0)

    # Se añaden 3 índices de calidad del aire. PM10, O3 y NO2
    df = pd.DataFrame()
    for link, location in paths.items():
        current_path = base_path + link
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
        df_specific_city = pd.DataFrame()
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
                                        key: int_or_none(rect.text)
                                    })
                                    data.append(temp_data)

            # Gets the air pollution label
            df_temp = pd.DataFrame(data)
            new_label = key + '_level'
            df_temp[new_label] = df_temp[key].apply(
                aqi_air_pollution_level
            )
            if df_specific_city.empty:
                df_specific_city = df_temp
                # Añadimos ciudad y comunidad autónoma
                df_specific_city['ciudad'] = location['ciudad']
                df_specific_city['ca'] = location['ca']
            else:
                df_specific_city = df_specific_city.join(
                    df_temp.set_index('timestamp'), on='timestamp'
                )

        # joins the dataframe with all the particules:
        print(f'Extrayendo los datos de la ciudad {location}')
        if df.empty:
            df = df_specific_city
            del df_specific_city
        else:
            print(df_specific_city.head(2))
            print(df.head(2))
            df = df.append(df_specific_city, ignore_index=True)
            del df_specific_city

    driver.close()

    columns_order = [
        'timestamp', 'ca', 'ciudad',
        'pm10', 'pm10_level', 'o3',
        'o3_level', 'no2', 'no2_level'
    ]
    # crear dataframe y hacer un merge on timestamp and city
    df.to_csv(
        '../data/air_contamination.csv',
        index=False, columns=columns_order
    )


if __name__ == '__main__':
    # generamos un diccionario con los links a extraer y sus comunidades
    # autónomas y ciudades
    links_to_scrap = {
        'spain/andalucia/sevilla/santa-clara/': {
            'ca': 'Andalucia', 'ciudad': 'Sevilla'
        },
        'spain/catalunya/barcelona/': {
            'ca': 'Catalunya', 'ciudad': 'Barcelona'
        },
        'madrid/': {
            'ca': 'Madrid', 'ciudad': 'Madrid'
        },
        'spain/valencia/valencia/pista-de-silla/': {
            'ca': 'Valencia', 'ciudad': 'Valencia'},
        'spain/galicia/vigo/coia/': {
            'ca': 'Galicia', 'ciudad': 'Vigo'},
        'spain/castilla-y-leon/valladolid/vega-sicilia/': {
            'ca': 'Castilla y León',
            'ciudad': 'Valladolid'
        },
        'spain/pais-vasco/bilbao/mazarredo/': {
            'ca': 'Pais Vasco', 'ciudad': 'Bilbao'},
        'spain/canarias/san-nicolas/': {
            'ca': 'Canarias', 'ciudad': 'Las Palmas de Gran Canaria'},
        'spain/murcia/san-basilio-murcia-ciudad/': {
            'ca': 'Murcia', 'ciudad': 'Murcia'},
        'spain/zaragoza/el-picarral/': {
            'ca': 'Aragon', 'ciudad': 'Zaragoza'
        },
        'spain/baleares/foners/': {
            'ca': 'Islas Baleares', 'ciudad': 'Palma'
        },
        'spain/navarra/pamplona/rotxapea/': {
            'ca': 'Navarra', 'ciudad': 'Pamplona'
        },
        'spain/cantabria/santander-centro/': {
            'ca': 'Cantabria',
            'ciudad': 'Santander'
        }
    }

    get_page_data_by_city(links_to_scrap)
