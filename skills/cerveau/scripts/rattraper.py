#!/usr/bin/env python3
"""Rattraper : retrouver les conversations (Claude Code, Codex) jamais sauvées dans le cerveau.

Un modèle local (Ollama) lit chaque conversation et note son projet, un résumé, ce qu'il faut
retenir et les idées. L'IA de la session ne lit ensuite que ces notes courtes et les range dans
les fiches. Sans Ollama, les dialogues sont préparés pour qu'un petit modèle (Haiku, Luna) les lise.

Usage :
  rattraper.py trier [--depuis AAAA-MM-JJ] [--max N]   lit les conversations pas encore triées
  rattraper.py rapport                                 notes à ranger (JSON), à donner à l'IA
  rattraper.py marquer [id ...]                        marque comme rangées (toutes si aucun id)
  rattraper.py etat                                    combien de conversations à chaque étape

Réglages (variables d'environnement, facultatives) :
  CERVEAU                       chemin du cerveau (sinon lu dans les règles globales)
  CERVEAU_RATTRAPAGE_MODELE     modèle Ollama (défaut gemma4:12b)
  OLLAMA_HOST                   adresse d'Ollama (défaut http://127.0.0.1:11434)
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rever import cerveau, extraire  # noqa: E402

HOME = Path.home()
ETAT = HOME / ".agents" / "reves" / "rattrapage.json"
PREPARES = HOME / ".agents" / "reves" / "rattrapage"
MODELE = os.environ.get("CERVEAU_RATTRAPAGE_MODELE", "gemma4:12b")
_hote = urllib.parse.urlsplit(("" if "://" in os.environ.get("OLLAMA_HOST", "") else "http://")
                               + (os.environ.get("OLLAMA_HOST") or "127.0.0.1"))
OLLAMA = f"{_hote.scheme}://{(_hote.hostname or '127.0.0.1').replace('0.0.0.0', '127.0.0.1')}:{_hote.port or 11434}"
MORCEAU = 30_000         # caractères de dialogue lus par le modèle local en une fois
MINIMUM = 1_500          # en dessous, rien à retenir
RECENT = 20 * 60         # une conversation modifiée il y a moins de 20 min est peut-être encore ouverte
INTERNES = ("Mode rêve", "Mode rattrapage", "Tu ranges la mémoire")


def lire_etat():
    try:
        return json.loads(ETAT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def ecrire_etat(etat):
    ETAT.parent.mkdir(parents=True, exist_ok=True)
    tmp = ETAT.with_suffix(".tmp")
    tmp.write_text(json.dumps(etat, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(ETAT)


def conversations(depuis):
    """(ia, fichier) des conversations modifiées depuis la date, hors celles encore ouvertes."""
    limite = time.time() - RECENT
    lots = [("claude", (HOME / ".claude" / "projects").glob("*/*.jsonl")),
            ("codex", (HOME / ".codex" / "sessions").glob("**/rollout-*.jsonl"))]
    for ia, fichiers in lots:
        for f in fichiers:
            try:
                m = f.stat().st_mtime
            except OSError:
                continue
            if depuis <= m <= limite:
                yield m, ia, f


def dossier(f):
    """Le dossier où la conversation a été tenue."""
    try:
        with open(f, encoding="utf-8", errors="replace") as h:
            for _, brut in zip(range(40), h):
                try:
                    d = json.loads(brut)
                except ValueError:
                    continue
                c = d.get("cwd") or (d.get("payload") or {}).get("cwd")
                if c:
                    return c
    except OSError:
        pass
    return ""


def dialogue(f):
    return extraire(f, maximum=None)


def carte(brain):
    """Les notes où ranger : chaque fiche de projet, plus les notes qu'une fiche cite ([[projets/…]]),
    avec leur titre. Le reste du projet est du détail : la fiche suffit pour choisir."""
    fiches = sorted((brain / "projets").glob("*/fiche.md"))
    citees = set()
    for fiche in fiches:
        try:
            citees |= set(re.findall(r"\[\[(projets/[^\]|#]+)", fiche.read_text(encoding="utf-8")))
        except OSError:
            pass
    notes = fiches + sorted(brain / f"{c}.md" for c in citees if not c.endswith("/fiche") and (brain / f"{c}.md").exists())
    lignes = []
    for note in sorted(set(notes)):
        rel = note.relative_to(brain).as_posix()
        try:
            texte = note.read_text(encoding="utf-8")
        except OSError:
            continue
        titre = next((l[2:].strip() for l in texte.splitlines() if l.startswith("# ")), note.stem)
        corps = re.sub(r"^---.*?---", "", texte, flags=re.S)
        intro = next((l.strip() for l in corps.splitlines() if l.strip() and not l.startswith(("#", "📂", "|", "-"))), "")
        lignes.append(f"- {rel} : {titre}. {intro[:160]}")
    lignes.append("- notes/a-faire.md : choses à faire qui n'appartiennent à aucun projet")
    lignes.append("- a-trier : rien ne colle, ou conversation sans rien d'utile à garder")
    return "\n".join(lignes)


def demander(consigne):
    corps = json.dumps({"model": MODELE, "prompt": consigne, "stream": False,
                        "options": {"num_ctx": 16384, "temperature": 0.2}}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", corps, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        rep = json.load(r).get("response", "")
    m = re.search(r"\{.*\}", rep, re.S)
    return json.loads(m.group(0)) if m else {"projet": "a-trier", "resume": rep[:500]}


def ollama_pret():
    try:
        with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=5) as r:
            noms = [m.get("name", "") for m in json.load(r).get("models", [])]
        return any(n == MODELE or n.split(":")[0] == MODELE for n in noms)
    except Exception:
        return False


def trier(depuis, maximum):
    brain = cerveau()
    if not brain:
        sys.exit("cerveau introuvable (variable CERVEAU, ou section ## Cerveau des règles globales)")
    local = ollama_pret()
    if not local:
        print(f"Ollama ou le modèle {MODELE} est absent : dialogues préparés pour un petit modèle, sans tri local.",
              file=sys.stderr)
    etat, faits = lire_etat(), 0
    plan = carte(brain)
    for m, ia, f in sorted(conversations(depuis), key=lambda x: x[0]):
        if maximum and faits >= maximum:
            break
        cle = str(f)
        texte = dialogue(f)
        if len(texte) < MINIMUM or texte.split(" : ", 1)[-1].startswith(INTERNES):
            continue
        ancien = etat.get(cle, {})
        if ancien.get("taille") == len(texte):
            continue  # déjà vue dans cet état
        dejala = ancien.get("lu", 0) if ancien.get("statut") == "range" else 0  # ne relire que la suite
        nouveau = texte[dejala:] if dejala < len(texte) else texte
        entree = {"id": f.stem[-8:], "ia": ia, "date": datetime.fromtimestamp(m).strftime("%Y-%m-%d %H:%M"),
                  "dossier": dossier(f), "taille": len(texte), "lu": len(texte), "statut": "trie"}
        if local:
            notes = []
            for i in range(0, len(nouveau), MORCEAU):
                morceau = nouveau[i:i + MORCEAU]
                print(f"{entree['date']} {ia} {entree['id']} : morceau {i // MORCEAU + 1}"
                      f"/{(len(nouveau) - 1) // MORCEAU + 1}", file=sys.stderr, flush=True)
                notes.append(demander(consigne_tri(plan, entree, morceau)))
            entree["notes"] = notes
        else:
            PREPARES.mkdir(parents=True, exist_ok=True)
            p = PREPARES / f"{entree['id']}.md"
            p.write_text(nouveau, encoding="utf-8")
            entree["dialogue"] = str(p)
        etat[cle] = entree
        ecrire_etat(etat)  # à chaque conversation : on peut interrompre et reprendre
        faits += 1
    print(f"{faits} conversation(s) triée(s). Suite : rattraper.py rapport", file=sys.stderr)


def consigne_tri(plan, entree, morceau):
    return f"""Tu ranges la mémoire d'un utilisateur. Voici les notes de son cerveau où l'on peut ranger quelque chose :

