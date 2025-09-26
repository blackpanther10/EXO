# EXO
# Projet CI/CD – Déploiement Multi-Environnements (DEV & PROD)

## Auteur
**Chams Eddine Zaiem**  
Master Cybersécurité & Cloud, IPSSI Paris  
Cloud Engineer and DevOps Enthusiast  

---

## 🧪 Contexte du projet
Ce projet est un **exercice final DevOps** visant à automatiser le cycle de vie complet d’une application Web sur deux environnements :

- **Développement (DEV)** : serveur simulé sur Docker, port 2222
- **Production (PROD)** : serveur simulé sur Docker, port 2200

Objectifs :
- Gestion propre du code via Git multi-branches (`main`, `dev`, `feature/*`)
- Compilation ou tests automatiques de l'application
- Déploiement automatique sur DEV et PROD via Ansible
- Sécurisation des accès (GitHub Secrets et Ansible Vault)

Durée : 2 jours  
Scénario réel : Déploiement multi-environnements d’une application Web avec pipeline CI/CD complet

---

## 🎯 Objectifs pédagogiques
- Gérer un projet Git multi-branches
- Automatiser un pipeline complet CI/CD avec GitHub Actions
- Déployer sur deux environnements distincts via Ansible
- Sécuriser les accès avec des secrets (Vault, SSH Keys)
- Structurer les rôles et inventaires Ansible proprement

---

## 📂 Architecture du projet

project-root/
├── .github/
│ └── workflows/
│ └── pipeline.yml
├── ansible/
│ ├── inventory/
│ │ ├── dev.ini
│ │ └── prod.ini
│ ├── playbooks/
│ │ ├── deploy-dev.yml
│ │ └── deploy-prod.yml
│ └── roles/
│ └── app/
│ └── (handlers, tasks, templates…)
├── app/
│ ├── main.py
│ └── utils.py
├── vault.yml
├── README.md
└── requirements.txt

markdown
Copier le code

---

## 📋 Étapes du projet

### 🔧 Étape 1 – Préparation du dépôt et du code source
- Initialisation d’un dépôt Git propre
- Structuration des branches : `main`, `dev`, `feature/*`
- Ajout d’une mini-application Python testable
- Ajout d’un `.gitignore` adapté

### ⚙ Étape 2 – Serveurs DEV & PROD avec Docker
- Création de deux conteneurs Docker
  - `serveur-dev` → port 2222
  - `serveur-prod` → port 2200
- Configuration SSH et accès root
- Vérification de l’accès via Ansible

