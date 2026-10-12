# 制作流程与口径清单

每趟旅行固定走这条流程；引擎与模板不变，只换一份 `book_data.json` 和照片。

## 1. 接收输入（用户低成本整理）

- **照片根目录**：`<photos>/1/`、`/2/` …… 子目录名 = 第几天，文件名随意；
  根目录可放 `旅途最佳.jpg`、`couple.png`（署名装饰）、音乐文件。
- **每日回忆**：用户口语化叙述（可分天陆续发），含人名、细节、笑点、狼狈。
- 不要求用户打字录入订单信息；以用户实际叙述与照片为准。

## 2. 扫描与选片

```
python <skill>/scripts/scan_photos.py --photos <照片根>
```

- Read 产出的 `_scan/manifest.md` 和每天 `contact_dN.jpg`（序号对应）。
- 每天选 **约 16–18 张**：横竖搭配、覆盖当天关键事件与情绪，去掉重复 / 糊片。
- 为每天选一张 `cover`（折叠条头图）；从根目录或全天里选一张 `best`（旅途最佳）。
- 照片与封面可由 AI 代选，选完让用户过目。

## 3. 撰写 book_data.json

按 [data_schema.md](data_schema.md) 填写，守住 [data_schema.md](data_schema.md) 的写作口径：
- 每天 `story`（杂志式一段）+ `bits`（碎片小事短句）。
- `stats` 数字**真实统计**：天数、景点数、出海次数等。
  景点口径 = 行程中实际到访、去重后的景点（不含车站、纯餐厅、重复点）。
- `quotes` 金句、`capsule` 下一站、`ending` 谢幕：可 AI 代拟，**交用户核对后定稿**；
  用户已确认的句子逐字保留。

## 4. 地图（可选）

需要封面总览图时按 [map_guide.md](map_guide.md) 准备 `map`；否则省略该字段。

## 5. 构建

```
python <skill>/scripts/build_book.py --book book_data.json --photos <照片根> --out ./site
```

构建器压缩图片、按方向自动排网格跨度、转码音乐（AAC +faststart，失败原样复制）、
注入数据，产出 `./site/index.html` + `assets/`。

## 6. 双端自检（必做）

```
python <html skill>/scripts/shot.py ./site/index.html
```

- 桌面 + 手机都要截图复看，逐项确认：
  - 封面、各天折叠条（**所有天默认折叠**）、四个专栏、谢幕排版正常；
  - 照片网格无重复图、无裂图、无横向溢出；
  - 灯箱点开后可**左右滑动 / 按钮**切换、可关闭；
  - 地图（若有）每个城市点位准确、标签无遮挡、海滨城市为正方形不裁剪；
  - 音乐循环播放、有**可见的关闭按钮**；
  - 控制台无 error（file:// 下 headless 不加载音乐属已知，可忽略）。
- 发现问题改 `book_data.json`（或模板）后**重新 build、重新全量自检**。

## 7. 发布

路径只接受相对当前目录，先 `cd` 到产物所在目录：

```
lark-cli apps +deploy --dir ./site                      # 首发，自动建应用
lark-cli apps +deploy --dir ./site --app-id app_xxx     # 更新同一应用（复用首次 app_id）
```

受理后用返回的 poll 提示执行 `+release-get`，轮询到 `status=finished`，再读 `online_url` 交付。

## 隐私与终稿红线

- **绝不写进公开页**：护照 / 证件号、电子票号、PNR、确认号、订单号、房间号、酒店电话。
- 账号、密码、验证码不写入任何产物或长期记忆。
- 页面保持**终稿**：不放修改日志、版本说明、占位骨架。
- 交付前必须电脑端与手机端均可用；不确定的数字宁可不写。
