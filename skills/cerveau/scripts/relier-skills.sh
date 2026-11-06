#!/usr/bin/env bash
# Relie chaque skill du cerveau (<cerveau>/skills/<nom>/SKILL.md) dans les dossiers de skills des IA de cette machine.
# Usage : relier-skills.sh <cerveau> [dossier de skills...]
# Par défaut : ~/.agents/skills (Codex et autres) et ~/.claude/skills (Claude Code) s'il existe.
# Ne remplace jamais un vrai dossier : il le signale.
set -u
cerveau="${1:?usage: relier-skills.sh <cerveau> [dossier de skills...]}"
shift
[ -d "$cerveau/skills" ] || { echo "pas de skills dans le cerveau ($cerveau/skills)"; exit 0; }
if [ $# -eq 0 ]; then
  set -- "$HOME/.agents/skills"
  [ -d "$HOME/.claude" ] && set -- "$@" "$HOME/.claude/skills"
fi

reel() { (cd "$1" 2>/dev/null && pwd -P); }
lier() { # <cible> <lien>
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) MSYS_NO_PATHCONV=1 cmd /c mklink /J "$(cygpath -w "$2")" "$(cygpath -w "$1")" >/dev/null ;;
    *) ln -s "$1" "$2" ;;
  esac
}

probleme=0
vus=""
for dest in "$@"; do
  mkdir -p "$dest"
  dest_reel="$(reel "$dest")"
  # Deux dossiers qui sont en fait le même (un lien de l'un vers l'autre) : une seule fois.
  case " $vus " in *" $dest_reel "*) continue ;; esac
  vus="$vus $dest_reel"
  for s in "$cerveau"/skills/*/; do
    [ -f "$s/SKILL.md" ] || continue
    nom="$(basename "$s")"; cible="$(reel "$s")"; lien="$dest/$nom"
    if [ -e "$lien" ] || [ -L "$lien" ]; then
      if [ "$(reel "$lien")" = "$cible" ]; then echo "ok        $lien"
      else echo "CONFLIT   $lien existe déjà et ne vient pas du cerveau : rien changé"; probleme=1; fi
    else
      lier "$cible" "$lien" && echo "relié     $lien" || { echo "ÉCHEC     $lien"; probleme=1; }
    fi
  done
  # Liens morts qui pointaient vers un skill retiré du cerveau.
  for l in "$dest"/*; do
    [ -e "$l" ] || [ ! -L "$l" ] && continue
    echo "MORT      $l (lien vers un skill disparu)"; probleme=1
  done
done
exit $probleme
