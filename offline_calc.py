# -*- coding: utf-8 -*-
from pathlib import Path
"""Offline arithmetic on numbers transcribed from the LoRA paper. No GPU run, no training."""
lines = []
def emit(s=""):
    lines.append(s)

emit("LoRA reading audit - offline arithmetic")
emit("Paper: Hu et al., LoRA: Low-Rank Adaptation of Large Language Models (arXiv:2106.09685v2).")
emit("All values below are arithmetic on numbers transcribed from the paper.")
emit("No model was trained, no GPU was used, no kernel was run.")
emit()

emit("== D1: three savings, three quantities  [P + A] ==")
vr = 1.2 / 0.35
ckpt = 350_000 / 35
emit(f"  training VRAM  1.2TB -> 350GB : reduction = 1.2/0.35 = {vr:.3f}x  [A]")
emit(f"  VRAM fraction remaining        : 350/1200 = {350/1200*100:.2f}%  [A]")
emit(f"  VRAM saved fraction            : 1 - 350/1200 = {1-350/1200:.3f} (~2/3)  [A]")
emit(f"  checkpoint 350GB -> 35MB       : reduction = 350000/35 = {ckpt}x  [A]")
emit("  => abstract 10,000x = checkpoint/trainable-params; 3x = training VRAM.  [P]")
emit()

emit("== D2: alpha/r scaling  [P + T] ==")
emit("  forward: h = W0 x + (alpha/r) * BA x   (Eq.3 plus alpha/r scaling)  [P]")
emit("  with alpha = r (the 'first r we try') the scale is r/r = 1.0  [T]")
emit("  A ~ Gaussian(0, sigma^2), B = 0  =>  BA = 0 at init  [P]")
emit()

emit("== D3: adapter latency table (GPT-2 medium, ms, RTX8000, 100 trials)  [P + A] ==")
rows = [("Fine-Tune/LoRA", 19.8), ("AdapterL", 23.9), ("AdapterH", 25.8)]
for name, ms in rows:
    emit(f"  {name:<18} batch1={ms} ms")
emit(f"  AdapterL vs baseline: 23.9/19.8 = {23.9/19.8:.3f}  (+{(23.9/19.8-1)*100:.1f}%)  [A]")
emit(f"  AdapterH vs baseline: 25.8/19.8 = {25.8/19.8:.3f}  (+{(25.8/19.8-1)*100:.1f}%)  [A]")
emit()

emit("== D4: subspace similarity  [P + A] ==")
emit("  Ar=8 vs Ar=64: top singular vectors overlap; dim-1 subspace with normalized similarity > 0.5  [P]")
emit("  => top direction carries the useful signal, rest ~ noise, so r=1 works well.  [P]")
emit("  NOT concluded: 'higher rank is always better'.  [P]")
emit()

emit("-- summary --")
emit("  Paper values (P): abstract, Eq.(3)+alpha/r, Table 1, Sec.4.2 VRAM/checkpoint, Sec.7.2 subspace.")
emit("  Arithmetic (A): ratios and percentages above.")
emit("  Teaching (T): alpha/r = 1 when alpha is set to the first r tried.")
emit("  NOT done: no GPU run, no kernel run, no training, no new experiment.")

out = Path(__file__).resolve().parent / "offline-output.txt"
out.write_text("\n".join(lines) + "\n", encoding="utf8")
print("\n".join(lines))
print()
print("wrote", out)

