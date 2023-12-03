import os
import shutil
import http.cookiejar
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

banner = f"""
{Fore.GREEN}> Este codigo fue creado por t.me/indexdpp
> Fecha: 03/12/2023
> Este programa verifica la validez de las cookies de Netflix,\npor tal motivo puede quedar obsoleto mas adelante si Netflix hace modificaciones en su plataforma.
> Formato compatible Netscape 
"""
print(banner)
input("Recuerda colocar tus cookies en la carpeta cookies\nPresiona cualquier tecla para continuar...")
os.system('cls' if os.name == 'nt' else 'clear')

def parse_cookie_line(line):
    parts = line.strip().split('\t')
    return http.cookiejar.Cookie(
        version=0,
        name=parts[5],
        value=parts[6],
        port=None,
        port_specified=False,
        domain=parts[0],
        domain_specified=bool(parts[1]),
        domain_initial_dot=parts[0].startswith('.'),
        path=parts[2],
        path_specified=bool(parts[3]),
        secure=bool(parts[4]),
        expires=int(parts[4]) if parts[4].isdigit() else None,
        discard=False,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False,
    )

def verify_cookie(filename):
    cookie_jar = http.cookiejar.CookieJar()
    try:
        with open(f'cookies/{filename}', 'r') as f:
            for line in f:
                if not line.startswith('#'):
                    cookie = parse_cookie_line(line)
                    cookie_jar.set_cookie(cookie)
    except FileNotFoundError as e:
        print(f'Error al abrir el archivo: {e}')

    session = requests.Session()
    session.cookies = cookie_jar

    url = 'https://www.netflix.com/YourAccount'
    response = session.get(url)

    if response.url == url:
        soup = BeautifulSoup(response.text, 'html.parser')
        email = soup.find('div', {'data-uia': 'account-email'}).text
        account_type = soup.find('div', {'data-uia': 'plan-label'}).text
        new_filename = f'{account_type}_{email}_{filename}'
        shutil.move(f'cookies/{filename}', f'valid/{new_filename}')
        return f'{Fore.GREEN}[V] Las cookies en {filename} parecen ser válidas. Se han movido a valid/{new_filename}'
    elif 'for="id_password"' in response.text:
        new_filename = f'invalid_{filename}'
        shutil.move(f'cookies/{filename}', f'invalid/{new_filename}')
        return f'{Fore.RED}[X] Cookies en {filename} no parecen ser válidas. Se han movido a invalid/{new_filename}'
    else:
        return f'{Fore.YELLOW}[-] No se puede determinar la validez de las cookies en {filename}'

if not os.path.exists('valid'):
    os.makedirs('valid')
if not os.path.exists('invalid'):
    os.makedirs('invalid')

if not os.listdir('cookies'):
    print("No se han encontrado cookies en la carpeta 'cookies'.")
else:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        filenames = [filename for filename in os.listdir('cookies') if filename.endswith('.txt')]
        results = list(executor.map(verify_cookie, filenames))

    for result in results:
        print(result)
