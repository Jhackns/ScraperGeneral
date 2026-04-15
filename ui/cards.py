import flet as ft

class CategoryCard(ft.Container):
    def __init__(self, title: str, icon: str, formats: str, on_change=None):
        super().__init__()
        self.title_text = title
        self.formats_text = formats
        self.on_change_callback = on_change
        self.visible = False # Oculto por defecto
        
        self.checkbox = ft.Checkbox(on_change=self._handle_change, fill_color=ft.Colors.CYAN_ACCENT)
        self.counter_text = ft.Text(self.formats_text, size=12, color=ft.Colors.GREY_500)
        self.progress_ring = ft.ProgressRing(width=12, height=12, stroke_width=2, visible=False, color=ft.Colors.CYAN_ACCENT)
        
        # UI Attributes 
        self.border_radius = 12
        self.padding = 15
        self.bgcolor = "#0D0D0D" # Deep Dark background
        self.border = ft.border.all(1, ft.Colors.CYAN_ACCENT)
        self.shadow = [
            ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.4, ft.Colors.CYAN_ACCENT),
                offset=ft.Offset(0, 0),
                blur_style=ft.ShadowBlurStyle.OUTER,
            )
        ]
        self.ink = True
        self.on_click = self._toggle_checkbox
        
        # Layout
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(name=icon, size=30, color=ft.Colors.CYAN_ACCENT),
                        self.checkbox
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Text(self.title_text, size=18, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        self.progress_ring,
                        self.counter_text
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=5
                )
            ]
        )

    @property
    def is_selected(self):
        return self.checkbox.value
        
    def _handle_change(self, e):
        if self.on_change_callback:
            self.on_change_callback()
            
    def _toggle_checkbox(self, e):
        self.checkbox.value = not self.checkbox.value
        self.checkbox.update()
        if self.on_change_callback:
            self.on_change_callback()

    def update_result(self, count: int):
        """Asigna visibilidad y actualiza el subtítulo con el conteo."""
        if count > 0:
            self.visible = True
            self.counter_text.value = f"{count} {self.title_text.lower()} detectadas"
            self.counter_text.color = ft.Colors.CYAN_ACCENT
        else:
            self.visible = False
        self.update()

