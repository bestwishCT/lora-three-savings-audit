# 读论文时把 LoRA 的三种“省”读混怎么办：《LoRA》摘要三个数字的一次真实核查

我在读《LoRA: Low-Rank Adaptation of Large Language Models》（Hu et al., arXiv:2106.09685v2, ICLR 2022）时，在摘要里连续踩到同一个坑：**摘要一句话里同时出现三个关于“省”的数字——可训练参数减少 10,000 倍、GPU 内存减少 3 倍、推理零额外延迟——这三个量不是一回事，却很容易被当成同一件事来读。**

最典型的读法是：把“10,000 倍”当成训练显存省了 10,000 倍（错），把“零额外延迟”当成“推理更快”（错）。这篇分享把问题拆成 D1–D4 四个子题，用一次真实 Bohrium 调用测试，再逐题回到原文核查。结果分两类：**机械层原答失败**（20 个行号整数带前导零，`output.json` 不是合法 JSON），**语义层四题实质回答都正确**。原答原样保留，下面把结论、论文原文、模型原答、作者推导分开写。

## 一、阅读难点

1. **三个数字不是一回事**：摘要“reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times”，把参数数量和显存两个量并排写，方向相同、主语不同。
2. **10,000× 与 3× 的正文对应**：正文 4.2 节把 10,000× 落实为 checkpoint `350GB→35MB`，把约 3× 落实为训练 VRAM `1.2TB→350GB`，同时又说“up to 2/3”。不回到正文，光看摘要会张冠李戴。
3. **“无额外延迟”≠“降低延迟”**：LoRA 的卖点是可把 `W = W0 + BA` 合并，从而不像 adapter 那样**增加**推理延迟；它不是把基线模型变快。

## 二、问题与方法（运行前冻结）

四个子题：
- D1：摘要的 10,000× 与 3× 各对应什么量？1.2TB→350GB、350GB→35MB 各是几倍？
- D2：公式 (3) 是 `BAx` 还是 `(α/r)·BAx`？α/r 是什么？W0 是否冻结、A/B 如何初始化？
- D3：“No Additional Inference Latency”是降低还是不增加？条件是什么？Table 1 与不合并时批处理怎么讲？
- D4：Ar=8 与 Ar=64 的子空间相似度说明什么？能否说 rank 越大越好？

方法：
1. 只给模型物理页 1/4/5/11 的编号文本（`numbered.txt`），要求输出 JSON（decisions D1–D4，每项含 answer / evidence / limitations），行号引用 source_id + start_line/end_line。
2. 调用前 `--dry-run` 逐字核对 message，加独立 nonce 防缓存；服务端 temperature/seed 不可锁定。
3. 机械层 `validate.py` 查 JSON 合法性与行号范围；语义层逐题查数字归属、分母、单位、方向、因果与外推。
4. 原答失败不重写；作者在 `audit.md` 给正确解答，并区分论文值、教学推导、模型输出、作者判断。

冻结哈希见 `protocol-lock.json`（覆盖 `criteria.md`、`protocol.md`、`task.txt`、`sources.json`、`numbered.txt` 及四张页图）。

## 三、真实模型输入、原始输出与 metadata

- 模型：`chenkun/gpt-5-mini`（响应 `data.model`）
- completion id：`chatcmpl-EdWmhLhNmFpmniacxwL7T2edaTGlZ`
- usage：prompt 5191 / completion 4147（含 reasoning 2560）/ total 9338 tokens
- 耗时：40.06 秒；费用：null（服务不逐次返回货币扣费，见 `metadata.json`）
- 输入：`request.txt` = 独立 nonce + `task.txt` + `numbered.txt`
- 原始输出：`output.json`。**它不是合法 JSON**：20 个 `start_line`/`end_line` 整数带三位前导零（模型照抄 `numbered.txt` 的 `019` 显示格式）。`output-normalized.json` 是作者只去掉前导零的机读修复版，未改任何文字或数字。
- `response.json`（余额已脱敏）、`preflight.json`、`metadata.json`、`stderr.txt` 全部保留。

## 四、逐题核查（结论 / 论文原文 / 模型原答 / 作者推导）

### D1：10,000× 与 3× 的归属
- **结论**：摘要“10,000×”=可训练参数/checkpoint（正文 350GB→35MB）；“3×”=训练 VRAM（正文 1.2TB→350GB≈3.43×）。二者不是同一个量。
- **论文原文**：`LORA-P1` 行 19–21 给出摘要两个倍数；`LORA-P5` 行 14–18 给出“up to 2/3”、1.2TB→350GB、checkpoint 10,000×（350GB→35MB）。
- **模型原答**：归属正确，数值 3.43× / 10,000× / 29% 正确。
- **作者推导**：复核无误；“up to 2/3”是省掉的占比，与“减到 1/3”同义。

### D2：(α/r)·BAx 与初始化
- **结论**：实际更新项是 `(α/r)·BAx`；α 是 r 的常数，作者令 α=首次 r 且不调；W0 冻结；A 高斯、B 零初始化使 ΔW 初始为 0。
- **论文原文**：`LORA-P4` 行 23–31（公式 (3) + α/r + 初始化）。
- **模型原答**：全部正确；“α 视为与 r 相关的常数”措辞略松（原文指 α 不随 r 变）。
- **作者推导**：α=r 时缩放为 1，是“换 r 不必重调学习率”的关键设计。

