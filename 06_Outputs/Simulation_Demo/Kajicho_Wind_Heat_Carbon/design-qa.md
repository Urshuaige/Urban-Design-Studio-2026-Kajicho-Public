# Portfolio design QA

final result: passed

The visual reference is the user's urban-design mapping boards, adapted to a responsive Site. The task requests a new composition and local palette, so this is an adaptation review, not a pixel copy. The reference's source area differs from Kajicho and is used only for layout and drawing language.

Source visual truth: `../../Portfolio_2026-10-15/qa/reference-site-context.png` (1088×914) and `reference-theme-plates.png` (1174×1316). Implementation: `../../Portfolio_2026-10-15/qa/home-desktop-zh.jpg`, `mapping-desktop-zh.jpg`, `mapping-mobile-en.jpg`, `team-mobile-ja.jpg`, `cfd-math-mobile-ja.jpg`. Browser CSS viewports were 1440×1000 and 390×844. Screenshots use the in-app browser's JPEG output at its captured density. Source and implementation were opened together in the same comparison input; no pixel-level equality is implied across different content and viewports.

Typography: Chinese/Japanese Noto Serif display and body roles, Caslon Latin display, Source Serif Latin body, Sans UI and mono code are assigned through composite font families. Page language selects the regional CJK form. Fonts are self-hosted. Main heading, section heading, body and caption levels remain distinct on mobile. KaTeX retains its math family; 99 math/MathML instances render without errors.

Layout: a large site map sits beside a short introduction. The atlas uses a main plate with adjacent reading notes and an indexed set of thematic plates. Fine rules, flat surfaces, consistent margins and a paper background echo the supplied boards. On mobile, columns stack and theme tabs wrap. No horizontal document overflow was found at 390px in the portfolio, team page, studies, style guide or CFD guide.

Colours: Edo purple and dark grey derive from the Chiyoda public-sign reference; the digital HEX values are declared as studio choices. Observed building/land uses use MLIT category colours, not the identity accent. Height proxies and unknown uses retain separate legends.

Images: actual GIS geometry supplies seven maps. There are no generated or fictional geographic assets. Lightweight previews retain full SVG/PNG downloads. All plates use the same extent, north direction and scale; legal zoning and observed use are separate. Focused map review used the building-use JPEG to inspect labels, category colours, station names, legend and scale. A coverage-line correction and scale-label padding were completed in the cartographic pass before final asset integration.

Copy: 12 source-backed context records retain document year, web date and download date. Three-language UI and content were checked. Design actions are discussion prompts; source gaps and current CFD status stay beside the relevant information.

Interactions: context filtering, theme selection, keyboard-tab handlers, full-plate dialog, detail zoom and close, language switching, shared package links and figure downloads are implemented. Browser checks exercised filters, map selection, dialog/zoom/close and language switching. Source/asset/ZIP validation checked all local targets, 22 archive members, font files and size limits. Studies still initializes two WebGL canvases. Browser error/warning logs were empty on the tested new and existing routes.

Comparison history: the first complete web composition had no actionable P0/P1/P2 findings. The cartographic review corrected an overly broad coverage outline and scale padding before final integration. Final source/asset sync retained those corrections. Small-print source details remain available at full resolution and in the manifest.

Expected differences: actual Kajicho geometry, official Japanese thematic colours, regional serif type, responsive tabs and source disclosures replace the reference board's location, palette and static page format. Static downloadable plates use English/Chinese labels, with Japanese place names; the surrounding Site explanations support Chinese, English and Japanese.

## PNG delivery correction · 2026-10-15

The user's later instruction replaces SVG map delivery with PNG only. All active SVG map assets and links are removed. The map dialog now displays the existing 3200px PNG, and the downloadable atlas contains seven PNG plates plus source records (15 files). The exporter no longer writes SVG; the CI contract rejects SVG map files, archive entries and producer filename literals. Browser readback confirms a 3200px PNG, zero SVG links and a working modal. The earlier comparison above records the original design pass; the current delivery format is PNG. No map rerender or CFD job was needed.
