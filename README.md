# 🚀 DevOps YouTube Channels

Una colección curada de canales de YouTube enfocados en DevOps, Platform Engineering, Cloud Computing y tecnologías relacionadas. Este repositorio organiza los canales por categoría e idioma.

> 🌐 **[Ver la página web interactiva →](https://jersonmartinez.github.io/DevOps-YouTube-Channels/)**

## ✨ Características

- 📊 **Métricas actualizadas automáticamente** - Suscriptores actualizados semanalmente
- 🔍 **Búsqueda y filtros avanzados** - Encuentra canales por tecnología, idioma o categoría
- 🌐 **Interfaz web interactiva** - Navegación fácil sin necesidad de buscar en archivos
- 🏷️ **Organizado por categorías** - Platform Engineering, DevSecOps, Cloud, y más
- 🌎 **Multilenguaje** - Canales en español e inglés

## 📋 Categorías

- [🏗️ Platform Engineering](categories/platform-engineering.md)
- [🔒 DevSecOps & Security](categories/devsecops.md)
- [🐳 Containers & Orchestration](categories/containers.md)
- [☁️ Cloud Infrastructure](categories/cloud.md)
- [🏠 HomeLab & Self-Hosting](categories/homelab.md)
- [🤖 Automation & IaC](categories/automation.md)

## 🌐 Colecciones por Idioma

- [🇪🇸 Canales en Español](Spanish-Channels.md)
- [🇬🇧 English Channels](English-Channels.md)

## 📊 Sistema de Actualización Automática

Este repositorio incluye un sistema automatizado que actualiza las métricas de los canales de YouTube semanalmente sin necesidad de API keys.

### 🔧 Cómo Funciona

1. **Web Scraping Inteligente**: Obtiene métricas de múltiples fuentes públicas (Social Blade, YouTube, VidIQ)
2. **Sin Configuración**: No requiere API keys ni secretos - funciona out-of-the-box
3. **GitHub Actions**: Ejecuta automáticamente cada domingo y genera datos para la web
4. **Sistema Resiliente**: Si una fuente falla, automáticamente intenta con otras

### 🚀 Configuración Rápida

Consulta la [guía de configuración completa](SETUP.md) para instrucciones detalladas.

**Configuración básica:**
1. Fork o clona el repositorio
2. Activa GitHub Actions (se activan por defecto)
3. Activa GitHub Pages para la interfaz web
4. ¡Listo! No se requiere configuración adicional

### 📈 Métricas Disponibles
- Conteo de suscriptores actualizado
- Badges dinámicos en cada canal
- Estadísticas generales del repositorio
- Datos exportados para la web interactiva

## 🤝 Cómo Contribuir

¡Damos la bienvenida a las contribuciones! Aquí te explicamos cómo puedes ayudar:

### 📝 Añadir un Nuevo Canal

1. **Fork** el repositorio
2. **Crea una rama**: `git checkout -b add/nombre-del-canal`
3. **Encuentra la categoría apropiada** en `categories/`
4. **Añade el canal** siguiendo el formato establecido (ver [SETUP.md](SETUP.md))
5. **Commit**: `git commit -m 'Add channel: Nombre del Canal'`
6. **Push**: `git push origin add/nombre-del-canal`
7. **Abre un Pull Request**

### 🌟 Otras Formas de Contribuir

- 🐛 Reportar canales inactivos o enlaces rotos
- 💡 Sugerir nuevas categorías o mejoras
- 🌍 Traducir documentación
- ⭐ Dar una estrella al repositorio

## 🎯 Mejoras Implementadas y Futuras

### ✅ Implementado Recientemente
- [x] Página web interactiva con búsqueda y filtros
- [x] Actualización automática de métricas con API de YouTube
- [x] Sistema de caché y fallback para optimización
- [x] Badges dinámicos de suscriptores
- [x] Exportación de datos en múltiples formatos

### 🚀 Próximas Mejoras
- [ ] Añadir thumbnails de canales y videos destacados
- [ ] Sistema de recomendaciones basado en tags
- [ ] Integración con playlists educativas
- [ ] Soporte para más idiomas (portugués, francés)
- [ ] API pública para desarrolladores
- [ ] Sistema de votación/ranking comunitario
- [ ] Notificaciones de nuevos canales

## 🛠️ Tecnologías Utilizadas

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5
- **Backend**: Python 3.11, GitHub Actions
- **Web Scraping**: BeautifulSoup4, Requests, Fake-UserAgent
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions
- **Sin dependencias externas**: No requiere API keys ni servicios de terceros

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- A todos los creadores de contenido que comparten su conocimiento
- A la comunidad DevOps hispanohablante por su apoyo
- A los contribuidores que ayudan a mantener este proyecto actualizado

---

<div align="center">

*Este repositorio es mantenido con ❤️ por la comunidad DevOps*

**[⭐ Dale una estrella](https://github.com/tuusuario/DevOps-YouTube-Channels)** | **[🐛 Reportar un problema](https://github.com/tuusuario/DevOps-YouTube-Channels/issues)** | **[💡 Sugerir mejora](https://github.com/tuusuario/DevOps-YouTube-Channels/discussions)**

*Última actualización: Diciembre 2024*

</div>
