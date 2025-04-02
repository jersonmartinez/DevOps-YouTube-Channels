# scripts/update_metrics.py

import requests
from bs4 import BeautifulSoup
import os
import re

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
        print(f"Retrieved {subscribers} for {channel_url}")  # Salida de depuración
        return {
            'subscribers': subscribers,
        }
    except AttributeError:
        print(f"No se pudieron encontrar las métricas para {channel_url}.")
        return None

def extract_channels_from_md(file_path):
    channels = {}
    with open(file_path, 'r') as file:
        content = file.readlines()
    
    for line in content:
        # Busca líneas que contengan el nombre y la URL del canal
        if '**Canal**:' in line or '**Channel**:' in line:
            # Extraer el nombre del canal
            name_match = re.search(r'\*\*(.*?)\*\*', line)
            if name_match:
                name = name_match.group(1).strip()
            else:
                continue
            
            # Extraer la URL del canal
            url_match = re.search(r'\((.*?)\)', line)
            if url_match:
                url = url_match.group(1).strip()
                channels[name] = url
    return channels

def update_metrics():
    # Lista de archivos de categorías
    category_files = [
        'categories/devsecops.md',
        'categories/homelab.md',
        'categories/platform-engineering.md',
        'categories/cloud.md',
        'categories/automation.md',
        'categories/containers.md'
    ]

    all_channels = {}
    for category_file in category_files:
        all_channels.update(extract_channels_from_md(category_file))

    for name, url in all_channels.items():
        metrics = get_youtube_metrics(url)
        if metrics:
            print(f"{name}: {metrics['subscribers']} subscribers")
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