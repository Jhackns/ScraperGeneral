import flet as ft
from ui.cards import CategoryCard

class DiscoveryPanel(ft.Column):
    def __init__(self, on_selection_change=None):
        super().__init__()
        self.on_selection_change = on_selection_change
        self.visible = False # Panel enteramente oculto al inicio
        
        self.categories_map = {
            "Imágenes": {"icon": ft.Icons.IMAGE_ROUNDED, "formats": "jpg, png, webp, svg"},
            "Videos": {"icon": ft.Icons.ONDEMAND_VIDEO_ROUNDED, "formats": "mp4, webm, avi"},
            "Música": {"icon": ft.Icons.AUDIO_FILE_ROUNDED, "formats": "mp3, wav, ogg"},
            "Documentos": {"icon": ft.Icons.PICTURE_AS_PDF_ROUNDED, "formats": "pdf, docx, txt"},
            "Tablas": {"icon": ft.Icons.TABLE_CHART_ROUNDED, "formats": "csv, xlsx"},
            "Artículos": {"icon": ft.Icons.ARTICLE_ROUNDED, "formats": "Título, Contenido, Autor"},
            "Texto Plano": {"icon": ft.Icons.NOTES_ROUNDED, "formats": "txt, md, json"}
        }
        
        self.cards = {}
        grid_items = []
        for title, info in self.categories_map.items():
            card = CategoryCard(
                title=title, 
                icon=info["icon"], 
                formats=info["formats"],
                on_change=self.on_selection_change
            )
            self.cards[title] = card
            grid_items.append(card)
            
        self.grid = ft.ResponsiveRow(
            controls=[
                ft.Column(col={"sm": 12, "md": 6, "lg": 4}, controls=[item]) for item in grid_items
            ],
            spacing=15,
            run_spacing=15
        )
        
        self.content = self.grid
        self.controls = [self.content]

    def has_selection(self) -> bool:
        """Verifica si al menos una tarjeta visible está marcada."""
        return any(card.is_selected and card.visible for card in self.cards.values())

    def update_results(self, results: dict):
        """
        Recibe un diccionario con los conteos, ej: {"Imágenes": 14, "Videos": 0}.
        Revela las cards que superen el conteo, y muestra el panel.
        """
        has_items = False
        for category, count in results.items():
            if category in self.cards:
                self.cards[category].update_result(count)
                if count > 0:
                    has_items = True
        
        # Muestra el panel completo si al menos 1 categoría se detectó
        self.visible = has_items
        self.update()

    def set_loading_extraction(self, loading: bool):
        """Activa los ProgressRings sólo en tarjetas seleccionadas al extraer."""
        for card in self.cards.values():
            if card.is_selected and card.visible:
                card.progress_ring.visible = loading
                card.update()
