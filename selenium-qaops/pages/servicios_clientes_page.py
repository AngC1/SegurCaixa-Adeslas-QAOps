"""
Page Object Model (POM) con Motor de Auto-Curación (Self-Healing Locators)
para el portal SegurCaixa Adeslas (/servicios-para-clientes) — Ayesa Digital QAOps.
"""

from __future__ import annotations

from typing import List, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class ServiciosClientesPage:
    """Page Object del portal /servicios-para-clientes con soporte Self-Healing."""

    def __init__(self, driver: WebDriver, base_url: str = "http://127.0.0.1:8080") -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, 10)
        self.healing_events: List[str] = []

    def find_healed(self, candidates: List[Tuple[str, str]]) -> WebElement:
        """
        Intenta localizar un elemento probando selectores en orden de prioridad.
        Si el selector primario falla y funciona un fallback, registra un evento Self-Healing.
        """
        last_exc = None
        for idx, (by, value) in enumerate(candidates):
            try:
                el = self.wait.until(EC.presence_of_element_located((by, value)))
                if idx > 0:
                    self.healing_events.append(
                        f"Self-Healed locator: primary {candidates[0]} -> fallback {(by, value)}"
                    )
                return el
            except Exception as exc:
                last_exc = exc
        raise RuntimeError(f"No se pudo localizar el elemento con candidatos: {candidates}") from last_exc

    def open(self) -> "ServiciosClientesPage":
        self.driver.get(f"{self.base_url}/servicios-para-clientes")
        self.find_healed(
            [
                (By.ID, "hero-title"),
                (By.CSS_SELECTOR, "[data-testid='hero-title']"),
                (By.TAG_NAME, "h1"),
            ]
        )
        return self

    def get_hero_title(self) -> str:
        return self.find_healed([(By.ID, "hero-title"), (By.CSS_SELECTOR, "[data-testid='hero-title']")]).text

    def get_service_cards_count(self) -> int:
        cards = self.driver.find_elements(By.CSS_SELECTOR, "#catalogo-servicios-grid .service-card")
        return len(cards)

    def switch_tab(self, tab_btn_id: str) -> None:
        btn = self.find_healed(
            [
                (By.ID, tab_btn_id),
                (By.CSS_SELECTOR, f"[data-testid='{tab_btn_id}']"),
            ]
        )
        btn.click()

    # --- 1. Flujo Cuadro Médico ---
    def buscar_cuadro_medico(
        self,
        provincia: str = "Todas",
        especialidad: str = "Todas",
        poliza: str = "Todas",
        texto: str = "",
    ) -> int:
        self.switch_tab("btn-tab-cuadro")
        Select(self.find_healed([(By.ID, "cm-provincia")])).select_by_visible_text(
            "Todas las provincias" if provincia == "Todas" else provincia
        )
        Select(self.find_healed([(By.ID, "cm-especialidad")])).select_by_visible_text(
            "Todas las especialidades" if especialidad == "Todas" else especialidad
        )
        Select(self.find_healed([(By.ID, "cm-poliza")])).select_by_visible_text(
            "Todas las modalidades" if poliza == "Todas" else poliza
        )
        q_input = self.find_healed([(By.ID, "cm-query")])
        q_input.clear()
        if texto:
            q_input.send_keys(texto)

        self.find_healed([(By.ID, "btn-buscar-cuadro")]).click()
        self.wait.until(lambda d: "Mostrando" in d.find_element(By.ID, "cm-contador").text)
        cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='center-card-item']")
        return len(cards)

    # --- 2. Flujo Autorizaciones Médicas ---
    def solicitar_autorizacion(
        self,
        num_tarjeta: str,
        tipo_acto_visible: str,
        prescripcion: str,
        centro: str,
    ) -> str:
        self.switch_tab("btn-tab-autorizaciones")
        tarjeta_el = self.find_healed([(By.ID, "aut-tarjeta")])
        tarjeta_el.clear()
        tarjeta_el.send_keys(num_tarjeta)

        Select(self.find_healed([(By.ID, "aut-tipo-acto")])).select_by_visible_text(tipo_acto_visible)

        pres_el = self.find_healed([(By.ID, "aut-prescripcion")])
        pres_el.clear()
        pres_el.send_keys(prescripcion)

        centro_el = self.find_healed([(By.ID, "aut-centro")])
        centro_el.clear()
        centro_el.send_keys(centro)

        self.find_healed([(By.ID, "btn-solicitar-autorizacion")]).click()
        alert = self.wait.until(
            lambda d: d.find_element(By.ID, "aut-resultado-alert")
            if "show" in d.find_element(By.ID, "aut-resultado-alert").get_attribute("class")
            else False
        )
        return alert.text

    # --- 3. Flujo Reembolsos ---
    def solicitar_reembolso(
        self,
        nif: str,
        modalidad_visible: str,
        importe: str,
        iban: str,
    ) -> str:
        self.switch_tab("btn-tab-reembolsos")
        nif_el = self.find_healed([(By.ID, "rmb-nif")])
        nif_el.clear()
        nif_el.send_keys(nif)

        Select(self.find_healed([(By.ID, "rmb-modalidad")])).select_by_visible_text(modalidad_visible)

        imp_el = self.find_healed([(By.ID, "rmb-importe")])
        imp_el.clear()
        imp_el.send_keys(importe)

        iban_el = self.find_healed([(By.ID, "rmb-iban")])
        iban_el.clear()
        iban_el.send_keys(iban)

        self.find_healed([(By.ID, "btn-enviar-reembolso")]).click()
        alert = self.wait.until(
            lambda d: d.find_element(By.ID, "rmb-resultado-alert")
            if "show" in d.find_element(By.ID, "rmb-resultado-alert").get_attribute("class")
            else False
        )
        return alert.text

    # --- 4. Flujo Área Cliente ---
    def login_area_cliente(self, nif: str, password: str) -> str:
        self.switch_tab("btn-tab-area-cliente")
        nif_el = self.find_healed([(By.ID, "login-nif")])
        nif_el.clear()
        nif_el.send_keys(nif)

        pwd_el = self.find_healed([(By.ID, "login-password")])
        pwd_el.clear()
        pwd_el.send_keys(password)

        self.find_healed([(By.ID, "btn-login-cliente")]).click()
        alert = self.wait.until(
            lambda d: d.find_element(By.ID, "login-resultado-alert")
            if "show" in d.find_element(By.ID, "login-resultado-alert").get_attribute("class")
            else False
        )
        return alert.text

    # --- 5. Flujo Videoconsulta ---
    def reservar_videoconsulta(self, especialidad_visible: str, motivo: str) -> str:
        self.switch_tab("btn-tab-videoconsulta")
        Select(self.find_healed([(By.ID, "vc-especialidad")])).select_by_visible_text(especialidad_visible)

        motivo_el = self.find_healed([(By.ID, "vc-motivo")])
        motivo_el.clear()
        motivo_el.send_keys(motivo)

        self.find_healed([(By.ID, "btn-reservar-vc")]).click()
        alert = self.wait.until(
            lambda d: d.find_element(By.ID, "vc-resultado-alert")
            if "show" in d.find_element(By.ID, "vc-resultado-alert").get_attribute("class")
            else False
        )
        return alert.text
