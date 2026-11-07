#!/usr/bin/env python3
"""Rêve : à la fin d'une session, l'IA range dans le cerveau ce qui doit être retenu.

Branché sur le hook SessionEnd de Claude Code et de Codex. Il ne rêve que pour les projets
dont la fiche porte `reve: auto`, et seulement à partir du dialogue (pas des fichiers lus
ni des résultats de commandes), avec un petit modèle et un plafond par jour.

Usage :
  rever.py claude|codex          appelé par le hook (lit le JSON du hook sur stdin)
  rever.py installer             branche le hook dans Claude Code et Codex (sans doublon)
  rever.py desinstaller          le retire
  rever.py extraire <conversation.jsonl>   affiche le dialogue tel que le rêve le lirait

Réglages (variables d'environnement, facultatives) :
  CERVEAU                 chemin du cerveau (sinon lu dans les règles globales)
  CERVEAU_REVES_MAX       rêves maximum par jour, toutes IA confondues (défaut 5)
  CERVEAU_REVE_CLAUDE     modèle Claude du rêve (défaut haiku)
  CERVEAU_REVE_CODEX      modèle Codex du rêve (défaut : celui de Codex, effort bas)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
ETAT = HOME / ".agents" / "reves"
SCRIPT = Path(os.path.abspath(__file__))  # garde le chemin du lien, pas celui du dépôt
MARQUE = "rever.py"
DIALOGUE_MAX = 30_000   # caractères de dialogue lus au maximum (la fin de la conversation)
DIALOGUE_MIN = 1_500    # en dessous, la conversation est trop courte pour valoir un rêve
REVES_MAX = int(os.environ.get("CERVEAU_REVES_MAX", "5"))
BRUIT = re.compile(r"<(system-reminder|command-[a-z]+|local-command-[a-z]+|environment_context|user_instructions"
                   r"|skill|external_[a-z_]+|turn_aborted)>.*?</\1>|^Base directory for this skill:.*", re.S | re.M)


def cerveau():
    """Chemin du cerveau : variable CERVEAU, sinon la section ## Cerveau des règles globales."""
    if os.environ.get("CERVEAU") and (Path(os.environ["CERVEAU"]) / "AGENTS.md").exists():
        return Path(os.environ["CERVEAU"])
    for regles in (HOME / ".agents" / "AGENTS.md", HOME / ".claude" / "CLAUDE.md", HOME / ".codex" / "AGENTS.md"):
        try:
            texte = regles.read_text(encoding="utf-8")
        except OSError:
            continue
        m = re.search(r"Mon cerveau est `([^`]+)`", texte)
        if m:
            p = Path(os.path.expanduser(m.group(1)))
            if (p / "AGENTS.md").exists():
                return p
    return None


def norme(chemin):
    """Chemin comparable : /c/Users -> c:/users sous Windows, barres obliques, sans / final."""
    s = str(chemin).strip().replace("\\", "/")
    m = re.match(r"^/([a-zA-Z])/(.*)", s)
    if m and os.name == "nt":
        s = f"{m.group(1)}:/{m.group(2)}"
    s = os.path.expanduser(s).replace("\\", "/").rstrip("/")
    return s.lower() if os.name == "nt" else s


def projet_auto(brain, cwd):
    """Le projet dont la session vient, s'il a `reve: auto` dans sa fiche ; sinon None."""
    c = norme(cwd)
    for fiche in sorted((brain / "projets").glob("*/fiche.md")):
        try:
            tete = fiche.read_text(encoding="utf-8").split("---")[1]
        except (OSError, IndexError):
            continue
        champs = dict(re.findall(r"^([\w-]+):[ \t]*(.*?)[ \t]*(?:#.*)?$", tete, re.M))
        if champs.get("reve", "").lower() != "auto":
            continue
        lieux = [norme(fiche.parent)] + ([norme(champs["travail"])] if champs.get("travail") else [])
        if any(c == l or c.startswith(l + "/") for l in lieux):
            return fiche.parent.name
    return None


