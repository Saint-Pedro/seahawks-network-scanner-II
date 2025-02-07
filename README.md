# Seahawks Network Scanner

Un outil de scan réseau développé avec Flask et Python, permettant le scan de ports et le ping de serveurs dans le cadre d'un projet MSPR.

## Fonctionnalités

- Scan des ports de la machine locale
- Ping serveur avec mesure de latence
- Affichage des informations système
- Interface web

## Prérequis

- Python 3.8 ou supérieur
- Nmap (Network Mapper)

### Installation de Nmap

#### Windows :
1. Téléchargez Nmap depuis [nmap.org](https://nmap.org/download.html)
2. Exécutez l'installateur
3. Ajoutez Nmap au PATH système

#### Linux :
```bash
sudo apt-get update
sudo apt-get install nmap
```

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/seahawks-network-scanner.git
cd seahawks-network-scanner
```

2. Créez un environnement virtuel :
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Lancement de l'Application

1. Activez l'environnement virtuel (si ce n'est pas déjà fait) :
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Définissez les variables d'environnement Flask :
```bash
# Windows
set FLASK_APP=app
set FLASK_ENV=development

# Linux/Mac
export FLASK_APP=app
export FLASK_ENV=development
```

3. Lancez l'application :
```bash
flask run
```

4. Accédez à l'application dans votre navigateur : `http://127.0.0.1:5000`

## Utilisation

1. Informations Système :
   - Votre adresse IP locale et nom d'hôte sont affichés automatiquement

2. Scanner les Ports Locaux :
   - Cliquez sur "Start Network Scan" pour scanner les ports de votre machine

3. Ping Serveur :
   - Entrez une adresse IP dans le champ de saisie
   - Cliquez sur "Ping Server" pour tester la connectivité et mesurer la latence

## Notes de Sécurité

- Cet outil est destiné uniquement à l'administration et aux tests réseau
- Assurez-vous d'avoir l'autorisation de scanner le réseau/système cible
- Utilisez de manière responsable et conformément aux politiques de sécurité de votre organisation
