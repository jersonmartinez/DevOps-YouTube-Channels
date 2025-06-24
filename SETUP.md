# 🛠️ Configuración del Proyecto DevOps YouTube Channels

Este documento explica cómo configurar y mantener el proyecto DevOps YouTube Channels.

## 📋 Tabla de Contenidos

- [Requisitos](#requisitos)
- [Configuración Inicial](#configuración-inicial)
- [GitHub Actions](#github-actions)
- [Página Web](#página-web)
- [Scripts de Actualización](#scripts-de-actualización)
- [Contribuir](#contribuir)

## 📌 Requisitos

### Software Necesario
- Python 3.11 o superior
- Git
- Node.js (opcional, para desarrollo web)

### Dependencias Python
```bash
pip install -r requirements.txt
```

## 🚀 Configuración Inicial

### 1. Clonar el Repositorio
```bash
git clone https://github.com/jersonmartinez/DevOps-YouTube-Channels.git
cd DevOps-YouTube-Channels
```

### 2. Configurar el Entorno Virtual (Recomendado)
```bash
python -m venv venv
# En Windows
venv\Scripts\activate
# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

## 🔑 GitHub Actions

### Configuración

No se requieren secretos ni API keys. El sistema usa web scraping público.

### Workflows Disponibles

#### `update-metrics.yml`
- **Ejecución**: Semanal (domingos a medianoche UTC)
- **Trigger manual**: Sí
- **Función**: Actualiza métricas de suscriptores mediante web scraping y genera datos para la web
- **Sin requisitos**: No necesita API keys ni configuración adicional

## 🌐 Página Web

### Estructura
```
/
├── index.html          # Página principal
├── js/
│   ├── app.js         # Lógica de la aplicación
│   └── channels-data.js # Datos generados automáticamente
└── data/
    └── channels.json   # Backup de datos en JSON
```

### Características
- 🔍 Búsqueda en tiempo real
- 🏷️ Filtros por categoría, idioma y tecnología
- 📊 Estadísticas generales
- 📱 Diseño responsive
- ⚡ Carga rápida sin backend

### Despliegue con GitHub Pages
1. Ve a Settings → Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: / (root)
5. Guarda y espera el despliegue

## 🔧 Scripts de Actualización

### `generate_channels_data.py`
Genera los datos de canales para la web desde los archivos markdown.

```bash
python .github/scripts/generate_channels_data.py
```

**Salida**:
- `js/channels-data.js`: Datos en formato JavaScript
- `data/channels.json`: Backup en JSON

### `update_youtube_metrics.py`
Actualiza las métricas de suscriptores usando web scraping de múltiples fuentes.

```bash
python .github/scripts/update_youtube_metrics.py
```

**Características**:
- No requiere API keys ni configuración
- Scraping de múltiples fuentes (Social Blade, YouTube, VidIQ)
- Rotación automática de User-Agents
- Caché de resultados para optimizar el proceso
- Manejo inteligente de fallos con múltiples intentos

## 📝 Contribuir

### Añadir un Nuevo Canal

1. **Identifica la categoría correcta** en `categories/`
2. **Añade la información del canal** siguiendo este formato:

```markdown
### Nombre del Canal
[![@HandleDelCanal](https://img.shields.io/youtube/channel/subscribers/CHANNEL_ID?label=%40HandleDelCanal&style=social)](https://www.youtube.com/@HandleDelCanal?sub_confirmation=1)

**Canal**: https://www.youtube.com/@HandleDelCanal
**LinkedIn**: [Nombre del Autor](https://www.linkedin.com/in/perfil/)
**Rol**: Título Profesional
**Etiquetas**: `#tag1` `#tag2` `#tag3`

#### 🎯 Contenido Destacado
- Tema 1
- Tema 2
- Tema 3
```

### Proceso de PR
1. Fork el repositorio
2. Crea una rama: `git checkout -b add-channel-name`
3. Añade los cambios
4. Commit: `git commit -m 'Add channel: Channel Name'`
5. Push: `git push origin add-channel-name`
6. Crea un Pull Request

## 🐛 Solución de Problemas

### La página web no muestra canales
1. Verifica que `js/channels-data.js` existe
2. Ejecuta: `python .github/scripts/generate_channels_data.py`
3. Abre la consola del navegador para ver errores

### Las métricas no se actualizan
1. Verifica que el workflow esté habilitado
2. Revisa los logs del workflow en Actions
3. Verifica la conectividad a los sitios de scraping
4. Algunos canales pueden no tener datos disponibles públicamente

### Canales sin métricas
- Algunos canales ocultan su número de suscriptores
- Los sitios de scraping pueden no tener datos de canales nuevos
- El script intentará múltiples fuentes antes de marcar como fallido

## 📊 Límites y Consideraciones

### Web Scraping
- **Fuentes utilizadas**: Social Blade, YouTube directo, VidIQ
- **Rate limiting**: Delays automáticos entre 1-4 segundos
- **User-Agents**: Rotación automática para evitar bloqueos
- **Resiliencia**: Si una fuente falla, intenta con las siguientes
- **Caché**: Evita repetir scraping del mismo canal

### Mejores Prácticas
- Ejecutar el workflow máximo una vez al día
- Los domingos suelen tener menos tráfico
- El proceso completo toma ~15-30 minutos para 70+ canales

## 🔗 Enlaces Útiles

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.3/)

---

*Última actualización: Abril 2025* 