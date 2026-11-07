#!/usr/bin/env python3
"""Rangement de nuit du cerveau, sans IA : seulement ce qui est sûr et mécanique.

- index.md : ajoute la ligne d'une fiche qui n'y est pas, retire celle dont la fiche n'existe plus ;
- journal.md : déplace les lignes des mois clos dans _archive/journal-AAAA-MM.md ;
- notes/a-ranger.md : la liste de ce qu'une IA ou l'utilisateur devrait regarder (fiche « actif »
  sans mise à jour depuis 30 jours, fiche sans état, dossier de travail introuvable sur cette machine).
Il ne supprime jamais une note et ne fait aucune sauvegarde git : la synchro s'en charge.

Usage : ranger.py <dossier du cerveau> [--essai]   (--essai : montre sans rien écrire)
"""
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

RETARD = 30  # jours sans mise à jour avant de signaler une fiche « actif »
LIGNE_JOURNAL = re.compile(r"^- (\d{4})-(\d{2})-\d{2} ")


def champs(texte):
    try:
        tete = texte.split("---")[1]
    except IndexError:
        return {}
    return dict(re.findall(r"^([\w-]+):[ \t]*(.*?)[ \t]*(?:#.*)?$", tete, re.M))


def fiches(brain):
    for f in sorted((brain / "projets").glob("*/fiche.md")):
        texte = f.read_text(encoding="utf-8")
        titre = next((l[2:].strip() for l in texte.splitlines() if l.startswith("# ")), f.parent.name)
        yield f.parent.name, titre, champs(texte)


def ranger_index(brain, essai):
    p = brain / "index.md"
    texte = p.read_text(encoding="utf-8")
    lignes = texte.split("\n")
    existants = {nom for nom, _, _ in fiches(brain)}
    cites, gardees, retirees = set(), [], []
    for l in lignes:
        m = re.search(r"\[\[projets/([^/\]]+)/fiche\]\]", l)
        if m and l.startswith("|"):
            if m.group(1) not in existants:
                retirees.append(m.group(1))
                continue
            cites.add(m.group(1))
        gardees.append(l)
    ajouts = []
    for nom, titre, c in fiches(brain):
        if nom not in cites:
            travail = f"`{c['travail']}`" if c.get("travail") else "—"
            ajouts.append(f"| {titre} | [[projets/{nom}/fiche]] | {travail} | {c.get('etat') or 'à préciser'} |")
    if ajouts:
        fin = max((i for i, l in enumerate(gardees) if l.startswith("|")), default=None)
        if fin is None:
            gardees += ["", "| Projet | Fiche | Dossier de travail | État |", "|---|---|---|---|"] + ajouts
        else:
            gardees[fin + 1:fin + 1] = ajouts
    if (ajouts or retirees) and not essai:
        p.write_text("\n".join(gardees), encoding="utf-8", newline="\n")
    return [f"index : ajouté {a.split('|')[2].strip()}" for a in ajouts] + [f"index : retiré {r} (fiche introuvable)" for r in retirees]


def ranger_journal(brain, essai):
    p = brain / "journal.md"
    if not p.exists():
        return []
    mois = date.today().strftime("%Y-%m")
    garder, partir = [], {}
    for l in p.read_text(encoding="utf-8").split("\n"):
        m = LIGNE_JOURNAL.match(l)
        if m and f"{m.group(1)}-{m.group(2)}" < mois:
            partir.setdefault(f"{m.group(1)}-{m.group(2)}", []).append(l)
        else:
            garder.append(l)
    if not partir:
        return []
    if not essai:
        (brain / "_archive").mkdir(exist_ok=True)
        for m, ls in partir.items():
            a = brain / "_archive" / f"journal-{m}.md"
            avant = a.read_text(encoding="utf-8").rstrip("\n").split("\n") if a.exists() else [f"# Journal {m}", ""]
            nouvelles = [l for l in ls if l not in avant]
            a.write_text("\n".join(avant + nouvelles) + "\n", encoding="utf-8", newline="\n")
        p.write_text("\n".join(garder), encoding="utf-8", newline="\n")
    return [f"journal : {len(ls)} ligne(s) de {m} archivées" for m, ls in sorted(partir.items())]


def a_regarder(brain):
    points = []
    today = date.today()
    for nom, titre, c in fiches(brain):
        etat = (c.get("etat") or "").lower()
        if not etat:
            points.append(f"- [[projets/{nom}/fiche]] : pas d'état (actif, en pause ou fini).")
        maj = c.get("mis-a-jour", "")
        try:
            jours = (today - datetime.strptime(maj, "%Y-%m-%d").date()).days
        except ValueError:
            jours = None
        if etat == "actif" and jours is not None and jours > RETARD:
            points.append(f"- [[projets/{nom}/fiche]] : « actif » mais pas mise à jour depuis {jours} jours. Toujours actif ?")
        t = c.get("travail", "")
        if t and Path(t).anchor and Path(Path(t).anchor).exists() and not Path(os.path.expanduser(t)).exists():
            points.append(f"- [[projets/{nom}/fiche]] : le dossier de travail `{t}` est introuvable.")
    for d in sorted((brain / "projets").iterdir()):
        if d.is_dir() and not any(d.iterdir()):
            points.append(f"- `projets/{d.name}/` : dossier vide.")
    return points


def ecrire_a_ranger(brain, points, essai):
    p = brain / "notes" / "a-ranger.md"
    texte = ("# À ranger\n\nListe tenue par le rangement de nuit (`ranger.py`), refaite à chaque passage. "
             "Rien n'est supprimé : à regarder avec une IA (« range le cerveau »).\n\n"
             + ("\n".join(points) if points else "Rien à signaler.") + "\n")
    if (p.read_text(encoding="utf-8") if p.exists() else None) == texte or (not points and not p.exists()):
        return []
    if not essai:
        p.parent.mkdir(exist_ok=True)
        p.write_text(texte, encoding="utf-8", newline="\n")
    return [f"a-ranger : {len(points)} point(s) à regarder"]


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args or not (Path(args[0]) / "AGENTS.md").exists():
        sys.exit(__doc__)
    brain, essai = Path(args[0]), "--essai" in sys.argv
    fait = ranger_index(brain, essai) + ranger_journal(brain, essai) + ecrire_a_ranger(brain, a_regarder(brain), essai)
    print(f"{datetime.now():%Y-%m-%d %H:%M} " + ("; ".join(fait) if fait else "rien à ranger"))
