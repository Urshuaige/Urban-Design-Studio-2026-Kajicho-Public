# Kajicho public Site source

This is the static source of [Kajicho Site Atlas](https://kajicho-site-atlas.specialgooood.chatgpt.site), published version 10. It contains the HTML, CSS, JavaScript, maps, data files and fonts used by that version. The primary building-age layer was updated on 13 November 2026; other site evidence retains its stated dates.

## Run locally

From the repository root, run:

```sh
python3 -m http.server 8000 --directory website
```

Open <http://localhost:8000> in a browser. Stop the server with Ctrl+C. No npm install or build step is required. `package.json` identifies ES modules; its `private` flag controls npm publication, not access to this GitHub repository.

## Read the code

| Files | Purpose |
| --- | --- |
| `index.html`, `info.js`, `info.css` | Atlas entry, data loading and page presentation |
| `history.html`, `history.js`, `history/` | Historical timeline, map periods and source records |
| `policy.html`, `conditions.html`, `info-data/` | Planning policy and existing-condition data |
| `field-visit.html`, `field-visit.js`, `field-graphs.js` | Fieldwork reading and relationship diagrams |
| `building-age.html`, `building-age.js`, `study-atlas/` | Building-age evidence and dated study layers |
| `site-navigation.js`, `page-outline.js` | Shared navigation and page outline |
| `fonts/manifest.json` | Font sources and licence links |

Start with the HTML entry, follow its JavaScript module, and inspect the JSON/CSV it reads. Keep source IDs, years and evidence status when making your own version. The [current GIS delivery](../04_Data/Ready/QGIS_Current_2026-11-04/README.md) includes the latest complete intersecting building footprints; the site snapshot includes the 13 November primary building-age update.

See [source notices](../NOTICE.md) and the data registers for attribution and reuse terms. Hosting credentials, deployment identity and Git history are not part of this source copy.
