from utils import add_task, list_tasks

if __name__ == "__main__":
    add_task("Apprendre GitHub Actions")
    add_task("Configurer Ansible")
    print("Tâches actuelles :", list_tasks())