def extraire(transcript, maximum=DIALOGUE_MAX):
    """Le dialogue seul (utilisateur et IA), sans outils, fichiers lus ni réflexion interne."""
    lignes = []
    for brut in open(transcript, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(brut)
        except ValueError:
            continue
        if d.get("isSidechain"):
            continue
        role, morceaux = None, []
        if d.get("type") in ("user", "assistant") and isinstance(d.get("message"), dict):   # Claude Code
            role, c = d["type"], d["message"].get("content")
            if isinstance(c, str):
                morceaux = [c]
            elif isinstance(c, list):
                morceaux = [b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"]
        elif d.get("type") == "response_item":                                                # Codex
            p = d.get("payload") or {}
            if p.get("type") == "message" and p.get("role") in ("user", "assistant"):
                role = p["role"]
                morceaux = [b.get("text", "") for b in p.get("content") or [] if isinstance(b, dict)]
        texte = BRUIT.sub("", "\n".join(morceaux)).strip()
        if not role or not texte or texte.startswith(("# AGENTS.md", "<INSTRUCTIONS>")):
            continue
        lignes.append(f"{'Utilisateur' if role == 'user' else 'IA'} : {texte}")
    dialogue = "\n\n".join(lignes)
    return dialogue[-maximum:] if maximum else dialogue


def consigne(ia, dialogue, cwd, brain, projet):
    return (
        f"Mode rêve. Une session {ia} sur le projet « {projet} » vient de se terminer, dans `{cwd}`. "
        f"Son dialogue (sans les fichiers ni les commandes) est dans `{dialogue}`. "
        f"Le cerveau est `{brain}`. Lis seulement son AGENTS.md, la fiche `projets/{projet}/fiche.md` "
        "et les 20 dernières lignes de journal.md, puis applique le geste « sauver » du skill cerveau "
        "à cette fiche : ne garde que ce qui servira à une prochaine session (état, décisions avec leur "
        "raison et les options écartées, prochaines étapes). Si la fiche renvoie à une mémoire propre au "
        "dossier de travail, n'y recopie pas le détail : seulement l'état général et les décisions. "
        "Si la session a déjà sauvé (ligne de journal récente), complète seulement ce qui manque ; "
        "si rien de durable n'a été dit, ne change rien. Ne touche à aucun autre fichier du cerveau "
        f"sauf journal.md, où tu signes « {ia} (rêve) ». Ne lance aucune commande git."
    )


def trouver(nom):
    """Chemin de l'IA. Une app lancée depuis le Dock (macOS) ou un hook a souvent un PATH réduit :
    on regarde aussi les endroits d'installation habituels."""
    exe = shutil.which(nom)
    if exe:
        return exe
    lieux = [HOME / ".local" / "bin", HOME / ".claude" / "local", HOME / ".npm-global" / "bin",
             HOME / ".bun" / "bin", Path("/opt/homebrew/bin"), Path("/usr/local/bin"), Path("/usr/bin")]
    lieux += sorted((HOME / ".nvm" / "versions" / "node").glob("*/bin"), reverse=True)
    if os.name == "nt":
        lieux += [Path(os.environ.get("APPDATA", "")) / "npm"]
    return shutil.which(nom, path=os.pathsep.join(str(l) for l in lieux))


def commande(ia, brain):
    """Commande sans interface, petit modèle ; la consigne arrive par l'entrée standard."""
    if ia == "claude":
        exe = trouver("claude")
        return exe and [exe, "-p", "--model", os.environ.get("CERVEAU_REVE_CLAUDE", "haiku"),
                        "--permission-mode", "acceptEdits",
                        "--allowedTools", "Read", "Edit", "Write", "--add-dir", str(brain)]
    exe = trouver("codex")
    if not exe:
        return None
    cmd = [exe, "exec", "-s", "workspace-write", "--skip-git-repo-check", "-C", str(brain),
           "-c", 'model_reasoning_effort="low"']
    if os.environ.get("CERVEAU_REVE_CODEX"):
        cmd += ["-m", os.environ["CERVEAU_REVE_CODEX"]]
    return cmd + ["-"]


def compteur_du_jour():
    f = ETAT / f"compteur-{time.strftime('%Y-%m-%d')}"
    try:
        n = int(f.read_text())
    except (OSError, ValueError):
        n = 0
    return f, n


def note(texte):
    with open(ETAT / "reves.log", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M')} {texte}\n")


def rever(ia):
    if os.environ.get("CERVEAU_REVE"):
        return
    try:
        evt = json.load(sys.stdin)
    except (ValueError, OSError):
        return
    transcript, cwd = evt.get("transcript_path"), evt.get("cwd") or ""
    brain = cerveau()
    if not brain or not transcript or not Path(transcript).exists():
        return
    projet = projet_auto(brain, cwd)
    if not projet:
        return  # projet sans rêve automatique : on sauve à la main
    ETAT.mkdir(parents=True, exist_ok=True)
    session = re.sub(r"[^\w.-]", "_", str(evt.get("session_id") or Path(transcript).stem))
    dialogue = extraire(transcript)
    if len(dialogue) < DIALOGUE_MIN:
        return
    deja = ETAT / f"{session}.taille"
    if deja.exists() and deja.read_text().strip() == str(len(dialogue)):
        return  # déjà rêvé de cette conversation dans cet état
    compteur, n = compteur_du_jour()
    if n >= REVES_MAX:
        note(f"{ia} {projet} : plafond de {REVES_MAX} rêves atteint aujourd'hui, pas de rêve")
        return
    cmd = commande(ia, brain)
    if not cmd:
        return
    compteur.write_text(str(n + 1))
    deja.write_text(str(len(dialogue)))
    fichier = ETAT / f"{session}.dialogue.md"
    fichier.write_text(dialogue, encoding="utf-8")
    tache = ETAT / f"{session}.tache.json"
    tache.write_text(json.dumps({
        "cmd": cmd, "cwd": str(brain), "entree": consigne(ia, fichier, cwd, brain, projet),
        "titre": f"{time.strftime('%Y-%m-%d %H:%M')} {ia} {projet} ({len(dialogue)} caractères de dialogue)",
    }, ensure_ascii=False), encoding="utf-8")
    # On rend la main tout de suite : un relais Python détaché fait le rêve.
    options = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   env=dict(os.environ, CERVEAU_REVE="1"))
    if os.name == "nt":
        options["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        options["start_new_session"] = True
    subprocess.Popen([sys.executable, str(SCRIPT), "_executer", str(tache)], **options)


def executer(tache):
    t = json.loads(Path(tache).read_text(encoding="utf-8"))
    with open(ETAT / "reves.log", "a", encoding="utf-8") as journal:
        journal.write(f"\n=== {t['titre']}\n")
        journal.flush()
        r = subprocess.run(t["cmd"], cwd=t["cwd"], input=t["entree"], text=True, encoding="utf-8",
                           errors="replace", stdout=journal, stderr=subprocess.STDOUT,
                           env=dict(os.environ, CERVEAU_REVE="1"), timeout=1800)
        journal.write(f"--- fin, code {r.returncode}\n")
        # La sauvegarde git est faite ici, pas par l'IA (le bac à sable de Codex protège .git).
        git = lambda *a: subprocess.run(["git", *a], cwd=t["cwd"], capture_output=True, text=True,
                                        encoding="utf-8", errors="replace")
        if git("status", "--porcelain").stdout.strip():
            git("add", "-A")
            c = git("commit", "-m", f"rêve : {t['titre']}")
            journal.write(("sauvegardé\n" if c.returncode == 0 else f"sauvegarde impossible : {c.stderr}\n"))
        else:
            journal.write("rien de nouveau à retenir\n")
    Path(tache).unlink(missing_ok=True)
    Path(str(tache).replace(".tache.json", ".dialogue.md")).unlink(missing_ok=True)


# --- installation des hooks -------------------------------------------------

def _lire(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _ecrire(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        shutil.copy2(p, p.with_name(p.name + ".avant-reve"))
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _retirer(groupes):
    return [g for g in groupes if not any(MARQUE in json.dumps(h) for h in g.get("hooks", []))]


def installer(retirer=False):
    py = "py -3" if os.name == "nt" and shutil.which("py") else ("python3" if shutil.which("python3") else "python")
    s = str(SCRIPT).replace("\\", "/")
    faits = []
    cibles = [("claude", HOME / ".claude" / "settings.json"), ("codex", HOME / ".codex" / "hooks.json")]
    for ia, fichier in cibles:
        if not fichier.parent.exists():
            continue
        data = _lire(fichier)
        hooks = data.setdefault("hooks", {})
        groupes = _retirer(hooks.get("SessionEnd", []))
        if not retirer:
            h = {"type": "command", "command": f'{py} "{s}" {ia}', "timeout": 30}
            if ia == "codex" and os.name == "nt":
                h["commandWindows"] = h["command"]
            groupes.append({"hooks": [h]})
        if groupes:
            hooks["SessionEnd"] = groupes
        else:
            hooks.pop("SessionEnd", None)
        _ecrire(fichier, data)
        faits.append(f"{'retiré de' if retirer else 'branché dans'} {ia} ({fichier})")
    print("\n".join(faits) or "ni Claude Code ni Codex trouvés")
    if not retirer and any(ia == "codex" for ia, f in cibles if f.parent.exists()):
        print("Codex : ouvre Codex et approuve le hook avec /hooks (une seule fois).")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action in ("claude", "codex"):
        try:
            rever(action)
        except Exception as e:  # un rêve raté ne doit jamais gêner la fermeture de l'IA
            ETAT.mkdir(parents=True, exist_ok=True)
            with open(ETAT / "reves.log", "a", encoding="utf-8") as f:
                f.write(f"erreur : {e!r}\n")
    elif action == "_executer" and len(sys.argv) > 2:
        try:
            executer(sys.argv[2])
        except Exception as e:
            with open(ETAT / "reves.log", "a", encoding="utf-8") as f:
                f.write(f"erreur : {e!r}\n")
    elif action == "extraire" and len(sys.argv) > 2:
        print(extraire(sys.argv[2]))
    elif action == "installer":
        installer()
    elif action == "desinstaller":
        installer(retirer=True)
    else:
        print(__doc__)
