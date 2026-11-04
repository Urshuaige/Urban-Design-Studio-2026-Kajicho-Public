# Language and naming

English is the default for filenames, project-authored documentation, comments, task descriptions and repository metadata. The root README provides [English](../README.md), [Chinese](../README.zh-CN.md) and [Japanese](../README.ja.md) entry points. The website starts in English for a new visitor and keeps a visitor's explicit language choice.

Use descriptive ASCII filenames with the existing folder and date conventions. The tracked filenames were already ASCII at this revision, so no data-path migration was needed. Name optional translations with a language suffix, for example `README.zh-CN.md` and `README.ja.md`.

Official documents, source titles, place names, IDs, original field names and category values retain their original spelling. Changing these values would break source tracing or data joins. Use the [English field-name glossary](../04_Data/Metadata/Field_Name_Glossary.csv) to interpret Japanese GIS fields; the field catalog continues to match the GeoPackage schema exactly.

Chinese/Japanese language dictionaries and explicitly named fields such as `label_zh` remain translations. Previously issued map images and dated download archives retain their versioned content. New documentation and editable descriptions use English first; a translation should preserve numbers, units, uncertainty and source links.

Run `python3 08_Scripts/check_repository_language.py` to check the three README entry points, local Markdown links, ASCII filenames and website default-language settings. This is a structural check; review translation meaning separately.
