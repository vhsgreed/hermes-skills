# Putting a live Pages site on hold

Use when Karl wants a site paused: every URL shows a short holding page, and the source stays restorable.

## Procedure

1. **Don't touch the existing build.** In the site repo, add a `holding/` folder with three files:
   - `index.html`: plain HTML, inline CSS, `<meta name="robots" content="noindex">`, one heading and one sentence. Dark mode via `prefers-color-scheme`.
   - `_redirects`: send any old section with cached pages to `/` explicitly, then add a catch-all.
     ```
     /blog  /  302
     /blog/*  /  302
     /*  /index.html  200
     ```
   - `robots.txt`: `User-agent: *` / `Disallow: /`
2. **Repoint the Pages project. No build step needed.** Read the account token from `~/.secrets/CLOUDFLARE_ACCOUNT_TOKEN` and get the account id from `GET /client/v4/accounts`. Then:
   ```
   PATCH /client/v4/accounts/$A/pages/projects/<project>
   {"build_config":{"build_command":"","destination_dir":"holding","root_dir":""}}
   ```
   The project name is `name` in `GET .../pages/projects`. It can differ from the pages.dev subdomain (`site` vs `site-rvi.pages.dev`).
3. **Commit and push.** A Git-connected project deploys on push. Confirm with `GET .../pages/projects/<p>/deployments?per_page=2`: the newest entry should be your commit hash with `deploy success`.
4. **Verify every hostname and path class.** Curl the apex, www, pages.dev, a deep old path, a nonexistent path and the RSS feed. Grep each response for the holding `<title>`.
   - Pitfall: pages with a long `s-maxage` from the old build can keep being served after a zone `purge_everything`, because the Pages asset layer still holds them. To spot this, append a query string: if `?x=1` shows the holding page but the bare URL doesn't, the bare URL is stale cache. An explicit `_redirects` rule for that path fixes it; repeated purges don't.
5. **Make the repo private if asked.** Use `gh api -X PATCH repos/<owner>/<repo> -f visibility=private -q .visibility` and check that it prints `private`. Push-triggered Pages deploys keep working on a private repo.
6. **Bringing back one page while on hold.** Run the old build locally (`npm ci && npm run build`). Copy `dist/<path>/index.html` into `holding/<path>/`, and also every `/_astro/*` asset it references plus the favicon. Then add rules to `_redirects` above the catch-all: the no-slash path 301s to the slash path, the slash path 200s to `.../index.html`, and `/_astro/*  /_astro/:splat  200`. Without these the `/*` catch-all hides the page. Push, then curl apex, www, the no-slash path, a CSS asset, and a sibling page, which should still show the holding page.
7. **Write down how to undo it.** Restoring the original `build_command`/`destination_dir` (e.g. `npm run build` / `dist`) and pushing brings the site back.
