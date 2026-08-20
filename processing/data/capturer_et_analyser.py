import os
import json
import time
import requests
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

api_key = ""      # <-- mets ta cle Gemini ici
webcam_url = ""   # <-- mets l'URL IP Webcam ici, ex: "http://192.168.1.42:8080/shot.jpg"

# Temperature de chauffe du robot : constante materielle (pas de reglage
# variable), meme valeur pour toutes les etapes "chauffer" de tous les
# plats. TODO : mesurer la vraie valeur et la remplacer ici.
TEMPERATURE_CUISSON_C = None  # <-- a definir une fois mesuree

# Nombre de tentatives max et delai (secondes) entre chaque tentative,
# en cas de probleme de connexion (reseau coupe, telephone injoignable,
# serveur Gemini surcharge, etc.)
MAX_TENTATIVES = 3
DELAI_ENTRE_TENTATIVES = 5

def capturer_photo():
    for tentative in range(1, MAX_TENTATIVES + 1):
        try:
            print(f"Capture de la photo depuis {webcam_url} (tentative {tentative}/{MAX_TENTATIVES})...")
            reponse = requests.get(webcam_url, timeout=5)
            reponse.raise_for_status()  # leve une erreur si le telephone ne repond pas
            print("Photo recuperee avec succes.")
            return reponse.content
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion au telephone : {e}")
            if tentative < MAX_TENTATIVES:
                print(f"Nouvelle tentative dans {DELAI_ENTRE_TENTATIVES}s...")
                time.sleep(DELAI_ENTRE_TENTATIVES)
            else:
                raise RuntimeError(
                    "Impossible de recuperer la photo apres plusieurs tentatives. "
                    "Verifie que l'app IP Webcam est lancee et que le telephone "
                    "est bien sur le meme reseau WiFi."
                ) from e


