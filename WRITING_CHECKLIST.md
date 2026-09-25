# Writing Checklist for "All Memory Is Local"

## 快速参考清单

---

## 必须避免 (❌)

1. ❌ "我们证明没有长期记忆" → ✅ "not distinguishable from adaptation"
2. ❌ "memory disappears after 15 sessions" → ✅ "excess no longer distinguishable from transfer"
3. ❌ "our protocol eliminates all confounds" → ✅ "controls for the confounds we identify"
4. ❌ "our theory explains TTT" → ✅ "consistent with observed decay pattern"
5. ❌ "Sessions are isotropic" → ✅ "We construct vocabularies to approximate isotropy"
6. ❌ "The effect increases with model scale" → ✅ "larger at 4B, although single-seed"
7. ❌ 把 significant 写成 important
8. ❌ 编造虚假的研究过程 ("Initially, we were surprised...")
9. ❌ 把 post-hoc interpretation 写成 prediction
10. ❌ 为了 human-like narrative 改写真实研究史

---

## 必须突出 (✅)

### S-tier (必须进正文)
1. Delayed retrieval ≠ persistence
2. Fresh-session control
3. Interpretation changed because of control
4. Rapid decay of session-specific component
5. Adaptation explains long-lag residual

### A-tier
6. Contamination / vocabulary controls
7. Capability cost
8. Write-mass theory (as pre-specified prediction)

### B-tier (可压缩)
9. Session-reset policy
10. Consistency gating

### C-tier (放 Appendix)
11. Fisher / surprise / extra comparisons

---

## 值得保留的"人类痕迹"

- ✅ Shared vocabulary bug ("inflated 2× before being fixed")
- ✅ H2 interpretation 被改变 ("revise the interpretation")
- ✅ Unattributed remainder ("we have not isolated it")
- ✅ Theory → Prediction → Test 的真实时间顺序

---

## 理论的正确写法

❌ "Our theory is validated."
❌ "These results prove Proposition 1."

✅ "The observed scaling is consistent with Proposition 1."
✅ "The η sweep supports the prediction derived from the model."

---

## 写作风格

| 避免 | 替换为 |
|------|--------|
| We demonstrate X. We show Y. We establish Z. | We observe... This suggests... The control indicates... |
| Taken together... | (删除或重组) |
| First... Second... Finally... | 自然展开 |
| This demonstrates X. | 让 evidence 自己说话 |

---

## Results 每节检查

- [ ] What did we observe?
- [ ] What could explain it?
- [ ] What alternative exists?
- [ ] What control distinguishes?
- [ ] What changed after control?
- [ ] What can we claim?

---

## 统计表述检查

- [ ] non-significant ≠ evidence of equality
- [ ] CI overlap ≠ equivalence test
- [ ] single-seed claim 降级
- [ ] "not distinguishable" ≠ "absent"

---

## 如果只改 5 件事

1. Introduction: "six artifacts" → "delayed retrieval ≠ persistence"
2. Fresh-session control 升级为 centerpiece
3. Results 重排: observation → control → revised interpretation
4. §3.4 写出 Testable Predictions
5. Secondary results 移入 Appendix

---

*快速参考版本 - 详细内容见 REVISION_BLUEPRINT.md*
