from celery import Celery
from app.config import settings
from app.webdriver.setup import get_chrome_driver
from selenium.webdriver.common.by import By
import time

celery_app = Celery(
    "scraping_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


@celery_app.task(bind=True, name="execute_scraping")
def execute_scraping(self, request_data):
    try:
        # Atualiza o status para STARTED
        self.update_state(state="STARTED")

        # Aqui você adapta para o seu scraping existente
        driver = get_chrome_driver(headless=True)

        # Exemplo genérico - substitua pelo seu scraping real
        driver.get(request_data["url"])
        time.sleep(2)  # Simula trabalho

        # Exemplo: extrair título da página
        result = {
            "title": driver.title,
            "url": driver.current_url,
            "additional_data": request_data["parameters"],
        }

        driver.quit()

        return {"status": "SUCCESS", "result": result, "error": None}

    except Exception as e:
        if "driver" in locals():
            driver.quit()
        return {"status": "FAILURE", "result": None, "error": str(e)}
