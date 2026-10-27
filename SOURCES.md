# 来源、版本与许可

## 论文

Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen.
*LoRA: Low-Rank Adaptation of Large Language Models.*
arXiv:2106.09685v2 [cs.CL], 2021-10-16. https://arxiv.org/abs/2106.09685
会议版本：ICLR 2022.

许可：论文 arXiv 版本按 arXiv 许可发布；本包只含足以核查结论的四页片段与四张页图，不重新分发整篇 PDF。

## 本包包含什么（版权合规说明）

本包**不重新分发整篇 PDF**。只包含：

| 内容 | 物理页 | 形式 |
|---|---|---|
| `LORA-P1` | 1（摘要 + 第 1 节开头） | 逐行文本 + 页图 `page1.png` |
| `LORA-P4` | 4（Table 1 + 第 4 节方法 + 公式 (3) + α/r + 无额外延迟） | 逐行文本 + 页图 `page4.png` |
| `LORA-P5` | 5（第 4.2 节：VRAM/checkpoint 数字 + 批处理限制） | 逐行文本 + 页图 `page5.png` |
| `LORA-P11` | 11（第 7.2 节：子空间相似度，Figure 3 / 公式 (4)） | 逐行文本 + 页图 `page11.png` |

**署名与出处**：以上片段全部出自上述论文，保留原作者署名与许可。本包中的原创文字与脚本以 MIT 许可发布（见 `LICENSE`）。

## 版本与校验

- 原 PDF：`github68/lora.pdf`（本地保留，不随包分发）。
- 原 PDF SHA256：`e9a0d3128767db616085dc0f4e6e455e672e89af823e8ed1282793682787395a`
- 页码约定：`page` 是 PDF 物理页（从 1 开始），不是印刷页码。本文正文页码与物理页码一致（首页即第 1 页）。

## 抽取与修复

- 该 PDF 的提取文本含连字（ligature）字符，如 `ﬁ`→`fi`、`ﬂ`→`fl`、`ﬃ`→`ffi`。`build_materials.py` 在生成 `sources.json`/`numbered.txt` 前做了这些替换，**不改任何数值与内容**。
- 数学符号（`ℝ`、`∈`、`≪`、`×`、`√`）保留为 Unicode，与原文一致。
- 未对提取文本做任何语义改写；行号 `001` 起始、含两端。

## 第三方内容

- 论文片段：Hu et al.，arXiv:2106.09685v2（见上）。
- 本包引用的公式 (3)(4)、Table 1、Sec.4.2 / 7.2 内容均出自该论文。
- 无其它第三方数据、无凭据、无私有数据。