{plan}

Voici une conversation entre lui et une IA, tenue le {entree['date']} dans le dossier `{entree['dossier']}`.
Le dossier aide, mais range selon le SUJET : une conversation lancée dans un dossier peut parler d'un autre projet.
Réponds en français, en JSON seulement :
{{"projet": "<chemin exact d'une note de la liste ci-dessus, ou a-trier>",
  "confiance": "haute|moyenne|basse",
  "resume": "<3 à 5 phrases : de quoi ça parle, ce qui a été trouvé, fait ou décidé>",
  "a_retenir": ["<faits, décisions avec leur raison, états, prochaines étapes, sans rien inventer>"],
  "idees": ["<chaque idée, piste ou sujet proposé, même non retenu, avec un mot sur pourquoi>"]}}
Si la conversation n'a rien d'utile à garder (un essai, une question sans suite), mets "projet": "a-trier" et des listes vides.

Conversation :
{morceau}"""


def rapport():
    a_ranger = [e for e in lire_etat().values() if e.get("statut") == "trie"]
    print(json.dumps(sorted(a_ranger, key=lambda e: e["date"]), ensure_ascii=False, indent=1))


def marquer(ids):
    etat = lire_etat()
    n = 0
    for e in etat.values():
        if e.get("statut") == "trie" and (not ids or e["id"] in ids):
            e["statut"], n = "range", n + 1
            e.pop("notes", None)
            if e.get("dialogue"):
                Path(e.pop("dialogue")).unlink(missing_ok=True)
    ecrire_etat(etat)
    print(f"{n} conversation(s) marquée(s) comme rangée(s)")


def compter():
    etat = lire_etat()
    for statut in ("trie", "range"):
        print(f"{statut} : {sum(1 for e in etat.values() if e.get('statut') == statut)}")
    print(f"modèle local : {MODELE} ({'prêt' if ollama_pret() else 'absent'})")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = sys.argv[1:]
    action = args[0] if args else ""
    if action == "trier":
        d = args[args.index("--depuis") + 1] if "--depuis" in args else None
        depuis = datetime.strptime(d, "%Y-%m-%d").timestamp() if d else time.time() - 7 * 86400
        n = int(args[args.index("--max") + 1]) if "--max" in args else 0
        trier(depuis, n)
    elif action == "rapport":
        rapport()
    elif action == "marquer":
        marquer(set(args[1:]))
    elif action == "etat":
        compter()
    else:
        print(__doc__)
