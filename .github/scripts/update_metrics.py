# scripts/update_metrics.py

import requests
from bs4 import BeautifulSoup
import os

def get_youtube_metrics(channel_url):
    # Realiza una solicitud a la página de Social Blade
    response = requests.get(channel_url)
    if response.status_code != 200:
        print(f"Error al acceder a {channel_url}")
        return None

    # Analiza el contenido HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extrae las métricas deseadas (ejemplo: suscriptores)
    try:
        subscribers = soup.find('span', class_='number').text.strip()
        return {
            'subscribers': subscribers,
            # Agrega más métricas según sea necesario
        }
    except AttributeError:
        print("No se pudieron encontrar las métricas.")
        return None

def update_metrics():
    # Lista de canales de YouTube a actualizar
    channels = {
        'Channel Name': 'https://socialblade.com/youtube/channel/CHANNEL_ID',
        # Agrega más canales según sea necesario
    }

    for name, url in channels.items():
        metrics = get_youtube_metrics(url)
        if metrics:
            print(f"{name}: {metrics['subscribers']} subscribers")
            # Aquí puedes agregar lógica para actualizar los archivos markdown correspondientes
            update_markdown_file(name, metrics)

def update_markdown_file(channel_name, metrics):
    # Ruta del archivo markdown correspondiente
    markdown_file_path = f"categories/{channel_name.replace(' ', '_').lower()}.md"
    
    # Verifica si el archivo existe
    if os.path.exists(markdown_file_path):
        with open(markdown_file_path, 'r') as file:
            content = file.readlines()

        # Actualiza la línea de suscriptores
        for i, line in enumerate(content):
            if 'Subscribers:' in line:
                content[i] = f"**Subscribers:** {metrics['subscribers']}\n"
                break

        # Escribe el contenido actualizado de nuevo en el archivo
        with open(markdown_file_path, 'w') as file:
            file.writelines(content)
    else:
        print(f"El archivo {markdown_file_path} no existe.")

if __name__ == "__main__":
    update_metrics()