---
name: travel-memory-book
description: 旅行纪念册网页生成器。当用户想把一次旅行的照片与回忆做成可发布、可分享的网页纪念册、旅行相册、照片回忆录或旅行手账时使用。用户只需提供「按天整理的照片文件夹（1/2/3 子目录，文件名随意）+ 口语化每日回忆」，即可产出胶片摄影杂志风的响应式单页：封面手绘总览地图（可选）、逐日折叠照片墙、旅途最佳大图、纪念数据、金句、时间胶囊专栏与谢幕，并完成桌面与手机双端自检和在线发布。模板与构建 / 地图 / 灯箱引擎固定，每趟只换一份 book_data.json 与照片。
---

# Travel Memory Book

把一次旅行沉淀为一本「印出来的摄影杂志」风格网页。核心是**数据与引擎分离**：模板、构建器、地图与灯箱引擎不变，每趟只准备一份 `book_data.json` 和一个照片文件夹，用户整理成本最低。

## 用户需要给什么

- **照片根目录**：`<photos>/1/`、`/2/` …… 子目录名 = 第几天，文件名随意；
  根目录可放旅途最佳一张、couple 装饰图、音乐。
- **每日回忆**：口语化叙述（可分天陆续发），保留人名、细节、笑点与狼狈。
- 不让用户打字录入订单；信息以叙述和照片为准。

## 端到端流程

1. **扫描选片**：`python scripts/scan_photos.py --photos <照片根>`，Read 清单与每日 contact sheet，
   每天选约 16–18 张 + 当日 cover + 全页 best（可 AI 代选后让用户过目）。
2. **写 book_data.json**：每日 story / bits，统计 stats，代拟金句 / 时间胶囊 / 谢幕并交用户核对。
3. **地图（可选）**：需要封面总览图才准备 `map`，否则省略。
4. **构建**：`python scripts/build_book.py --book book_data.json --photos <照片根> --out ./site`。
5. **双端自检**：用 html skill 的 `shot.py` 截桌面 + 手机，逐项核对（见下）。
6. **发布**：`lark-cli apps +deploy --dir ./site`，轮询到 `finished`，交付链接。

完整操作、命令与口径见 [references/workflow.md](references/workflow.md)。

## 何时读哪份参考

- 填写 / 核对数据结构、字段与写作口径 → [references/data_schema.md](references/data_schema.md)。
- 微调模板、颜色、字体、版式 → [references/visual_spec.md](references/visual_spec.md)。
- 制作封面总览地图（坐标、view、意向化、防遮挡）→ [references/map_guide.md](references/map_guide.md)。
- 完整流程、自检清单、发布与隐私红线 → [references/workflow.md](references/workflow.md)。

## 交付前自检要点

桌面 + 手机双端截图确认：所有天默认折叠、照片网格无重复 / 裂图 / 横向溢出、
灯箱可左右滑动与关闭、地图点位准确且标签无遮挡（海滨城市为正方形不裁剪）、
音乐循环且有可见关闭按钮、控制台无 error。改后重新 build 并全量复检。

## 硬约束

- 数字（天数、景点数、出海次数）从实际行程与照片统计，不编造；景点按实际到访去重计数。
- 用户已确认的金句 / 胶囊答案 / 署名逐字保留。
- 证件号、票号、PNR、确认号、订单号、房间号、酒店电话不进公开页；账号密码不写产物或记忆。
- 页面保持终稿，无版本说明 / 修改日志；交付前电脑端与手机端必须都可用。
