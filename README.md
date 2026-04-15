# Scraper Universal Dinámico

Un potente motor de descubrimiento y extracción de recursos web desarrollado en **Python**, **Flet** y **Playwright**. Diseñado para sortear sistemas de carga perezosa (Lazy Loading) y protecciones WAF mediante un enfoque híbrido de intercepción de red y mapeo del DOM.

## App
![Screenshot Placeholder](/app.png)

---

## Requisitos e Instalación

Para que el motor funcione correctamente en tu sistema, sigue estos pasos en orden:

### 1. Clonar o descargar el proyecto
Asegúrate de estar dentro de la carpeta raíz `ScraperGeneral`.

### 2. Instalar dependencias de Python
Este proyecto requiere librerías modernas compatibles con Python 3.13+. Ejecuta el siguiente comando en tu terminal (PowerShell o CMD):

```bash
pip install -r requirements.txt
```

### 3. Instalar binarios de Playwright
Playwright necesita descargar su propio motor de Chromium (Chrome) para el modo de navegación visible. Ejecuta este comando:

```bash
python -m playwright install chromium
```

---

## Cómo ejecutar la aplicación

Una vez instaladas las dependencias, simplemente lanza el punto de entrada principal:

```bash
python main.py
```

---

## Manual de Uso Correcto

El Scraper está diseñado bajo un flujo de **Descubrimiento Dinámico** en cuatro fases:

1.  **Ingreso de URL**: Pega el enlace de la página que deseas analizar (actualmente optimizado para **portales de noticias**). Debe comenzar con `https://`.
2.  **Escaneo Activo**: Haz clic en el botón `Escanear URL`. Se abrirá una ventana de Chrome **visible**. 
    *   *Nota*: Si aparece un Captcha o bloqueo de Cloudflare, resuélvelo manualmente en la ventana de Chrome y el bot continuará automáticamente después.
    *   El bot realizará un **Scroll Automático** para forzar la carga de todas las imágenes y recursos ocultos.
3.  **Selección de Recursos**: Una vez finalizado el escaneo, aparecerán en la interfaz tarjetas Neón con los recursos detectados (Imágenes, Videos, Tablas, Artículos, etc.). Selecciona las categorías que te interesen mediante los checkboxes.
4.  **Extracción Masiva**: Haz clic en `Confirmar y Extraer`. El sistema descargará todo de forma paralela y organizada.

---

## 📁 Organización de los Datos

Toda la información minada se guarda automáticamente en la raíz del proyecto dentro de la carpeta:

`📂 DatosExtraidos/`
  `└── 📂 nombre_del_dominio/`
    `├── 📂 Imágenes/` (Fotos reales capturadas)
    `├── 📂 Tablas/` (Archivos .csv listos para Excel)
    `├── 📂 Artículos/` (Contenido textual estructurado en .json con identación)
    `└── 📂 Texto Plano/` (JSONs y APIs detectadas en red)

---

## Características Principales

*   **Diseño Cyberpunk**: Interfaz Neon moderna con Dark Mode integrado.
*   **Doble Validación**: El motor verifica el Tipo MIME y la extensión real para evitar archivos basura.
*   **Extracción de Tablas a CSV**: Convierte tablas visuales de la web en datos estructurados.
*   **Estructura Legible**: Todos los archivos JSON se guardan con sangría (indent=4) para una lectura humana sencilla.
*   **Gestión de Concurrencia**: Descargas controladas mediante semáforos (Semaforo x5) para evitar bloqueos por parte de los servidores.

---

> [!TIP]
> **Optimización**: Actualmente el motor brilla en sitios de noticias (RPP, La República, Diario Correo, etc.), logrando extraer el cuerpo del texto y metadatos del autor de forma automática.
