# AI Girlfriend Kit

一个本地管理 AI 伴侣人格和长期记忆的小工具。

我做这个主要是因为现成的角色卡要么太假，要么记忆全靠模型自己记，聊久了就崩。想自己控制性格和记忆，就慢慢整理成现在这样。

现在有了真正的 CLI，可以结构化地管记忆，并一键生成可直接复制给模型的 context。

仍然是 local-first、不上传、不绑定任何模型供应商。

---

## 60 秒上手

```bash
pip install .

aigf init
aigf persona list
aigf persona set teasing-sister

aigf memory add "我不喜欢被冷暴力" --category preference --importance high
aigf memory add "我喜欢别人主动哄我" --category relationship --importance high

aigf context build
```

把输出的整段 context 复制到你正在用的前端 / 本地模型 / API 对话里即可。

---

## 它实际做什么

- **人格（persona）**：继续用人类可读的 markdown，中英双语
- **长期记忆（memory）**：结构化 JSONL，可增删改搜、去重、归档
- **Context 构建**：根据当前人格 + 选中的记忆，生成稳定、可预测的提示文本
- **Export**：plain prompt / SillyTavern card / OpenWebUI JSON
- **不调用任何 LLM**：选择记忆、生成 context 都是本地确定性逻辑

---

## 常用命令

```text
aigf init
aigf doctor
aigf version

aigf persona list
aigf persona set <name>
aigf persona show <name>

aigf memory add "内容" --category preference --importance high
aigf memory list
aigf memory search 关键词
aigf memory remove <id前缀>
aigf memory archive <id前缀>
aigf memory compact
aigf memory compact --drop-archived
aigf memory export backup.jsonl

aigf context build
aigf context build --lang en --max-memories 8

aigf export prompt
aigf export sillytavern card.json
aigf export openwebui ow.json
```

记忆分类：`user_profile` / `preference` / `relationship` / `event` / `boundary` / `ongoing_topic` / `favorite` / `other`

---

## 人设

| 名称 | 风格 | 备注 |
|------|------|------|
| teasing-sister | 会调戏人的姐姐 | 我自己最常用 |
| soft-clingy | 软萌粘人 | 想被哄的时候 |
| mature-gentle | 成熟温柔 | 情绪不好时 |
| cold-beauty | 表面冷淡 | 还在调 |

人设模板随包发布，`aigf init` 会复制到项目里的 `personalities/`，直接改 markdown 就行。没初始化也能用：`persona list` 会回退到内置模板。

---

## 隐私

- 记忆默认在 `.aigf/memories.jsonl`
- 不上传、无 telemetry、无远程同步
- `aigf doctor` 会简单扫描明显的 API key 形态

---

## 开发 / 测试

```bash
pip install -e .
pip install pytest ruff
pytest -q
ruff check src tests
```

CI 覆盖 Python 3.10–3.13。

---

## 状态

早期 v0.1。单人维护。  
目标是好用、可改、本地可控，不是做一个大而全的陪伴平台。

MIT。
