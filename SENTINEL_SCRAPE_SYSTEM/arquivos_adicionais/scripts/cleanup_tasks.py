from app.tasks import celery_app

celery_app.control.purge()  # Limpa todas as tarefas concluídas
