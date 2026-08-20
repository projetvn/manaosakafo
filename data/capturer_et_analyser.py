

import json
import time
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

api_key = "AQ.Ab8RN6Lqty9QmOxnYxeyrPUNq0nv71W6mbVMX8xKrp4XM5nRLg" 


TEMPERATURE_CUISSON_C = 150  

MAX_TENTATIVES = 3
DELAI_ENTRE_TENTATIVES = 5


def analyser_avec_gemini(description_ingredients, simuler_non_comestible=False):
    """Envoie le prompt texte a Gemini et retourne le plan structure en JSON."""
    client = genai.Client(api_key=api_key)

    schema = {
        "type": "object",
        "properties": {
            "contient_non_comestible": {
                "type": "boolean",
                "description": (
                    "true si la description contient au moins un objet qui "
                    "n'est pas un ingredient alimentaire (objet, outil, "
                    "dechet, produit non alimentaire, etc.)"
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
                                        "type": "string",
                                        "enum": ["0", "1"],
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
            },
        },
        "required": ["contient_non_comestible", "message_alerte", "plats"],
    }

    prompt = (
        "Regarde d'abord attentivement la description ci-dessous pour "
        "verifier si TOUS les objets mentionnes sont des ingredients "
        "alimentaires comestibles. Si un objet non comestible (outil, "
        "dechet, emballage, objet quelconque, produit non alimentaire, "
        "etc.) est mentionne, mets contient_non_comestible a true, decris "
        "le probleme dans message_alerte, et laisse plats vide (liste "
        "vide). Dans ce cas, n'invente AUCUN plat. "
        "\n\n"
        "Si tous les objets sont bien des ingredients alimentaires "
        "comestibles, mets contient_non_comestible a false et "
        "message_alerte a une chaine vide, puis continue normalement : "
        "\n\n"
        "Les ingredients suivants sont deja physiquement presents dans le "
        "recipient, MAIS a l'etat brut : non epluches, non coupes, non "
        f"laves, tels qu'ils sortent du marche ou du frigo : {description_ingredients}. "
        "Propose tous les plats realisables avec ces ingredients, "
        "prepares en deux phases distinctes et sans AUCUNE intervention "
        "humaine entre les deux : "
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

    if simuler_non_comestible:
        prompt += (
            "\n\n(Note pour ce test : imagine qu'un tournevis metallique "
            "est aussi visible parmi les ingredients, pour tester la "
            "detection non comestible.)"
        )

    for tentative in range(1, MAX_TENTATIVES + 1):
        try:
            print(f"Envoi du prompt a Gemini (tentative {tentative}/{MAX_TENTATIVES})...")
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
            print("Reponse recue.")
            return json.loads(response.text)
        except (genai_errors.ServerError, genai_errors.ClientError) as e:
            print(f"Erreur API Gemini : {e}")
            if tentative < MAX_TENTATIVES:
                print(f"Nouvelle tentative dans {DELAI_ENTRE_TENTATIVES}s...")
                time.sleep(DELAI_ENTRE_TENTATIVES)
            else:
                raise RuntimeError(
                    "Gemini n'a pas repondu apres plusieurs tentatives."
                ) from e


def afficher_resultat(data):
    if data.get("contient_non_comestible"):
        print("\n /!\\ ALERTE : objet(s) non comestible(s) detecte(s)")
        print(f"    {data.get('message_alerte', '')}")
        print("    Aucun plat propose.")
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
    import os

    # Change ces deux lignes pour tester differents scenarios :
    ingredients_fictifs = "tomates, oeufs, oignons, fromage"
    tester_alerte_non_comestible = False  # mets True pour tester l'alerte

    resultat = analyser_avec_gemini(ingredients_fictifs, tester_alerte_non_comestible)
    afficher_resultat(resultat)

    if resultat.get("contient_non_comestible"):
        dossier_script = os.path.dirname(os.path.abspath(__file__))
        chemin_json = os.path.join(dossier_script, "recettes_robot.json")

        with open(chemin_json, "w", encoding="utf-8") as f:
            json.dump(resultat, f, ensure_ascii=False, indent=2)
        print(f"\nResultat sauvegarde dans {chemin_json}")
    else:
        dossier_script = os.path.dirname(os.path.abspath(__file__))
        chemin_json = os.path.join(dossier_script, "recettes_robot.json")

        with open(chemin_json, "w", encoding="utf-8") as f:
            json.dump(resultat, f, ensure_ascii=False, indent=2)
        print(f"\nResultat sauvegarde dans {chemin_json}")
