import time
from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser
from typing import Dict, Any

class ScoutEngine:
    def __init__(self):
        """Inicializa el motor de descubrimiento, manteniendo el contexto apagado por defecto para ahorrar RAM hasta que se invoque."""
        self.playwright_context = None
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        
        # Almacenamiento per-sesión de recursos encontrados
        self.resources = {
            "Imágenes": set(),
            "Videos": set(),
            "Música": set(),
            "Documentos": set(),
            "Tablas": set(),
            "Artículos": set(),
            "Texto Plano": set()
        }

    def start_browser(self):
        """Abre Playwright en modo visible. Utiliza el canal Chrome local."""
        if self.playwright is None:
            self.playwright_context = sync_playwright()
            self.playwright = self.playwright_context.__enter__()
            
            # Modo Espejo (Stealth visual)
            self.browser = self.playwright.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            # Ocultamos el user agent automatizado 
            self.context = self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            )
            self.page = self.context.new_page()

    def _intercept_response(self, response):
        """
        Capa de Tráfico: Escucha todo lo que descarga el navegador mediante la tarjeta de red.
        Aplica validación cruzada: MIME Type + Extensión real
        """
        url = response.url.lower()
        if response.status >= 400: return # Filtra errores 404 o caídas
        
        content_type = response.headers.get('content-type', '').lower()
        clean_url = url.split('?')[0] # Elimina parametros extra de la ruta
        
        # --- Filtrado Doble Validación ---
        if 'image/' in content_type and not ('icon' in content_type or 'svg' in content_type):
            if any(clean_url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                self.resources["Imágenes"].add(response.url)
                
        elif 'video/' in content_type:
            if any(clean_url.endswith(ext) for ext in ['.mp4', '.webm', '.avi']):
                self.resources["Videos"].add(response.url)
                
        elif 'audio/' in content_type:
            if any(clean_url.endswith(ext) for ext in ['.mp3', '.wav', '.ogg']):
                self.resources["Música"].add(response.url)
                
        elif 'application/pdf' in content_type or 'wordprocessingml.document' in content_type or 'msword' in content_type:
            if any(clean_url.endswith(ext) for ext in ['.pdf', '.docx', '.doc']):
                self.resources["Documentos"].add(response.url)
                
        elif 'text/plain' in content_type or 'application/json' in content_type:
            if any(clean_url.endswith(ext) for ext in ['.txt', '.md', '.json', '.csv']):
                self.resources["Texto Plano"].add(response.url)

    def _parse_dom(self):
        """Capa HTML: Cuenta los elementos que componen la estructura interna."""
        try:
            # Detección de Tablas
            tables = self.page.locator('table').count()
            for i in range(tables):
                self.resources["Tablas"].add(f"tabla_html_{i}")
            
            # Detección de Artículos (Heurística: Meta títulos o H1 con texto extenso)
            has_h1 = self.page.locator('h1').count() > 0
            if has_h1:
                self.resources["Artículos"].add("articulo_estructurado_0")
                
        except Exception:
            pass

    def _auto_scroll(self):
        """Fuerza al navegador a bajar intermitentemente provocando la carga perezosa (Lazy Loading) del servidor web."""
        self.page.evaluate("""
            () => {
                return new Promise((resolve) => {
                    let totalHeight = 0;
                    let distance = 600;
                    let timer = setInterval(() => {
                        let scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;

                        if(totalHeight >= scrollHeight || totalHeight > 15000){
                            clearInterval(timer);
                            resolve();
                        }
                    }, 250); // Speed: Quarter second per jump
                });
            }
        """)

    def scan_url(self, url: str) -> Dict[str, int]:
        """
        Director Maestro de Fases:
        1. Levanta navegador.
        2. Escucha red.
        3. Realiza Scroll.
        4. Escucha elementos.
        Devuelve el total mapeado.
        """
        # 1. Asegurar navegador estático
        if not self.context:
            self.start_browser()
            
        # 2. Limpiar RAM del mapeo de un escaneo previo a otra URL
        for key in self.resources:
            self.resources[key].clear()
            
        # 3. Anclar Event Listener
        self.page.on("response", self._intercept_response)
        
        try:
            # wait_until = domcontentloaded acelera el proceso frente a networkidle
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(2) # Dar margen de procesamiento contra CloudFlare manual
            
            # 4. Solución al Lazy Loading
            self._auto_scroll()
            time.sleep(1) # Margin post-scroll settling
            
            # 5. Capa de DOM (Tablas, Iframes, etc.)
            self._parse_dom()
            
        except Exception as e:
            print(f"[Core] Error de navegación: {e}")
        finally:
            # Evitar fuga de memoria deteniendo la interceptacion
            try:
                self.page.remove_listener("response", self._intercept_response)
            except Exception:
                pass
            
        # Se genera el Diccionario de Resultados {"Categoria": 25}
        return {cat: len(items) for cat, items in self.resources.items() if len(items) >= 0}

# Instancia Persistente Singleton
scout = ScoutEngine()
