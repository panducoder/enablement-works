#!/bin/zsh
# One-time: create the public GitHub repo, push, and turn on GitHub Pages for enablement.works.
set -e
cd "$(dirname "$0")/.."
gh auth switch --user panducoder >/dev/null 2>&1 || true
gh repo create panducoder/enablement-works --public --description "Enablement Works website (enablement.works)" --source . --push
gh api -X POST repos/panducoder/enablement-works/pages -f "source[branch]=main" -f "source[path]=/docs" >/dev/null
gh api -X PUT repos/panducoder/enablement-works/pages -f cname=enablement.works >/dev/null
echo "Live soon at https://panducoder.github.io/enablement-works/ and, once DNS resolves, https://enablement.works"
