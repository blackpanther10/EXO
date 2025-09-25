tasks = []

def add_task(task: str) -> None:
    """Ajoute une tâche à la liste."""
    tasks.append(task)

def list_tasks():
    """Retourne la liste des tâches."""
    return tasks