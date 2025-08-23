import os  # Importation du module os pour les opérations système
import shutil  # Importation du module shutil pour les opérations de fichiers de haut niveau
import hashlib  # Importation du module hashlib pour les fonctions de hachage
import zipfile  # Importation du module zipfile pour la manipulation des fichiers ZIP
import tarfile  # Importation du module tarfile pour la manipulation des fichiers TAR
import sys   # Importation du module sys pour la manipulation des operations du systeme
import time  # Importation du module time pour la manipulation du temps
import winsound  # Ajout du module winsound pour le son

"""/////////////////////////////////////////////////////////////////////////////////////////////////////////////////"""
"""///////////////////////////// ANIMATION DU CHARGEMENT ///////////////////////////////////////////////////////////"""
"""/////////////////////////////////////////////////////////////////////////////////////////////////////////////////"""

# Fonction pour jouer un son (ajouter à la fin du chargement)
def play_sound():
    winsound.Beep(1000, 500) # Joue un son de 1000 Hz pendant 500 ms
    
# Fonction pour afficher une animation de chargement
def loading_animation(message, max_steps=20):
    """Affiche une animation de chargement simple avec des étoiles ."""

    sys.stdout.write(f"{message}")
    sys.stdout.flush()
    for i in range(max_steps):
        # Affiche des points qui se rajoutent à chaque itération
        sys.stdout.write(f'\r{message}{"*" * (i + 1)}')
        sys.stdout.flush()
        time.sleep(0.2)  # Pause entre chaque ajout de point
    sys.stdout.write(f'\r{message}{"*" * max_steps} DONE!\n')
    sys.stdout.flush()
    play_sound()

"""/////////////////////////////////////////////////////////////////////////////////////////////////////////////////"""
"""///////////////////////////// LES FONCTIONS DU PROGRAMME ///////////////////////////////////////////////////////////"""
"""/////////////////////////////////////////////////////////////////////////////////////////////////////////////////"""

def calculate_checksum(file_path):
    """Calcule le hash SHA-256 d'un fichier pour vérifier son intégrité."""
    try:
        hasher = hashlib.sha256()  # Création d'un objet de hachage SHA-256
        with open(file_path, 'rb') as f:  # Ouverture du fichier en mode binaire
            while chunk := f.read(8192):  # Lecture du fichier par blocs de 8192 octets
                hasher.update(chunk)  # Mise à jour du hachage avec le bloc lu
        return hasher.hexdigest()  # Retourne le hachage sous forme de chaîne hexadécimale
    except Exception as e:
        print(f"Erreur lors du calcul du checksum pour {file_path}: {e}")  # Affiche un message d'erreur en cas d'exception
        return None  # Retourne None en cas d'erreur


def backup_files(file_list, backup_name, format='zip'):
    """Crée une sauvegarde compressée des fichiers spécifiés."""

    backup_path = f"{backup_name}.{format}"  # Détermine le chemin de la sauvegarde avec le format spécifié
    try:
        loading_animation("Chargement en cours: ", max_steps=30)  # Animation de chargement pendant la sauvegarde
        if format == 'zip':
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:  # Crée un fichier ZIP
                for file in file_list:
                    if os.path.exists(file):  # Vérifie si le fichier existe
                        zipf.write(file, os.path.basename(file))  # Ajoute le fichier au ZIP
        elif format == 'tar.gz':
            with tarfile.open(backup_path, 'w:gz') as tar:  # Crée un fichier TAR.GZ
                for file in file_list:
                    if os.path.exists(file):  # Vérifie si le fichier existe
                        tar.add(file, arcname=os.path.basename(file))  # Ajoute le fichier au TAR.GZ
        else:
            raise ValueError("Format non supporté. Utilisez 'zip' ou 'tar.gz'.")  # Lève une exception si le format n'est pas supporté
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {e}")  # Affiche un message d'erreur en cas d'exception
        return None  # Retourne None en cas d'erreur

    return backup_path  # Retourne le chemin de la sauvegarde créée


