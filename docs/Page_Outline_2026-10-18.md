# Page outline

The atlas has a fixed outline on its left edge. Eight chapter marks are longer than the 27 subsection marks. Hover over the rail to open the titles; select a title to jump to that part of the page. The current item and its chapter follow scrolling.

The outline reads the rendered headings, including maps and source sections loaded later. It updates with the English, Chinese and Japanese page labels. Enter opens the outline, Escape closes it, and a selected link moves focus below the fixed header. On narrow screens, a Contents button opens the same list.

The source assets are in `08_Scripts/site_modules/page-outline.js` and `page-outline.css`. `install_page_outline.py` adds them to the atlas without rebuilding its data. The standard site assembler calls that installer before saving the repository mirror.

Checks covered a child link, its target position and scroll highlight; all three languages; Enter and Escape; the narrow-screen toggle and panel bounds; JavaScript syntax; unique asset references; and matching Site/repository bytes. See [release record](Page_Outline_Release_2026-10-18.json).
