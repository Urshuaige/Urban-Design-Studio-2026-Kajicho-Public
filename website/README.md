# Kajicho public Site source

This folder contains the 619 public client files from [Kajicho Site Atlas](https://kajicho-site-atlas.specialgooood.chatgpt.site), published version **52** on 24 November 2026. The public files are from deployed source commit `f0d50120d846af3ba067520f370d1cb9a383e37d`. The history report uses the repository’s relative link to Site Data. [Public copy record](../PUBLIC_COPY.json)

| Start here | Public page | Source |
| --- | --- | --- |
| Atlas and current maps | [Site Atlas](https://kajicho-site-atlas.specialgooood.chatgpt.site/) | [index.html](index.html) |
| Interim exhibition | [Interim Progress](https://kajicho-site-atlas.specialgooood.chatgpt.site/studio) | [studio.html](studio.html) |
| Workshop and English meeting report | [Summary](https://kajicho-site-atlas.specialgooood.chatgpt.site/workshop) · [Full report](https://kajicho-site-atlas.specialgooood.chatgpt.site/workshop-report) | [workshop.html](workshop.html) · [workshop-report.html](workshop-report.html) |
| Planning and implementation | [Future Vision](https://kajicho-site-atlas.specialgooood.chatgpt.site/vision) · [Field Visit](https://kajicho-site-atlas.specialgooood.chatgpt.site/field-visit) | [vision.html](vision.html) · [field-visit.html](field-visit.html) |
| 3D conditions and proposals | [Kajicho in 3D](https://kajicho-site-atlas.specialgooood.chatgpt.site/city-model) | [city-model.html](city-model.html) · [city-model-assets](city-model-assets/) |
| Scenario comparison | [Scenario workbench](https://kajicho-site-atlas.specialgooood.chatgpt.site/scenario-workbench) | [scenario-workbench.html](scenario-workbench.html) · [public scenario data](workbench-assets/data.json) |

## Preview locally

Run the command from the repository root.

```sh
python3 08_Scripts/serve_public_website.py
```

Open <http://127.0.0.1:8000>. The preview resolves the same extensionless page links as the hosted site. The local workbench can display the supplied scenario results. For live recalculation and saved jobs, use the [hosted workbench](https://kajicho-site-atlas.specialgooood.chatgpt.site/scenario-workbench).

Published web map exports use the coordinate formats expected by the browser. For distance, area and overlay analysis, use the [EPSG:6677 GIS data](../docs/COORDINATE_REFERENCE.md). [Source notices](../NOTICE.md) · [Font sources and licences](fonts/manifest.json)
