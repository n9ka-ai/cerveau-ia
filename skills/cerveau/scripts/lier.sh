#!/usr/bin/env bash
# Relie un dossier de travail à la fiche de son projet dans le cerveau.
# Usage : lier.sh <dossier de travail> <dossier du projet dans le cerveau>
# Écrit le chemin dans le champ `travail` de la fiche et, sous le titre, un bouton
# « 📂 Ouvrir le dossier de travail » qui l'ouvre dans l'explorateur (depuis Obsidian).
# Aucun lien n'est créé dans le cerveau : le dossier de travail reste seul à son endroit.
# S'il reste un ancien lien `travail` (versions précédentes), il est retiré sans toucher au dossier.
set -eu
cible="${1:?usage: lier.sh <dossier de travail> <dossier du projet>}"
projet="${2:?usage: lier.sh <dossier de travail> <dossier du projet>}"
fiche="$projet/fiche.md"

[ -d "$cible" ] || { echo "dossier de travail introuvable : $cible"; exit 1; }
[ -f "$fiche" ] || { echo "fiche introuvable : $fiche (crée-la d'abord)"; exit 2; }

windows=0
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) windows=1 ;; esac
if [ "$windows" = 1 ]; then chemin="$(cygpath -m "$(cd "$cible" && pwd -P)")"   # C:/Users/...
else chemin="$(cd "$cible" && pwd -P)"; fi                                         # /Users/...

# Ancien lien `travail` : on retire seulement la porte, jamais ce qu'il y a derrière.
ancien="$projet/travail"
if [ -L "$ancien" ]; then   # Git Bash voit aussi les jonctions Windows comme des liens
  if [ "$windows" = 1 ]; then MSYS_NO_PATHCONV=1 cmd /c rmdir "$(cygpath -w "$ancien")"; else rm "$ancien"; fi
  [ -d "$cible" ] || { echo "ERREUR : le dossier de travail a disparu"; exit 9; }
  echo "ancien lien retiré : $ancien (le dossier de travail est intact)"
elif [ -e "$ancien" ]; then
  echo "$ancien est un vrai dossier, pas un lien : rien changé, à regarder"; exit 3
fi

# Adresse cliquable : espaces et caractères spéciaux encodés.
url="file://$(case "$chemin" in /*) ;; *) printf /;; esac)$(printf '%s' "$chemin" | sed -e 's/%/%25/g' -e 's/ /%20/g' -e 's/#/%23/g' -e 's/(/%28/g' -e 's/)/%29/g')"
bouton="📂 [Ouvrir le dossier de travail]($url)"

awk -v chemin="$chemin" -v bouton="$bouton" '
  NR == 1 && $0 == "---" { entete = 1; print; next }
  entete && $0 == "---" { if (!vu) print "travail: " chemin; entete = 0; print; next }
  entete && /^travail:/ { print "travail: " chemin; vu = 1; next }
  /^📂 \[Ouvrir le dossier de travail\]/ { saute = 1; next }   # ancien bouton, et sa ligne vide
  saute && $0 == "" { saute = 0; next }
  { saute = 0 }
  !titre && /^# / { print; print ""; print bouton; titre = 1; next }
  { print }
' "$fiche" > "$fiche.tmp" && mv "$fiche.tmp" "$fiche"

grep -qxF "travail: $chemin" "$fiche" && grep -qF "$bouton" "$fiche" || { echo "la fiche n'a pas été mise à jour"; exit 4; }
echo "relié : $fiche → $chemin"
