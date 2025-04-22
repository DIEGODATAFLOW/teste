from app.tasks import celery_app

if __name__ == "__main__":
    celery_app.worker_main(
        argv=[
            "worker",
            "--loglevel=info",
            "--pool=solo",
        ]  # Usando pool solo para evitar problemas com o Selenium
    )
