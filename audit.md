# 作者逐题核查（github68 / LoRA）

原答来自一次真实 Bohrium 调用（model=`chenkun/gpt-5-mini`，completion_id=`chatcmpl-EdWmhLhNmFpmniacxwL7T2edaTGlZ`）。
原答有一个**真实机械失败**：20 个 `start_line`/`end_line` 整数带前导零（`019`、`021`…），导致 `output.json` 不是合法 JSON。
`output-normalized.json` 是作者**只把前导零去掉**的机读修复版，未改任何文字、数字或行号范围。
下面每道题把「结论 / 论文原文 / 模型原答 / 作者推导」分开写，并给判定。

---

## D1：摘要的 10,000× 与 3× 各对应什么量

- **结论**：摘要“10,000 times”对应**可训练参数 / checkpoint 大小**（正文 350GB→35MB）；“3 times”对应**训练时 GPU 内存 / VRAM**（正文 1.2TB→350GB，约 3.43 倍）。两个数字不是同一个量，最容易读反。
- **论文原文**：`LORA-P1` 行 19–21：“Compared to GPT-3 175B fine-tuned with Adam, LoRA can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times.” `LORA-P5` 行 14–18：“reduce that VRAM usage by up to 2/3 … reduce the VRAM consumption during training from 1.2TB to 350GB. With r=4 and only the query and value projection matrices being adapted, the checkpoint size is reduced by roughly 10,000× (from 350GB to 35MB).”
- **模型原答**：方向判断正确——10,000×=checkpoint、3×=VRAM；并正确算出 1.2TB/0.35TB≈3.43、350GB/35MB=10,000、剩余 29%。证据用 `LORA-P1` 19–21、`LORA-P5` 14–18、`LORA-P5` 46–47。
- **作者推导**：复核无误。1.2/0.35=3.43；350000/35=10000；350/1200=29.2%。补充一点：“up to 2/3”是**省掉**的 VRAM 占比（约 2/3），与“减到 350GB（约 1/3 剩余）”是同义的两面，不是两处矛盾数字。
- **判定**：✅ 正确。

## D2：更新项是 BAx 还是 (α/r)·BAx

- **结论**：实际前向项是 **(α/r)·BAx**。公式 (3) 先写 `h = W0x + ΔWx = W0x + BAx`，随后明确“scale ΔWx by α/r”。α 是关于 r 的常数；作者令 α=首次尝试的 r 且不再调，这样改变 r 时几乎不用重调学习率。训练时 W0 冻结；A 高斯初始化、B 零初始化，故 ΔW=BA 初始为 0。
- **论文原文**：`LORA-P4` 行 23–31：“During training, W0 is frozen … We use a random Gaussian initialization for A and zero for B, so ΔW=BA is zero at the beginning of training. We then scale ΔWx by α/r, where α is a constant in r … we simply set α to the first r we try and do not tune it.”
- **模型原答**：更新项、α/r 作用、W0 冻结、A/B 初始化全部正确。措辞“把 α 视为与 r 相关的常数”略松：原文“a constant in r”指 α **不随 r 变**，不是“取决于 r”。
- **作者推导**：复核无误。设 α=r 时缩放为 r/r=1，这是作者减少超参重调的关键设计，不是“除以 rank 让更新变小”的简单含义。
- **判定**：✅ 正确（一处措辞可更严谨，非数值错误）。

## D3：“No Additional Inference Latency”是降低还是不增加

- **结论**：是**不额外增加**，不是降低。条件是把 `W = W0+BA` 在部署前显式合并，推理与普通微调模型同构。Table 1 测的是 GPT-2 medium 单次前向推理延迟（ms，平均 100 次，RTX8000）：AdapterL/AdapterH 相对 Fine-Tune/LoRA 在 batch=1 时 +20.7% / +30.3%。不合并时，不同任务的 A/B 不能方便地在单个 forward 里批处理。
- **论文原文**：`LORA-P4` 行 41–44：“we can explicitly compute and store W = W0+BA … guarantees that we do not introduce any additional latency.” `LORA-P5` 行 25–28：“it is not straightforward to batch inputs to different tasks with different A and B in a single forward pass.”
- **模型原答**：方向正确，正确说出“不额外增加 + 需合并 + 不合并难批处理”；Table 1 的定位正确。仅举例时用 batch=32 的 +2.2%/+3.0%，未强调短序列下 +20.7%/+30.3% 更显著。
- **作者推导**：复核无误。LoRA 不改变基线模型的前向计算量；与 adapter 的差别在于“可合并、不加延迟”。
- **判定**：✅ 正确。

## D4：r=1 为什么不错，能否说 rank 越大越好

- **结论**：Ar=8 与 Ar=64 的 top singular vector 方向显著重叠（一个维度上归一化相似度 >0.5），说明最有用的适配方向集中在头部奇异向量，其余方向多为训练噪声，因此 r=1 就够用。**不能**据此说“rank 越大越好”。
- **论文原文**：`LORA-P11` 行 59–63：“Directions corresponding to the top singular vector overlap significantly … share a subspace of dimension 1 with normalized similarity > 0.5, providing an explanation of why r=1 performs quite well in our downstream tasks for GPT-3.” 行 64–66：“the top singular-vector directions … are the most useful, while other directions potentially contain mostly random noises … the adaptation matrix can indeed have a very low rank.”
- **模型原答**：方向正确，机制解释正确，并明确“论文不主张 rank 越大越好”。
- **作者推导**：复核无误。证据页未含 Table 6 的完整 rank 对比（r=1/2/4/8/64），结论只到“低秩足够 + 顶方向最有用”，不越界外推。
- **判定**：✅ 正确。

---

## 手工核验清单（提交前逐项）

- precision/recall、TP/FP/FN：本次为数值核查，无二分类预测，不适用。
- 分母：D1 的倍数分母是“减少后的值”（350GB、35MB），已核对。
- 单位：GB vs TB vs MB 已统一换算（1.2TB=1200GB）。
- 方向：10,000× 与 3× 的归属方向已与正文 4.2 节逐字核对。
- 因果与外推：D4 未把“低秩足够”外推为“rank 越大越好”；D3 未把“不加延迟”说成“降低延迟”。
- 表头：Table 1 是 GPT-2 medium、ms、RTX8000、100 次平均；已核对。
- 原答失败不重写：`output.json` 原样保留；`output-normalized.json` 仅去前导零并明确标注。

## 结论

- 机械层：原答非法 JSON（20 个前导零），机读修复版 `ranges_valid`，10 段证据全在范围内。
- 语义层：D1–D4 四题的实质回答均正确；仅 D2 一处措辞、D3 一处举例选择可更严谨。
- 本次是“已知陷阱的单次测试”，无对照、无增益声称。