### D3：不额外增加，而非降低
- **结论**：LoRA 不降低基线延迟；合并 `W=W0+BA` 后不额外增加。Table 1 是 GPT-2 medium 单次前向延迟（ms、RTX8000、100 次平均），AdapterL/H 在 batch=1 时 +20.7%/+30.3%。不合并时不同任务 A/B 不便于单 forward 批处理。
- **论文原文**：`LORA-P4` 行 41–44、`LORA-P5` 行 25–28、`LORA-P4` 行 7–11（Table 1）。
- **模型原答**：方向正确，仅举例用了 batch=32 的 +2.2%/+3.0%。
- **作者推导**：复核无误；LoRA 改变的是“部署时是否带额外模块”，不是前向计算量。

### D4：低秩为什么够用
- **结论**：Ar=8 与 Ar=64 的 top 奇异向量显著重叠（一维子空间相似度 >0.5），顶方向最有用、其余多为噪声，故 r=1 就够用；不能外推为“rank 越大越好”。
- **论文原文**：`LORA-P11` 行 59–66。
- **模型原答**：方向与机制正确，并明确不主张 rank 越大越好。
- **作者推导**：复核无误；证据页未含 Table 6 完整 rank 对比，结论止于“低秩足够”。

## 五、离线可复算算例

`offline_calc.py` 只用标准库，对论文数字做算术，不跑 GPU、不训练。真实输出在 `offline-output.txt`：
- 训练 VRAM：1.2/0.35 = 3.429×；剩余 29.17%；省下约 2/3。
- checkpoint：350000/35 = 10000×。
- Table 1（batch=1）：AdapterL 23.9/19.8 = +20.7%；AdapterH 25.8/19.8 = +30.3%。
- 教学：α=r 时 α/r=1。

复算命令：`python offline_calc.py`。

## 六、这次实践证明了什么、没证明什么

**证明了**：
- 在这个任务上，模型语义层四题实质回答正确（数字归属、α/r、延迟方向、低秩机制）。
- 模型再次出现“照抄行号显示格式导致非法 JSON”的真实失败，说明机械层必须独立校验。
- “冻结输入 + 逐行编号 + 双层验收 + 逐题审计”流程对 LoRA 的数值/公式型问题同样成立。

**没有证明、也不能声称**：
- **没有对照**。本次只有一次调用、无 baseline 组，不报告稳定性、显著性、成本或提示词增益。
- **不是隐藏测试**。作者熟悉该论文，这是为检验一个具体读数陷阱设计的已知任务，不构成对模型阅读能力的普遍测量。
- **没有重新跑论文实验**。所有数值来自论文，脚本只做算术。
- **没有 GPU 结论**。未在 GPU 上跑任何 LoRA/训练。
- **服务端 temperature/seed 不可得**，本次结果不可精确复现，只能按同输入再跑看分布。
- **费用为 null**。服务不逐次返回货币扣费。

## 七、复做步骤

1. 取论文：`https://arxiv.org/abs/2106.09685v2`。原 PDF 本地 SHA256 记录在 `SOURCES.md`，本包只含四页合法片段与四张页图，不重新分发整篇 PDF。
2. 重建证据文本：`python build_materials.py`（需要 `pypdf` 与 `pymupdf`/`fitz`）。
3. 冻结输入：`protocol-lock.json` 记录 9 个文件的 SHA256；`run.py` 先校验哈希再调用。
4. 跑一次真实调用（需要本机 `bohr.exe`）：`python run.py`。
5. 机械校验：`python validate.py work/materials/sources.json work/runs/output-normalized.json`（原答 `output.json` 为非法 JSON，机读修复版退出码 0）。
6. 离线算例：`python offline_calc.py`。
7. 逐题语义核查：对照 `audit.md` 人工过一遍。

## 八、材料索引与来源

- **来源**：Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen. *LoRA: Low-Rank Adaptation of Large Language Models*. arXiv:2106.09685v2, 2021-10-16.
- **本包文件**：`README.md`（正文）、`audit.md`（逐题核查）、`SOURCES.md`（来源与许可）、`sources.json`/`numbered.txt`（四页编号原文）、`page1.png`/`page4.png`/`page5.png`/`page11.png`（页图）、`task.txt`/`criteria.md`/`protocol.md`/`protocol-lock.json`（问题与冻结协议）、`request.txt`/`preflight.json`/`response.json`/`output.json`/`output-normalized.json`/`metadata.json`/`stderr.txt`（真实调用记录）、`validate.py`/`validation-raw.json`/`validation-normalized.json`（机械校验）、`offline_calc.py`/`offline-output.txt`（离线算例）、`summary.json`（机器可读小结）。
- **个人贡献**：把 LoRA 的三种“省”拆成 D1–D4；重建编号证据与连字修复；冻结运行；一次真实 Bohrium 调用；逐题核查；离线算例与复做教程。
- **披露**：核查由 Codex 辅助、作者本人（非盲）复核，不是独立人类评审，也不是对模型阅读能力的独立测量。
- 原创文字与脚本以 MIT 许可发布（`LICENSE`）；第三方论文片段保留原许可（见 `SOURCES.md`）。
