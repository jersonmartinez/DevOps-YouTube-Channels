# scripts/update_metrics.py

import logging
import time
import random
import requests
from bs4 import BeautifulSoup
import os
import re

# Configurar el registro para depuración
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_youtube_metrics(channel_url):
    """Obtiene las métricas de un canal de YouTube desde Social Blade."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        logger.info(f"Accediendo a {channel_url}")
        response = requests.get(channel_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Error al acceder a {channel_url}: Código de estado {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Intentar encontrar el número de suscriptores con selectores más robustos
        sub_elements = soup.select('div[style*="font-weight: bold"]')
        for element in sub_elements:
            text = element.get_text(strip=True)
            if 'subscribers' in text.lower():
                logger.info(f"Métricas encontradas para {channel_url}: {text}")
                return {
                    'subscribers': text.split()[0],
                }

        logger.warning(f"No se encontraron métricas para {channel_url}.")
        return None

    except Exception as e:
        logger.error(f"Error al procesar {channel_url}: {e}")
        return None

    finally:
        time.sleep(random.uniform(2, 5))  # Retraso entre solicitudes para evitar bloqueos

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