### 📁 Étape 3 – Inventaires Ansible
**dev.ini**
```ini
[dev]
localhost ansible_port=2222 ansible_user=root ansible_connection=ssh ansible_ssh_common_args='-o StrictHostKeyChecking=no'
prod.ini

ini
Copier le code
[prod]
localhost ansible_port=2200 ansible_user=root ansible_connection=ssh ansible_ssh_common_args='-o StrictHostKeyChecking=no'
Définition des hôtes, ports, utilisateurs, clés SSH

Variables sensibles dans vault.yml ou GitHub Secrets

🧱 Étape 4 – Playbooks Ansible
deploy-dev.yml

yaml
Copier le code
---
- name: Déploiement DEV - Application Python depuis Git
  hosts: dev
  vars_files:
    - ../vault.yml
  tasks:
    - name: Installer Git, Python et pip
      apt:
        name: "{{ item }}"
        state: present
        update_cache: yes
      loop:
        - git
        - python3
        - python3-pip

    - name: Créer le répertoire de l'application
      file:
        path: /opt/app-dev
        state: directory

    - name: Cloner le dépôt depuis GitHub
      git:
        repo: 'https://github.com/blackpanther10/EXO.git'
        dest: /opt/app-dev
        version: dev
        force: yes

    - name: Installer dépendances Python (requirements.txt)
      pip:
        requirements: /opt/app-dev/requirements.txt
      ignore_errors: yes

    - name: Exécuter le script Python
      command: python3 main.py
      args:
        chdir: /opt/app-dev/app
      register: python_output

    - name: Afficher le résultat
      debug:
        msg: "Python script executed! Output:\n{{ python_output.stdout }}"

    - name: Créer un fichier de confirmation
      copy:
        content: "Déploiement DEV Python effectué avec succès le {{ ansible_date_time.iso8601 }}"
        dest: /opt/app-dev/deploy.log
deploy-prod.yml

yaml
Copier le code
---
- name: Déploiement PROD - Application Python depuis Git
  hosts: prod
  vars_files:
    - ../vault.yml
  tasks:
    - name: Installer Git, Python et pip
      apt:
        name: "{{ item }}"
        state: present
        update_cache: yes
      loop:
        - git
        - python3
        - python3-pip

    - name: Créer le répertoire de l'application
      file:
        path: /opt/app-prod
        state: directory

    - name: Cloner le dépôt depuis GitHub
      git:
        repo: 'https://github.com/blackpanther10/EXO.git'
        dest: /opt/app-prod
        version: main
        force: yes

    - name: Installer dépendances Python
      pip:
        requirements: /opt/app-prod/requirements.txt
      ignore_errors: yes

    - name: Exécuter le script Python
      command: python3 main.py
      args:
        chdir: /opt/app-prod/app
      register: python_output

    - name: Afficher le résultat
      debug:
        msg: "Python script executed! Output:\n{{ python_output.stdout }}"

    - name: Créer un fichier de confirmation
      copy:
        content: "Déploiement PROD Python effectué avec succès le {{ ansible_date_time.iso8601 }}"
        dest: /opt/app-prod/deploy.log
🔄 Étape 5 – Pipeline GitHub Actions
pipeline.yml

yaml
Copier le code
name: CI/CD Pipeline

on:
  push:
    branches:
      - dev
      - main

jobs:
  build-and-deploy:
    runs-on: self-hosted

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Run lint/tests
        run: |
          echo "Ici tu peux lancer pytest ou flake8 par exemple"
          # pytest tests/
          # flake8 app/

      - name: Install Ansible
        run: |
          python -m pip install --upgrade pip
          pip install ansible

      - name: Deploy with Ansible
        if: github.ref == 'refs/heads/dev' || github.ref == 'refs/heads/main'
        env:
          DEV_SSH_KEY: ${{ secrets.DEV_SSH_KEY }}
          PROD_SSH_KEY: ${{ secrets.PROD_SSH_KEY }}
          ANSIBLE_VAULT_PASSWORD: ${{ secrets.ANSIBLE_VAULT_PASSWORD }}
        run: |
          mkdir -p ~/.ssh
          if [ "${GITHUB_REF}" == "refs/heads/dev" ]; then
            echo "$DEV_SSH_KEY" > ~/.ssh/id_rsa
          else
            echo "$PROD_SSH_KEY" > ~/.ssh/id_rsa
          fi
          chmod 600 ~/.ssh/id_rsa

          echo "$ANSIBLE_VAULT_PASSWORD" > ~/.vault_pass.txt
          chmod 600 ~/.vault_pass.txt

          if [ "${GITHUB_REF}" == "refs/heads/dev" ]; then
            ansible-playbook ansible/playbooks/deploy-dev.yml \
              -i ansible/inventory/dev.ini \
              --vault-password-file ~/.vault_pass.txt \
              -e "@ansible/vault.yml" \
              -e "ansible_password={{ dev_password }}"
          else
            ansible-playbook ansible/playbooks/deploy-prod.yml \
              -i ansible/inventory/prod.ini \
              --vault-password-file ~/.vault_pass.txt \
              -e "@ansible/vault.yml" \
              -e "ansible_password={{ prod_password }}"
          fi
🐍 Application Python
app/utils.py

python
Copier le code
tasks = []

def add_task(task: str) -> None:
    """Ajoute une tâche à la liste."""
    tasks.append(task)

def list_tasks():
    """Retourne la liste des tâches."""
    return tasks
app/main.py

python
Copier le code
from utils import add_task, list_tasks

if __name__ == "__main__":
    add_task("Apprendre GitHub Actions")
    add_task("Configurer Ansible")
    print("Tâches actuelles :", list_tasks())
🔐 Gestion des secrets
GitHub Secrets : DEV_SSH_KEY, PROD_SSH_KEY, ANSIBLE_VAULT_PASSWORD

Ansible Vault : vault.yml pour stocker dev_password et prod_password

✅ Validation et livrables
Projet structuré avec Git, branches et historique clair

Serveurs DEV et PROD opérationnels

Playbooks Ansible propres et maintenables

Secrets bien gérés

Pipeline GitHub Actions déclenche les bons déploiements

Documentation claire et complète

📄 Remarques
Les ports Docker peuvent être modifiés si conflit

Les tests Python sont optionnels (pytest ou flake8)

Le dépôt GitHub doit être accessible depuis Ansible pour cloner l’application