# Kajicho · Urban Design Studio 2026

[English](README.md) | [简体中文](README.zh-CN.md) | **日本語**

東京大学都市デザインスタジオのテーマBの公開授業資料です。データ、QGIS プロジェクト、分析コードを収録しています。神田・日本橋のうち鍛冶町一・二丁目を中心に、建物の更新、暑熱と浸水、公共空間を検討します。

[![JR 神田駅周辺の俯瞰図を掲載した Kajicho 公開サイトのトップページ](06_Outputs/README_Public_Site_2026-11-24/Public_Site_Cover.jpg)](https://kajicho-site-atlas.specialgooood.chatgpt.site)

[公開サイトを開く](https://kajicho-site-atlas.specialgooood.chatgpt.site) · [現在の GIS データを取得](04_Data/Ready/QGIS_Current_2026-11-04/README.md) · [公開サイト第52版のソース](website/README.md)

## スタジオの資料

| 内容 | リンク |
| --- | --- |
| 11月24日の検討会 | [検討会のまとめ](https://kajicho-site-atlas.specialgooood.chatgpt.site/workshop) · [英語の詳細レポート](https://kajicho-site-atlas.specialgooood.chatgpt.site/workshop-report) |
| 11月18日の中間発表 | [成果展示 Between the Centers](https://kajicho-site-atlas.specialgooood.chatgpt.site/studio) · [スタジオの記録](docs/STUDIO_TIMELINE.md) |
| 地域の資料 | [現況データ](https://kajicho-site-atlas.specialgooood.chatgpt.site/conditions) · [現地調査](https://kajicho-site-atlas.specialgooood.chatgpt.site/field-visit) · [歴史](https://kajicho-site-atlas.specialgooood.chatgpt.site/history) · [計画・政策](https://kajicho-site-atlas.specialgooood.chatgpt.site/policy) |
| 2050年に向けた計画 | [将来構想](https://kajicho-site-atlas.specialgooood.chatgpt.site/vision) · [鍛冶町の3Dモデル](https://kajicho-site-atlas.specialgooood.chatgpt.site/city-model) · [シナリオの比較](https://kajicho-site-atlas.specialgooood.chatgpt.site/scenario-workbench) |

## 現在のGISデータ

現行のQGISプロジェクトと空間レイヤーは **EPSG:6677** で統一しています。重ね合わせ、距離、面積の計算に使えます。重点区域の建物年データは277棟分で、56棟は年が未記入です。元の出典、データ年、利用許諾は記録されていません。 [座標とデータの案内](docs/COORDINATE_REFERENCE.md)

**2026年11月4日版**は、**42.43712 haのwider boundary（周辺区域）**を使います。南側を含むすべての境界で、区域と交差する建物は元の輪郭全体を保持します。元の属性と分析対象の所属フィールドは変更していません。関東全域の元データ表は含みません。

| 内容 | ファイルと説明 |
| --- | --- |
| 179件のSHPデータセット | [レイヤー索引](04_Data/Ready/QGIS_Current_2026-11-04/metadata/Layer_Index.csv)、完全な属性と短縮フィールド名の対応表 |
| 192件のGeoPackageテーブル、うち14件は非空間テーブル | [Native data（完全な属性データ）](04_Data/Ready/QGIS_Current_2026-11-04/data) |
| 切り出した17件のラスター、369件のQGISレイヤー | [利用ガイド](04_Data/Ready/QGIS_Current_2026-11-04/README.md) |
| 出典リンク、資料年、処理方法 | [出典ガイド](04_Data/Ready/QGIS_Current_2026-11-04/SOURCES.md) |

1. リポジトリをcloneするか、ZIPをダウンロードして展開します。Git LFSは不要です。
2. フォルダ構成を保ち、QGISで `04_Data/Ready/QGIS_Current_2026-11-04/Kajicho_Current_Data.qgz` を開きます。
3. レイヤー索引から建物、計画、人口、アクセス、環境データを探します。SHPはSHX、DBF、PRJ、CPGと一緒に保持してください。

公開Siteの地図には、それぞれの公開日があります。上記の交付版が最新のダウンロード用GISです。推計値は元の手法と統計単位を保持するため、結合や集計の前に利用ガイドを確認してください。

## リポジトリを使う

| 作業 | 入口 |
| --- | --- |
| 公開サイトを実行・学習する | [サイトのソースとローカル実行ガイド](website/README.md) |
| チームで作業する | [Team start](docs/TEAM_START.md) · [作業計画](docs/PROJECT_PLAN.md) · [提出方法](CONTRIBUTING.md) |
| データとフィールドを調べる | [データガイド](docs/DATA_GUIDE.md) · [レイヤー一覧](04_Data/Metadata/Layer_Catalog.csv) · [フィールド一覧](04_Data/Metadata/Layer_Fields.csv) |
| 分析コードと手法を探す | [コード案内](CODE_INDEX.md) · [Theme Bの手法](03_Theme_B) · [処理スクリプト](08_Scripts) |
| 原資料・外部資料を取得する | [Data access](DATA_ACCESS.md) |
| 日付別の交付・試験を確認する | [交付記録](docs/CURRENT_DELIVERY.md) · [CFDの状態](docs/CFD_STATUS.md) · [研究レビュー](docs/Research_Review_2026-10-18/REPORT.md) |

## データの扱い

資料年、取得日、処理日は別々に保持します。建物のエネルギー値は推計です。建物年代は確定年、期間、未解決の根拠を区別します。各結果に対応する日付別の手法を参照してください。

QGISでは相対パスを使い、地図はPNGで出力します。SHPには付属ファイルを揃えます。プロジェクトの説明は英語を基本とし、中国語・日本語のREADMEも用意しています。ファイル名と原資料の用語は[言語規則](docs/LANGUAGE_GUIDE.md)を参照してください。
