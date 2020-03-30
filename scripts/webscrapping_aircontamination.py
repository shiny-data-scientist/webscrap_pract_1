from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

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
        time.sleep(5)

        # TODO: Se tienen que añadir las demás partículas:
        #  o3 y no3, por ahora solo está el pm10
        #  también se tiene que añadir la etiqueta de la calidad del aire.
        # buscamos partícula pm10 por el xpath
        pm10 = driver.find_element_by_xpath(
            '//*[@id="historic-aqidata-inner"]/div[2]/div[2]/center/ul/li[1]'
        )
        pm10.click()

        # Comprobamos si existe la página
        try:
            table = driver.find_element_by_class_name('squares')
        except:
            print(f'Ha habido un error para generar los datos en la página:'
                  f'path: {current_path}, partícula: pm10')
            return

        # hacemos una sopa con el código fuente
        soup = BeautifulSoup(driver.page_source)

        # Buscamos la tabla que contiene los datos en la sopa HTML
        table_data = soup.find(
            id='historic-aqidata-inner'
        ).find('table').find('tbody')
        print(table_data)

        # TODO: [ ] Código para extraer los datos.
        #  [ ] Añadir una opción para extraer los datos por fechas (las
        #  recibimos por parámetros)

    driver.close()


if __name__ == '__main__':
    get_page_data_by_city(['spain/catalunya/barcelona/'])