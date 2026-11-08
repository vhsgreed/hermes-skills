#!/usr/bin/env bash
# Usage: check-names.sh name1 name2 ...
# Reports PyPI (incl. - and _ variants), GitHub repo collisions, and whether
# github.com/<name> (user/org) is free, for candidate project/package names.
# Uses `gh api` when available: unauthenticated GitHub search rate-limits
# after ~10 queries and silently returns "?" instead of a count.
gh_search() {
  if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    gh api "search/repositories?q=$1+in:name&per_page=3" \
      --jq '"\(.total_count) \([.items[].full_name])"' 2>/dev/null || echo "?"
  else
    curl -s "https://api.github.com/search/repositories?q=$1+in:name&per_page=3" \
      | python3 -c "import json,sys
d=json.load(sys.stdin)
print(d.get('total_count','?'), [i['full_name'] for i in d.get('items',[])])" 2>/dev/null
  fi
}
for name in "$@"; do
  pypi=""
  for v in "$name" "${name//_/-}" "${name//-/_}"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/pypi/$v/json")
    pypi="$pypi $v:$code"
  done
  ghuser=$(curl -s -o /dev/null -w "%{http_code}" "https://github.com/$name")
  echo "$name | pypi:$pypi (404=free) | gh repos: $(gh_search "$name") | github.com/$name:$ghuser (404=free)"
  sleep 1
done
