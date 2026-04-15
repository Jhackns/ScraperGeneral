import flet as ft
from ui.dashboard import Dashboard

def main(page: ft.Page):
    # Configuración de base de Flet Window
    page.title = "Scraper Universal Dinámico"
    page.theme_mode = ft.ThemeMode.DARK 
    page.padding = 0
    page.window.width = 1100
    page.window.height = 800
    page.bgcolor = "#050505"
    
    # Custom Theme Options - Aspecto premium Neon
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.CYAN,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    
    # Motores de Playwright y Almacenamiento Acoplados
    from core.scout import scout
    from core.extractor import extractor
    import asyncio
    
    # Fase 2: Ejecuta Scout (Levantamiento, Scroll y Escaneo)
    def call_scan_url(url: str):
        print(f"[Main] Invocando al motor Scout. Chrome en camino hacia: {url}")
        
        import threading
        
        def run_scout_thread():
            try:
                # El proceso síncrono del Scout bloquea este hilo esclavo sin congelar la UI de Flet.
                resultados = scout.scan_url(url)
                print(f"[Main] Resultados de Capa Red y DOM: {resultados}")
                # Reporta el json final directamente al dashboard
                page.pubsub.send_all({"type": "scan_complete", "data": resultados})
            except Exception as ex:
                print(f"[Main] WAF crasheó el hilo: {ex}")
            
        threading.Thread(target=run_scout_thread, daemon=True).start()

    # Fase 4: Extractor Masivo Real
    def call_extract(url: str, seleccionados: list):
        print(f"[Main] Descargando recursos en DatosExtraidos... Categorías: {seleccionados}")
        
        import threading
        def run_extractor_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(extractor.run_extraction(url, seleccionados))
                print("[Main] Extracción completada exitosamente.")
                page.pubsub.send_all({"type": "extraction_complete", "message": "¡Extracción finalizada! Revisa la carpeta DatosExtraidos."})
            except Exception as ex:
                print(f"[Main] Error en fase de guardado: {ex}")
            finally:
                loop.close()

        threading.Thread(target=run_extractor_thread, daemon=True).start()

    # Event Router
    def ui_event_router(msg):
        if msg.get("type") == "scan_complete":
            dashboard.display_scan_results(msg["data"])
        elif msg.get("type") == "extraction_complete":
            dashboard.finish_extraction(msg["message"])

    page.pubsub.subscribe(ui_event_router)

    # Inyección de dependencias reales
    dashboard = Dashboard(
        on_scan_url=call_scan_url,
        on_extract=call_extract
    )
    page.add(dashboard)

if __name__ == "__main__":
    ft.app(target=main)
