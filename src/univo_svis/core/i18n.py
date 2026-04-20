"""Internationalization service for UNIVO-SVIS."""

from __future__ import annotations

import logging
from enum import Enum

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages."""

    EN = "en"
    ES = "es"


class I18nService(QObject):
    """Lightweight translation service."""

    # Signal emitted when the language is changed
    language_changed = Signal(Language)

    _translations = {
        Language.EN: {
            "app_name": "UNIVO-SVIS",
            "app_subtitle": "Safety Vest Inspection Suite",
            "university": "University of Oviedo",
            "nav_home": "HOME",
            "nav_image_analysis": "IMAGE ANALYSIS",
            "nav_live_monitor": "LIVE MONITORING",
            "home_analyze_desc": "Analyze photos for safety vest compliance.",
            "home_monitor_desc": "Real-time video stream inspection.",
            "home_footer_config": "Active Configuration",
            "header_vest_mode": "Vest Mode",
            "header_ready": "Ready",
            "btn_open_image": "OPEN IMAGE",
            "btn_process": "PROCESS IMAGE",
            "btn_save": "SAVE RESULT",
            "btn_exit": "EXIT",
            "status_no_image": "No image loaded",
            "status_loading": "Loading model...",
            "panel_person": "Person Detection Only",
            "panel_compliance": "Vest Compliance Analysis",
            "panel_no_image": "No Image",
            "metric_total": "Total Detected Persons",
            "metric_with_vest": "Persons with Vest",
            "metric_without_vest": "Persons without Vest",
            "control_person_conf": "Person Confidence",
            "control_vest_conf": "Vest Confidence",
            "control_overlap": "Overlap (IOA_vest)",
            "save_dialog_title": "Save Result",
            "open_dialog_title": "Open Image",
            "live_status_fps": "FPS",
            "live_status_source": "Source",
            "live_status_state": "State",
            "live_status_vest": "Vest Model",
            "btn_open_video": "OPEN VIDEO",
            "btn_open_webcam": "OPEN WEBCAM",
            "btn_start": "START",
            "btn_pause": "PAUSE",
            "btn_resume": "RESUME",
            "btn_stop": "STOP",
        },
        Language.ES: {
            "app_name": "UNIVO-SVIS",
            "app_subtitle": "Suite de Inspección de Chalecos",
            "university": "Universidad de Oviedo",
            "nav_home": "INICIO",
            "nav_image_analysis": "ANÁLISIS DE IMAGEN",
            "nav_live_monitor": "MONITOREO EN VIVO",
            "home_analyze_desc": "Analizar fotos para cumplimiento de chalecos.",
            "home_monitor_desc": "Inspección de video en tiempo real.",
            "home_footer_config": "Configuración Activa",
            "header_vest_mode": "Modo Chaleco",
            "header_ready": "Listo",
            "btn_open_image": "ABRIR IMAGEN",
            "btn_process": "PROCESAR IMAGEN",
            "btn_save": "GUARDAR RESULTADO",
            "btn_exit": "SALIR",
            "status_no_image": "Sin imagen cargada",
            "status_loading": "Cargando modelo...",
            "panel_person": "Solo Detección de Personas",
            "panel_compliance": "Análisis de Cumplimiento",
            "panel_no_image": "Sin Imagen",
            "metric_total": "Total de Personas",
            "metric_with_vest": "Personas con Chaleco",
            "metric_without_vest": "Personas sin Chaleco",
            "control_person_conf": "Confianza Persona",
            "control_vest_conf": "Confianza Chaleco",
            "control_overlap": "Solapamiento (IOA_vest)",
            "save_dialog_title": "Guardar Resultado",
            "open_dialog_title": "Abrir Imagen",
            "live_status_fps": "FPS",
            "live_status_source": "Origen",
            "live_status_state": "Estado",
            "live_status_vest": "Modelo Chaleco",
            "btn_open_video": "ABRIR VIDEO",
            "btn_open_webcam": "ABRIR WEBCAM",
            "btn_start": "INICIAR",
            "btn_pause": "PAUSAR",
            "btn_resume": "REANUDAR",
            "btn_stop": "DETENER",
        },
    }

    def __init__(self) -> None:
        super().__init__()
        self._current_lang = Language.EN

    @property
    def current_language(self) -> Language:
        """Get the current active language."""
        return self._current_lang

    def set_language(self, lang: Language) -> None:
        """Update the active language and notify observers."""
        if lang != self._current_lang:
            self._current_lang = lang
            logger.info("Language changed to: %s", lang.name)
            self.language_changed.emit(lang)

    def get_text(self, key: str) -> str:
        """Get translated text for the given key."""
        return self._translations[self._current_lang].get(key, f"!!{key}!!")


# Singleton instance for easy access
I18N = I18nService()
