import os
import sys
import json
import time
import requests
from google import genai
from google.genai import types

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
API_KEY = ""  # <-- Mets ta clé Gemini ici
URL_WEBCAM = "http://192.168.1.50:8080/shot.jpg"  # <-- Remplace par l'IP de ton smartphone / webcam IP
MODELE_GEMINI = "gemini-3.6-flash"

def capturer_photo_webcam(url):
    """Télécharge l'image instantanée depuis le serveur IP Webcam."""
    print(f"[python] Capture de la photo depuis {url}...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("[python] Photo capturée avec succès !")
            return response.content
        else:
            raise RuntimeError(f"Erreur HTTP {response.status_code} lors de la capture d'image.")
    except Exception as e:
        raise RuntimeError(f"Impossible de joindre la webcam IP : {e}")

def executer_requete_gemini(client, contents, schema):
    """Exécute la requête avec la gestion des erreurs et des réessais."""
    duree_attente = 5

    for tentative in range(1, 3):
        try:
            print(f"[python] Envoi avec {MODELE_GEMINI} (tentative {tentative}/2)...")
            response = client.models.generate_content(
                model=MODELE_GEMINI,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", 
                    response_schema=schema
                ),
            )
            print(f"[python] Réponse reçue avec succès via {MODELE_GEMINI} !")
            return json.loads(response.text)

        except Exception as e:
            print(f"[python] Erreur avec {MODELE_GEMINI} : {e}")
            if "503" in str(e):
                print(f"[python] Serveur occupé. Attente de {duree_attente}s...")
                time.sleep(duree_attente)
            else:
                time.sleep(1)

    raise RuntimeError("La requête auprès du modèle Gemini a échoué.")

# -------------------------------------------------------------------------
# ÉTAPE 1 : Capture photo -> Analyse ingrédients + Proposer Catégories
# -------------------------------------------------------------------------
def etape1_categories(client, image_bytes):
    schema = {
        "type": "object",
        "properties": {
            "contient_non_comestible": {"type": "boolean"},
            "message_alerte": {"type": "string"},
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Types de cuisine réalisables (ex: Cuisine Européenne, Asiatique, etc.)"
            }
        },
        "required": ["contient_non_comestible", "message_alerte", "categories"]
    }

    prompt = (
        "Analyse l'image du récipient.\n"
        "1. Identifie tous les éléments / ingrédients présents.\n"
        "2. Vérifie si tous les éléments sont comestibles. Si un objet non comestible est détecté, "
        "mets contient_non_comestible=true et explique le problème dans message_alerte.\n"
        "3. Si tout est comestible, mets contient_non_comestible=false et propose 3 à 4 catégories "
        "de cuisine réalisables avec les ingrédients identifiés."
    )

    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    return executer_requete_gemini(client, [prompt, image_part], schema)

# -------------------------------------------------------------------------
# ÉTAPE 2 : Proposer les plats pour la catégorie choisie
# -------------------------------------------------------------------------
def etape2_plats(client, image_bytes, categorie_choisie):
    schema = {
        "type": "object",
        "properties": {
            "plats_disponibles": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Noms des plats réalisables"
            }
        },
        "required": ["plats_disponibles"]
    }

    prompt = (
        f"En te basant sur l'image des ingrédients disponibles, "
        f"liste 3 à 4 noms de plats de la catégorie '{categorie_choisie}' qu'il est possible de cuisiner."
    )

    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    return executer_requete_gemini(client, [prompt, image_part], schema)

# -------------------------------------------------------------------------
# ÉTAPE 3 : Générer les étapes de la recette (Humain + Robot)
# -------------------------------------------------------------------------
def etape3_etapes_plat(client, image_bytes, plat_choisi):
    schema = {
        "type": "object",
        "properties": {
            "plats": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nom": {"type": "string"},
                        "preparation_manuelle": {
                            "type": "array",
                            "description": "Instructions de préparation pour l'humain avant la cuisson.",
                            "items": {"type": "string"},
                        },
                        "etapes_robot": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "action": {
                                        "type": "string",
                                        "enum": ["chauffer", "doser", "melanger", "attendre"],
                                    },
                                    "activer": {
                                        "type": "integer",
                                        "enum": ["0", "1"],  # Guillemets requis pour validation Pydantic
                                        "description": "1 pour allumer la plaque chauffante, 0 pour l'éteindre.",
                                    },
                                    "duree_secondes": {"type": "integer"},
                                    "eau_ml": {"type": "integer"},
                                    "sel_g": {"type": "integer"},
                                    "huile_ml": {"type": "integer"},
                                    "melanger": {"type": "boolean"},
                                },
                                "required": [
                                    "action", "activer", "duree_secondes",
                                    "eau_ml", "sel_g", "huile_ml", "melanger",
                                ],
                            },
                        },
                    },
                    "required": ["nom", "preparation_manuelle", "etapes_robot"],
                },
            }
        },
        "required": ["plats"],
    }

    prompt = (
        f"Regarde l'image des ingrédients et génère la recette détaillée pour le plat : '{plat_choisi}'.\n\n"
        "PHASE 1 (humaine) : liste précise de toutes les actions de préparation nécessaires "
        "(éplucher, couper, laver, etc.) à faire à la main avant la cuisson.\n\n"
        "PHASE 2 (robot) : une suite d'étapes automatiques exécutables par le robot cuiseur. "
        "Actions possibles : chauffer (activer=1 pour allumer, 0 pour éteindre), doser, mélanger, ou attendre. "
        "Fournis des valeurs précises pour duree_secondes, eau_ml, sel_g, huile_ml et melanger (true/false)."
    )

    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    return executer_requete_gemini(client, [prompt, image_part], schema)

# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------
if __name__ == "__main__":
    client = genai.Client(api_key=API_KEY)
    
    etape = sys.argv[1] if len(sys.argv) > 1 else "1"
    
    # 1. Capture de la photo en direct via IP Webcam
    image_bytes = capturer_photo_webcam(URL_WEBCAM)
    
    res = {}

    if etape == "1":
        res = etape1_categories(client, image_bytes)

    elif etape == "2":
        categorie = sys.argv[2] if len(sys.argv) > 2 else "Cuisine Européenne"
        print(f"[python] Catégorie reçue : {categorie}")
        res = etape2_plats(client, image_bytes, categorie)

    elif etape == "3":
        plat = sys.argv[2] if len(sys.argv) > 2 else "Omelette"
        print(f"[python] Plat reçu : {plat}")
        res = etape3_etapes_plat(client, image_bytes, plat)

    # 2. Sauvegarde du fichier JSON pour Processing
    dossier = os.path.dirname(os.path.abspath(__file__))
    chemin_json = os.path.join(dossier, "recettes_robot.json")
    
    with open(chemin_json, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    print(f"[python] Résultat sauvegardé dans {chemin_json}")
