#!/usr/bin/env bash
# Synchronise un cerveau avec son dépôt git : sauvegarde locale, récupération, envoi.
# Usage : synchro.sh <dossier du cerveau> [nom de l'agent]
# Sorties : 0 « synchro ok », 2 conflit (rien n'est envoyé, rien n'est perdu), 3 envoi impossible.
set -u
dir="${1:?usage: synchro.sh <dossier du cerveau> [nom]}"
nom="${2:-agent}"
cd "$dir" || { echo "dossier introuvable : $dir"; exit 1; }

# Une seule synchro à la fois (si flock existe).
if command -v flock >/dev/null 2>&1; then
  exec 9>"${TMPDIR:-/tmp}/cerveau-synchro.lock"
  flock -n 9 || { echo "synchro déjà en cours"; exit 0; }
fi

if [ -n "$(git status --porcelain)" ]; then
  git add -A && git commit -qm "$nom : sauvegarde $(date '+%Y-%m-%d %H:%M')"
fi

if ! git pull --rebase -q; then
  git rebase --abort 2>/dev/null
  echo "$(date '+%Y-%m-%d %H:%M') conflit avec le dépôt : rien envoyé, les changements locaux restent sauvegardés ici. À régler par l'utilisateur."
  exit 2
fi

git push -q || { echo "$(date '+%Y-%m-%d %H:%M') envoi impossible (réseau ou droits)"; exit 3; }
echo "synchro ok"