def verify_backup(backup_path, original_files):
    """Vérifie l'intégrité des fichiers en comparant les checksums."""

    temp_dir = "temp_restore"  # Nom du dossier temporaire pour l'extraction
    try:
        os.makedirs(temp_dir, exist_ok=True)  # Crée le dossier temporaire s'il n'existe pas
        extracted_files = []  # Liste pour stocker les fichiers extraits

        loading_animation("Chargement en cours: ", max_steps=20)  # Animation de chargement pendant la vérification
        if backup_path.endswith('.zip'):
            with zipfile.ZipFile(backup_path, 'r') as zipf:  # Ouvre le fichier ZIP en lecture
                zipf.extractall(temp_dir)  # Extrait tous les fichiers dans le dossier temporaire
                extracted_files = zipf.namelist()  # Récupère la liste des fichiers extraits
        elif backup_path.endswith('.tar.gz'):
            with tarfile.open(backup_path, 'r:gz') as tar:  # Ouvre le fichier TAR.GZ en lecture
                tar.extractall(temp_dir,filter=lambda x: x)  # Extrait tous les fichiers dans le dossier temporaire
                extracted_files = tar.getnames()  # Récupère la liste des fichiers extraits
        integrity_ok = True  # Variable pour suivre l'état de l'intégrité

        for file in extracted_files:
            orig_file = os.path.join(temp_dir, file)  # Chemin du fichier extrait
            orig_path = next((f for f in original_files if os.path.basename(f) == file), None)  # Trouve le chemin du fichier original correspondant
            if orig_path and os.path.exists(orig_file):  # Vérifie si le fichier original existe
                if calculate_checksum(orig_path) != calculate_checksum(orig_file):  # Compare les checksums
                    print(f"[ERREUR] Intégrité compromise pour {file}")  # Affiche un message d'erreur si les checksums ne correspondent pas
                    integrity_ok = False  # Met à jour l'état de l'intégrité
        shutil.rmtree(temp_dir)  # Supprime le dossier temporaire
        return integrity_ok  # Retourne l'état de l'intégrité

    except Exception as e:
        print(f"Erreur lors de la vérification de la sauvegarde: {e}")  # Affiche un message d'erreur en cas d'exception
        shutil.rmtree(temp_dir)  # Supprime le dossier temporaire en cas d'erreur
        return False  # Retourne False en cas d'erreur

def clear_screen():
    """Efface l'écran pour une interface plus propre."""
    os.system('cls' if os.name == 'nt' else 'clear')
    time.sleep(0.1)  # Pause pour laisser le temps à l'écran de s'effacer


"""/////////////////////////////////////////////////////////////////////////////////////////////////////////////////"""
"""///////////////////////////// INTERACTION - UTILISATEUR ///////////////////////////////////////////////////////////"""
"""/////////////////////////////////////////////////////////////////////////////////////////////////////////////////"""

# Exemple d'utilisation
if __name__ == "__main__":
    files_to_backup = ["test1.txt", "test2.txt"]
    backup_file = "backup"  # Nom du fichier sans extension (le format est ajouté dynamiquement)

    while True:
        clear_screen()
        print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
        print("================= BIENVENUE DANS NOTRE APPLICATION ======================")
        print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
        print("////////////////////////////// MENU /////////////////////////////////////")
        print("1. Créer une nouvelle sauvegarde")
        print("2. Vérifier l'intégrité")
        print("3. Quitter")
        choice = input("Choisir une option (1/2/3): ")

        if choice == "1":
            # Mode création de sauvegarde
            print("\nChoisissez le format de sauvegarde :")
            print("1. ZIP (.zip)")
            print("2. TAR.GZ (.tar.gz)")
            format_choice = input("Choisir une option (1/2): ")

            if format_choice == "1":
                backup_format = "zip"
            elif format_choice == "2":
                backup_format = "tar.gz"
            else:
                print("Option invalide ! Utilisation du format ZIP par défaut.")
                backup_format = "zip"

            print(f"\nCréation de la sauvegarde en format {backup_format}...")
            backup_path = backup_files(files_to_backup, "backup", backup_format)  # Création de la sauvegarde
            if backup_path:
                print(f"Sauvegarde '{backup_path}' créée avec succès.")
            else:
                print("❌ Erreur lors de la création de la sauvegarde.")

        elif choice == "2":
            # Mode vérification SEULEMENT
            print("\nVérification de l'intégrité...")
            if verify_backup(f"{backup_file}.{backup_format}", files_to_backup):
                print("✅ Sauvegarde intègre !")  # Affiche ce message lorsque la sauvegarde est intègre
            else:
                print("❌ Problème d'intégrité détecté !")  # Affiche ce message lorsqu'il y a un problème d'intégrité

        elif choice == "3":
            # Demande de confirmation
            choice2 = input("Voulez-vous vraiment quitter ? (o/n): ").strip().lower()
            if choice2 == "o":
                print("Merci d'avoir utilisé notre programme !")
                break  # Quitte le programme
            else:
                clear_screen()  # Efface l'écran si l'utilisateur ne veut pas quitter
        else:
            print("Option invalide ! Veuillez choisir entre 1, 2 et 3 svp !")


