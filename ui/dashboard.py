import flet as ft
from ui.discovery_panel import DiscoveryPanel
from utils.validators import is_valid_url

class Dashboard(ft.Container):
    def __init__(self, on_scan_url=None, on_extract=None):
        super().__init__()
        self.expand = True
        self.on_scan_url = on_scan_url
        self.on_extract = on_extract
        self.padding = 30
        
        # Estado Interno
        self.current_url = ""
        
        # Componentes de entrada
        self.url_input = ft.TextField(
            label="URL de Destino",
            hint_text="https://ejemplo.com",
            prefix_icon=ft.Icons.LINK_ROUNDED,
            border_radius=8,
            border_color=ft.Colors.CYAN_800,
            focused_border_color=ft.Colors.CYAN_ACCENT,
            label_style=ft.TextStyle(color=ft.Colors.CYAN_ACCENT),
            expand=True,
            on_change=self._validate_input
        )
        
        # Botón Fase 1: Escanear
        self.scan_button = ft.ElevatedButton(
            text="Escanear URL",
            icon=ft.Icons.RADAR_ROUNDED,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=20),
            disabled=True,
            on_click=self._handle_scan
        )
        
        # El Panel de Descubrimiento Dinámico
        self.discovery_panel = DiscoveryPanel(on_selection_change=self._update_extract_button_state)
        
        # Botón Fase 4: Confirmar y Extraer (Oculto al inicio)
        self.extract_button = ft.ElevatedButton(
            text="Confirmar y Extraer",
            icon=ft.Icons.DOWNLOAD_ROUNDED,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.CYAN_ACCENT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=20,
                shadow_color=ft.Colors.CYAN_ACCENT,
                elevation=20,
            ),
            visible=False,
            disabled=True,
            on_click=self._handle_extract
        )
        
        # Componente de carga general
        self.scanning_indicator = ft.Row(
            controls=[
                ft.ProgressRing(width=20, height=20, color=ft.Colors.CYAN_ACCENT),
                ft.Text("Navegando y escaneando la estructura...", color=ft.Colors.CYAN_ACCENT)
            ],
            visible=False,
            alignment=ft.MainAxisAlignment.CENTER
        )
        
        # Textos informativos dinámicos
        self.instruction_text = ft.Text(
            "Ingresa una ruta validada para desplegar a Playwright e identificar recursos.",
            size=12, color=ft.Colors.GREY_500
        )
        
        # Layout Principal Organizado Verticalmente
        self.content = ft.Column(
            controls=[
                ft.Text("Scraper Universal Dinámico", size=32, weight=ft.FontWeight.W_900, color=ft.Colors.CYAN_ACCENT),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                
                # Barra de Búsqueda
                ft.Row(
                    controls=[self.url_input, self.scan_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                
                ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                self.scanning_indicator,
                self.instruction_text,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                self.discovery_panel,
                
                # Botón de cierre
                ft.Row([self.extract_button], alignment=ft.MainAxisAlignment.END)
            ],
            scroll=ft.ScrollMode.AUTO
        )

    def _validate_input(self, e):
        """Evalúa si la URL es válida para habilitar el Escaneo."""
        url = self.url_input.value.strip()
        if not is_valid_url(url) and len(url) > 0:
            self.url_input.error_text = "Debe iniciar con https://"
            self.url_input.border_color = ft.Colors.RED_400
        else:
            self.url_input.error_text = None
            self.url_input.border_color = None
        self.url_input.update()
        
        # Activar el Scan button
        self.scan_button.disabled = not is_valid_url(url)
        self.scan_button.update()
        
        # Al modificar la URL, se reinicia la UI descartando resultados anteriores
        self.current_url = url
        self.discovery_panel.visible = False
        self.extract_button.visible = False
        self.instruction_text.value = "Ingresa una ruta validada para desplegar a Playwright e identificar recursos."
        self.update()

    def _update_extract_button_state(self):
        """Regla F4: Habilitar extracción solo con escaneo completo y casillas marcadas."""
        has_sel = self.discovery_panel.has_selection()
        self.extract_button.disabled = not has_sel
        self.extract_button.update()

    def _handle_scan(self, e):
        self.url_input.disabled = True
        self.scan_button.disabled = True
        self.scanning_indicator.visible = True
        self.instruction_text.value = "Atención al Chrome. Intervén manualmente si aparece un Captcha."
        self.update()
        
        if self.on_scan_url:
            self.on_scan_url(self.current_url)
            
    def _handle_extract(self, e):
        self.extract_button.disabled = True
        self.discovery_panel.set_loading_extraction(True)
        self.instruction_text.value = "Descargando recursos... Por favor, no cierres el navegador Chrome."
        self.instruction_text.color = ft.Colors.ORANGE_300
        self.update()
        
        if self.on_extract:
            selected_cats = [k for k, v in self.discovery_panel.cards.items() if v.is_selected and v.visible]
            self.on_extract(self.current_url, selected_cats)

    def finish_extraction(self, message: str):
        """Llamado cuando el extractor termina su tarea."""
        self.discovery_panel.set_loading_extraction(False)
        self.extract_button.disabled = False
        self.instruction_text.value = message
        self.instruction_text.color = ft.Colors.GREEN_ACCENT
        self.update()

    def display_scan_results(self, results: dict):
        """CallBack que se dispara cuando Playwright acaba."""
        self.scanning_indicator.visible = False
        self.url_input.disabled = False
        self.scan_button.disabled = False
        
        self.discovery_panel.update_results(results)
        
        if self.discovery_panel.visible:
            self.instruction_text.value = "Mapeo completo. Selecciona qué deseas descargar."
            self.extract_button.visible = True
        else:
            self.instruction_text.value = "El explorador no identificó ningún recurso válido en toda la página."
            self.extract_button.visible = False
            
        self.update()
        self._update_extract_button_state()
