#!/usr/bin/env python3
"""Rêve : à la fin d'une session, l'IA range dans le cerveau ce qui doit être retenu.

Branché sur le hook SessionEnd de Claude Code et de Codex. Il lit le JSON du hook sur
l'entrée standard (transcript_path, cwd, session_id), puis lance en tâche de fond la
même IA, sans interface, avec le geste « sauver » du skill cerveau.

Usage :
  rever.py claude|codex          appelé par le hook (lit le JSON sur stdin)
  rever.py installer             branche le hook dans Claude Code et Codex (sans doublon)
  rever.py desinstaller          le retire

Garde-fous : rien si la variable CERVEAU_REVE est posée (la session de rêve elle-même),
rien si aucun cerveau n'est déclaré, rien pour une conversation courte, une seule fois
par état de conversation.
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
TAILLE_MIN = 15_000  # octets de conversation en dessous desquels on ne rêve pas
SCRIPT = Path(os.path.abspath(__file__))  # garde le chemin du lien, pas celui du dépôt
MARQUE = "rever.py"


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


def consigne(ia, transcript, cwd, brain):
    return (
        f"Mode rêve. Une session {ia} vient de se terminer. La conversation complète est dans "
        f"`{transcript}` (une ligne JSON par message), elle s'est déroulée dans `{cwd}`. "
        f"Le cerveau de l'utilisateur est `{brain}` : lis son AGENTS.md et son index.md, puis applique "
        "le geste « sauver » du skill cerveau à partir de cette conversation. Ne garde que ce qui servira "
        "à une prochaine session : état du projet, décisions avec leur raison et les options écartées, "
        "prochaines étapes, idées. Si la session a déjà sauvé elle-même (regarde la fin de journal.md), "
        "complète seulement ce qui manque. Si la conversation n'a rien apporté de durable, ne change rien. "
        "Le dossier où s'est tenue la conversation n'est pas forcément un dossier de travail : ne remplis "
        "le champ `travail` d'une fiche que si la conversation le dit clairement. "
        f"Ne modifie aucun fichier hors du cerveau. Signe ta ligne de journal « {ia} (rêve) ». "
        "Ne lance aucune commande git : la sauvegarde est faite après toi."
    )


def commande(ia, brain):
    """Commande sans interface ; la consigne arrive par l'entrée standard (aucun souci de guillemets)."""
    if ia == "claude":
        exe = shutil.which("claude")
        return exe and [exe, "-p", "--permission-mode", "acceptEdits",
                        "--allowedTools", "Read", "Glob", "Grep", "Edit", "Write", "Bash(git:*)", "Skill",
                        "--add-dir", str(brain)]
    exe = shutil.which("codex")
    return exe and [exe, "exec", "-s", "workspace-write", "--skip-git-repo-check", "-C", str(brain), "-"]


def rever(ia):
    if os.environ.get("CERVEAU_REVE"):
        return
    try:
        evt = json.load(sys.stdin)
    except (ValueError, OSError):
        return
    transcript = evt.get("transcript_path")
    if not transcript or not Path(transcript).exists():
        return
    taille = Path(transcript).stat().st_size
    if taille < TAILLE_MIN:
        return
    brain = cerveau()
    if not brain:
        return
    ETAT.mkdir(parents=True, exist_ok=True)
    session = re.sub(r"[^\w.-]", "_", str(evt.get("session_id") or Path(transcript).stem))
    deja = ETAT / f"{session}.taille"
    if deja.exists() and deja.read_text().strip() == str(taille):
        return  # déjà rêvé de cette conversation dans cet état
    cmd = commande(ia, brain)
    if not cmd:
        return
    deja.write_text(str(taille))
    tache = ETAT / f"{session}.tache.json"
    tache.write_text(json.dumps({
        "cmd": cmd, "cwd": str(brain), "entree": consigne(ia, transcript, evt.get("cwd") or "?", brain),
        "titre": f"{time.strftime('%Y-%m-%d %H:%M')} {ia} {session} ({taille} octets)",
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
    elif action == "installer":
        installer()
    elif action == "desinstaller":
        installer(retirer=True)
    else:
        print(__doc__)
