import requests
import urllib3
from bs4 import BeautifulSoup
from urllib3 import HTTPSConnectionPool
from urllib3.exceptions import NewConnectionError


def get_expediente_page_content(usbid, password_cas):
    """
    Solo accede a la página expediente.dii.usb.com y regresa el contenido del expediente del usuario
    :param usbid:
    :param password_cas:
    :return:
    """

    if not password_cas or not usbid:
        return None

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    s = requests.Session()

    ## Accedemos a la página de expediente
    try:
        response = s.get("https://expediente.dii.usb.ve", verify=False)
    except NewConnectionError:
        return  None
    except requests.exceptions.Timeout:
        return None
    # Maybe set up for a retry, or continue in a retry loop
    except requests.exceptions.TooManyRedirects:
        return None
    # Tell the user their URL was bad and try a different one
    except requests.exceptions.RequestException as e:
        return  None

    ## Lee la página del CAS
    parsed_html = BeautifulSoup(response.content,"html.parser")

    # Get a secret code
    code_input_form = parsed_html.body.find(
        'input',
        attrs={
            'name': 'lt',
            'type': 'hidden',
        }
    ).get('value')

    url_cas = response.url
    #cookies = response.cookies

    log_in_data = {'username': usbid, 'password': password_cas, '_eventId': 'submit', 'lt': code_input_form}

    #Send the cas form filled
    response = s.post(url_cas, log_in_data, verify=False)

    if response.text.find('The credentials you provided cannot be determined to be authentic.') != -1:
        return  False
    # Se logea en expediente
    response = s.get('https://expediente.dii.usb.ve/login.do')

    # TODO: Parsear carrera de aquí
    #if not user.codigo_carrera:
        #response = s.get('http://expediente.dii.usb.ve/datosPersonales.do')
        #parsed_html = BeautifulSoup(response.content, "html.parser")
        # parsear_carrera()
    #    pass

    response = s.get('https://expediente.dii.usb.ve/informeAcademico.do')

    return response.text
