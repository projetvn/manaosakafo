import os
import json
import requests
from google import genai
from google.genai import types

api_key = 
webcam_url = 

def capturer_photo():
    print(f"Capture de la photo depuis {webcam_url} ...")
    reponse = requests.get(webcam_url, timeout=5)
    reponse.raise_for_status()  #leve une erreur si le telephone ne repond pas
    print("Photo recuperee avec succes.")
    return reponse.content


def analyser_avec_gemini(image_bytes):
    """Envoie l'image a Gemini et retourne le plan de preparation en JSON."""
    client = genai.Client(api_key=api_key)

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
                                    "temperature_celsius": {"type": "integer"},
                                    "duree_secondes": {"type": "integer"},
                                    "eau_ml": {"type": "integer"},
                                    "sel_g": {"type": "integer"},
                                    "sucre_g": {"type": "integer"},
                                    "huile_ml": {"type": "integer"},
                                    "melanger": {"type": "boolean"},
                                },
                                "required": [
                                    "action", "temperature_celsius", "duree_secondes",
                                    "eau_ml", "sel_g", "sucre_g", "huile_ml", "melanger",
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
        "Les ingredients visibles sur cette photo sont deja physiquement "
        "presents dans le recipient, MAIS a l'etat brut : non epluches, "
        "non coupes, non laves, tels qu'ils sortent du marche ou du frigo. "
        "Identifie les ingredients presents sur la photo, puis propose 2 "
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
        "le relais. Il peut UNIQUEMENT : chauffer a une temperature "
        "donnee, doser de l'eau, du sel, du sucre, ou de l'huile en "
        "quantite precise, et activer un melangeur. Il ne peut ni ajouter "
        "d'autres ingredients solides ni retirer quoi que ce soit du "
        "cuiseur, ni couper/eplucher quoi que ce soit (ca doit deja avoir "
        "ete fait en phase 1). Decris cette phase comme une suite "
        "d'etapes executables avec des valeurs precises : temperatures en "
        "degres Celsius, durees en secondes, quantites exactes "
        "d'eau/sel/sucre/huile."
    )

    print("Envoi de l'image a Gemini pour analyse...")
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


def afficher_resultat(data):
    for plat in data["plats"]:
        print(f"\n=== {plat['nom']} ===")

        print("  -- Phase 1 : preparation manuelle --")
        for i, action in enumerate(plat["preparation_manuelle"], start=1):
            print(f"    {i}. {action}")

        print("  -- Phase 2 : cuisson robot (automatique) --")
        for i, etape in enumerate(plat["etapes_robot"], start=1):
            print(f"    Etape {i} [{etape['action']}]:", end=" ")
            details = []
            if etape["temperature_celsius"] > 0:
                details.append(f"{etape['temperature_celsius']}C")
            if etape["duree_secondes"] > 0:
                details.append(f"{etape['duree_secondes']}s")
            if etape["eau_ml"] > 0:
                details.append(f"eau={etape['eau_ml']}ml")
            if etape["sel_g"] > 0:
                details.append(f"sel={etape['sel_g']}g")
            if etape["sucre_g"] > 0:
                details.append(f"sucre={etape['sucre_g']}g")
            if etape["huile_ml"] > 0:
                details.append(f"huile={etape['huile_ml']}ml")
            if etape["melanger"]:
                details.append("melangeur=ON")
            print(", ".join(details) if details else "-")


if __name__ == "__main__":
    photo = capturer_photo()
    resultat = analyser_avec_gemini(photo)
    afficher_resultat(resultat)

    dossier_script = os.path.dirname(os.path.abspath(__file__))
    chemin_json = os.path.join(dossier_script, "recettes_robot.json")

    with open(chemin_json, "w", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False, indent=2)
    print(f"\nResultat sauvegarde dans {chemin_json}")