def analyser_avec_gemini(image_bytes):
    """Envoie l'image a Gemini et retourne le plan de preparation en JSON."""
    client = genai.Client(api_key=api_key)

    schema = {
        "type": "object",
        "properties": {
            "contient_non_comestible": {
                "type": "boolean",
                "description": (
                    "true si la photo contient au moins un objet qui n'est "
                    "pas un ingredient alimentaire (objet, outil, dechet, "
                    "produit non alimentaire, etc.)"
                ),
            },
            "message_alerte": {
                "type": "string",
                "description": (
                    "Si contient_non_comestible est true, explique "
                    "brievement ce qui a ete detecte et qui n'est pas "
                    "comestible. Laisser une chaine vide sinon."
                ),
            },
            "plats": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nom": {"type": "string"},
                        "preparation_manuelle": {
                            "type": "array",
                            "description": (
                                "Instructions textuelles pour l'humain : eplucher, "
                                "couper, laver, etc. Doivent couvrir TOUTE la "
                                "preparation necessaire, sans rien laisser a faire "
                                "une fois le cuiseur lance."
                            ),
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
                                        "enum": [0, 1],
                                        "description": (
                                            "Pour l'action 'chauffer' uniquement : 1 pour "
                                            "allumer la plaque chauffante, 0 pour l'eteindre. "
                                            "Mettre 0 pour toute autre action."
                                        ),
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
        "required": ["contient_non_comestible", "message_alerte", "plats"],
    }

    prompt = (
        "Regarde d'abord attentivement la photo pour verifier si TOUS les "
        "objets visibles sont des ingredients alimentaires comestibles. "
        "Si tu detectes un objet non comestible (outil, dechet, embalage, "
        "objet quelconque, produit non alimentaire, etc.), mets "
        "contient_non_comestible a true, decris le probleme dans "
        "message_alerte, et laisse plats vide (liste vide). Dans ce cas, "
        "n'invente AUCUN plat. "
        "\n\n"
        "Si tous les objets sont bien des ingredients alimentaires "
        "comestibles, mets contient_non_comestible a false et "
        "message_alerte a une chaine vide, puis continue normalement : "
        "\n\n"
        "Les ingredients visibles sur cette photo sont deja physiquement "
        "presents dans le recipient, MAIS a l'etat brut : non epluches, "
        "non coupes, non laves, tels qu'ils sortent du marche ou du frigo. "
        "Identifie les ingredients presents sur la photo, puis propose tous les "
        "plats realisables avec ces ingredients, prepares en deux phases "
        "distinctes et sans AUCUNE intervention humaine entre les deux : "
        "\n\n"
        "PHASE 1 (humaine) : liste precise de toutes les actions de "
        "preparation necessaires (eplucher, couper, laver, casser les "
        "oeufs, etc.) que l'utilisateur doit faire a la main avant de "
        "mettre les ingredients dans le cuiseur. Cette liste doit rendre "
        "les ingredients INTEGRALEMENT prets a cuire, sans aucune etape "
        "manuelle restante apres. "
        "\n\n"
        "PHASE 2 (robot, automatique, sans humain) : une fois les "
        "ingredients prepares et deposes dans le cuiseur, le robot prend "
        "le relais. Il peut UNIQUEMENT : chauffer (a une temperature "
        "fixe non reglable, ne pas indiquer de valeur de temperature), "
        "doser de l'eau, du sel, ou de l'huile en quantite precise, et "
        "activer un melangeur. Il n'y a PAS de doseur de sucre. Il ne "
        "peut ni ajouter d'autres ingredients solides ni retirer quoi "
        "que ce soit du cuiseur, ni couper/eplucher quoi que ce soit (ca "
        "doit deja avoir ete fait en phase 1). "
        "Pour controler la plaque chauffante, utilise une etape avec "
        "action='chauffer' et activer=1 pour l'allumer, puis plus tard "
        "une autre etape avec action='chauffer' et activer=0 pour "
        "l'eteindre. Utilise ce mecanisme d'allumage/extinction explicite "
        "a chaque fois qu'il faut demarrer ou arreter la chauffe (par "
        "exemple avant de melanger si besoin, ou a la fin de la cuisson). "
        "Pour toutes les autres actions (doser, melanger, attendre), mets "
        "toujours activer a 0. "
        "Decris cette phase comme une suite d'etapes executables avec des "
        "valeurs precises : durees en secondes, quantites exactes "
        "d'eau/sel/huile."
    )

    for tentative in range(1, MAX_TENTATIVES + 1):
        try:
            print(f"Envoi de l'image a Gemini pour analyse (tentative {tentative}/{MAX_TENTATIVES})...")
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
            print("Reponse recue.")
            return json.loads(response.text)
        except (genai_errors.ServerError, genai_errors.ClientError) as e:
            # ServerError = probleme cote Google (ex: 503 surcharge)
            # ClientError peut aussi couvrir certains 429 (trop de requetes)
            print(f"Erreur API Gemini : {e}")
            if tentative < MAX_TENTATIVES:
                print(f"Nouvelle tentative dans {DELAI_ENTRE_TENTATIVES}s...")
                time.sleep(DELAI_ENTRE_TENTATIVES)
            else:
                raise RuntimeError(
                    "Gemini n'a pas repondu apres plusieurs tentatives. "
                    "Reessaie plus tard."
                ) from e
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion internet : {e}")
            if tentative < MAX_TENTATIVES:
                print(f"Nouvelle tentative dans {DELAI_ENTRE_TENTATIVES}s...")
                time.sleep(DELAI_ENTRE_TENTATIVES)
            else:
                raise RuntimeError(
                    "Pas de connexion internet apres plusieurs tentatives."
                ) from e


def afficher_resultat(data):
    if data.get("contient_non_comestible"):
        print("\n /!\\ ALERTE : objet(s) non comestible(s) detecte(s) dans le recipient")
        print(f"    {data.get('message_alerte', '')}")
        print("    Aucun plat propose. Retire l'objet et reessaie.")
        return

    for plat in data["plats"]:
        print(f"\n=== {plat['nom']} ===")

        print("  -- Phase 1 : preparation manuelle --")
        for i, action in enumerate(plat["preparation_manuelle"], start=1):
            print(f"    {i}. {action}")

        print("  -- Phase 2 : cuisson robot (automatique) --")
        print(f"    (temperature de chauffe fixe : {TEMPERATURE_CUISSON_C})")
        for i, etape in enumerate(plat["etapes_robot"], start=1):
            print(f"    Etape {i} [{etape['action']}]:", end=" ")
            details = []
            if etape["action"] == "chauffer":
                details.append("plaque=ON" if etape["activer"] == 1 else "plaque=OFF")
            if etape["duree_secondes"] > 0:
                details.append(f"{etape['duree_secondes']}s")
            if etape["eau_ml"] > 0:
                details.append(f"eau={etape['eau_ml']}ml")
            if etape["sel_g"] > 0:
                details.append(f"sel={etape['sel_g']}g")
            if etape["huile_ml"] > 0:
                details.append(f"huile={etape['huile_ml']}ml")
            if etape["melanger"]:
                details.append("melangeur=ON")
            print(", ".join(details) if details else "-")


if __name__ == "__main__":
    photo = capturer_photo()
    resultat = analyser_avec_gemini(photo)
    afficher_resultat(resultat)

    if resultat.get("contient_non_comestible"):
        # Pas de fichier recettes ecrit : rien d'exploitable pour le robot
        print("\nAucun fichier recettes_robot.json genere (alerte non comestible).")
    else:
        dossier_script = os.path.dirname(os.path.abspath(__file__))
        chemin_json = os.path.join(dossier_script, "recettes_robot.json")

        with open(chemin_json, "w", encoding="utf-8") as f:
            json.dump(resultat, f, ensure_ascii=False, indent=2)
        print(f"\nResultat sauvegarde dans {chemin_json}")
