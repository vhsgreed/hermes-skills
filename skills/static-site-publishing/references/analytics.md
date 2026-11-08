# Site analytics (self-hosted umami, Cloudflare)

Sites measure traffic with a self-hosted umami (v3, postgres) on a home server.
The public collector is `https://analytics.<your-domain>` (`/script.js`,
`/api/send`, `/api/heartbeat` returns `{"ok":true}`); the container only binds
127.0.0.1:3000 on the server, so all admin work goes over ssh.

## Add a site

1. Check it is not already there:
   `docker exec umami-umami-db-1 psql -U umami -d umami -At -c "select website_id,name,domain from website;"`
2. Register it under the existing umami user by copying `user_id`/`created_by`
   from an existing row (no admin password needed, no UI login):
   `insert into website (website_id,name,domain,user_id,created_by,created_at) select gen_random_uuid(), 'Name', 'example.org', user_id, created_by, now() from website where domain='<an-existing-site>' and not exists (select 1 from website where domain='example.org');`
   Use `$$...$$` dollar quoting inside the ssh/docker/psql nesting instead of
   fighting single quotes.
3. Put the tag in the shared page template (not per page), restricted to the
   real hostnames so deploy previews (`*.pages.dev`) never count:
   `<script defer src="https://analytics.<your-domain>/script.js" data-website-id="ID" data-domains="example.org,www.example.org"></script>`
4. Rebuild, `grep -c` the website id in every built HTML file, deploy, then curl
   each live URL and grep again.
5. Verify ingestion with a REAL browser load, not just the tag:
   `google-chrome --headless=new --no-sandbox --user-data-dir=<scratch> --user-agent="<normal Chrome UA>" --virtual-time-budget=8000 --dump-dom "https://example.org/page?ref=setupcheck"`,
   then select from `website_event` for the new website id.
6. Delete every test row (both `website_event` and its `session` row, matched by
   the `?ref=setupcheck` query or the returned sessionId) so counts start at zero.

- Pitfall: umami answers `{"beep":"boop"}` with HTTP 200 when it classifies the
  request as a bot (any odd user-agent, e.g. one containing "check" or a bare curl
  UA) and stores nothing. A 200 is not proof of ingestion; read the table.
- Traffic before the tag went live is gone from umami; say so in the ledger.

## Cloudflare as a traffic source

- Zone traffic (requests, page views, uniques, referer host, path) is readable
  only through the GraphQL Analytics API (`https://api.cloudflare.com/client/v4/graphql`,
  `httpRequests1dGroups` / `httpRequestsAdaptiveGroups` on the zone tag); the old
  zone analytics REST endpoint is sunset. The token needs **Zone > Analytics > Read**;
  a deploy-only Pages token gets an `authz` error. Adding the permission to the
  existing token in the dashboard keeps the token value unchanged.
- Cloudflare Web Analytics (RUM) only has data if it was enabled for the site.
- Cloudflare counts are raw edge requests including bots; treat them as an upper
  bound for a dated window (e.g. around a post), and use umami for referrers.
