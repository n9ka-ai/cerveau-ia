#!/usr/bin/env bash
# Relie un dossier de travail à la fiche de son projet dans le cerveau.
# Usage : lier.sh <dossier de travail> <dossier du projet dans le cerveau>
# Crée <dossier du projet>/travail (jonction sous Windows, lien symbolique ailleurs),
# l'exclut de git, puis vérifie qu'il mène bien au dossier de travail.
set -eu
cible="${1:?usage: lier.sh <dossier de travail> <dossier du projet>}"
projet="${2:?usage: lier.sh <dossier de travail> <dossier du projet>}"

[ -d "$cible" ] || { echo "dossier de travail introuvable : $cible"; exit 1; }
cible_abs="$(cd "$cible" && pwd -P)"
mkdir -p "$projet"
lien="$projet/travail"

if [ -e "$lien" ] || [ -L "$lien" ]; then
  if [ -d "$lien" ] && [ "$(cd "$lien" && pwd -P)" = "$cible_abs" ]; then
    echo "déjà relié : $lien → $cible_abs"
  else
    echo "$lien existe déjà et ne mène pas à $cible_abs : rien changé"; exit 2
  fi
else
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      # Une jonction ne demande ni droits admin ni mode développeur.
      MSYS_NO_PATHCONV=1 cmd /c mklink /J "$(cygpath -w "$lien")" "$(cygpath -w "$cible_abs")" >/dev/null ;;
    *)
      ln -s "$cible_abs" "$lien" ;;
  esac
  echo "relié : $lien → $cible_abs"
fi

# Exclure les liens de travail de git, une seule fois.
if racine="$(git -C "$projet" rev-parse --show-toplevel 2>/dev/null)"; then
  gi="$racine/.gitignore"
  grep -qxF 'projets/*/travail' "$gi" 2>/dev/null || printf 'projets/*/travail\n' >> "$gi"
  git -C "$racine" check-ignore -q "$lien" || { echo "attention : le lien n'est pas exclu de git ($lien)"; exit 3; }
fi

[ "$(cd "$lien" && pwd -P)" = "$cible_abs" ] || { echo "le lien ne mène pas au bon dossier"; exit 4; }
echo "ok"
