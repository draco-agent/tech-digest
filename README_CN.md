# Tech Digest 📰🐉

自动化科技新闻日报/周报系统，为 [OpenClaw](https://github.com/openclaw/openclaw) 打造的 Agent Skill。

三层数据采集，覆盖 AI/LLM、加密货币、前沿科技领域。

## 特性

- **RSS 一手源** — 30+ 精选技术博客和新闻源（灵感来自 [Karpathy 推荐的 HN 顶级博客](https://github.com/vigorX777/ai-daily-digest)）
- **Web Search** — 实时热点补充，支持时间窗口过滤
- **Twitter/X KOL 监控** — 30+ 大V，覆盖 AI、Crypto（含华语 KOL）、科技
- **多渠道发布** — Discord、Telegram、Email
- **报告归档** — 自动保存到 workspace，方便回看
- **完全可定制** — RSS 源、KOL 列表、话题、语言、发布渠道均可配置，且提供合理默认值

## 默认话题

开箱即用，报告涵盖以下话题（可通过 `config/tech-digest-topics.json` 自定义）：

- 🧠 **LLM / 大模型** — GPT、Claude、Gemini、开源模型、评测
- 🤖 **AI Agent** — 自主智能体、框架、工具调用
- 💰 **加密货币** — Bitcoin、Ethereum、DeFi、监管
- 🔬 **前沿科技** — 突破性进展、机器人、量子、生物技术

加上固定板块：

- 📢 **KOL 动态** — Twitter 大V + 博客重要发文
- 🔥 **Twitter/X 热议** — 病毒式传播讨论
- 📝 **博客精选** — RSS 源深度文章
- 📊 **本周趋势总结**（仅周报）

## 快速开始

### 通过 OpenClaw 安装

最简单的方式 — 直接对你的 OpenClaw bot 说：

> 从 ClawHub 安装 tech-digest skill 并配置好。日报和周报都在早上 7 点发到 Discord #news 频道。

Bot 会自动完成安装、配置和 cron 任务创建。

### 手动安装

**第 1 步：安装 Skill**

```bash
# 通过 ClawHub
clawhub install tech-digest

# 或通过 Git
git clone https://github.com/dracohoard/tech-digest.git ~/.openclaw/workspace/skills/tech-digest
```

**第 2 步：复制配置到 workspace**

```bash
mkdir -p ~/.openclaw/workspace/config ~/.openclaw/workspace/archive/tech-digest
cp ~/.openclaw/workspace/skills/tech-digest/config/tech-digest-*.json ~/.openclaw/workspace/config/
```

**第 3 步：设置 Cron 任务**

打开 `references/digest-prompt.md` — 这是日报和周报的统一模板。替换 `<...>` 占位符（文件内有对照表），然后用填好的 prompt 创建 cron 任务。

默认时间：日报和周报均为早上 7:00。

**第 4 步：（可选）Twitter/X API**

```bash
echo 'export X_BEARER_TOKEN="your-token"' >> ~/.zshenv
```

**此步骤可选** — 不配置也能通过 web search 抓取 Twitter 热点。

**第 5 步：（可选）邮件推送**

需要 [gog CLI](https://github.com/panyq357/gog) 配合 Gmail。不需要邮件的话，从 prompt 模板中删除邮件相关行即可。

**第 6 步：验证**

对 bot 说"现在跑一次日报"，或手动触发：

```bash
openclaw cron list        # 查看任务 ID
openclaw cron run <id>    # 触发执行
```

## 自定义

所有配置都有合理默认值，按需修改：

| 内容 | 文件 | 说明 |
|------|------|------|
| **RSS 源** | `config/tech-digest-rss-feeds.json` | 按领域增删源，`"priority": true` 标记必抓源，默认 30+ 个 |
| **Twitter KOL** | `config/tech-digest-kol-list.json` | 按分类增删 Twitter 账号，默认 30+ 个覆盖 AI、crypto（含华语）、科技 |
| **话题和板块** | `config/tech-digest-topics.json` | 增删/排序话题，每个话题定义 emoji、标题、搜索关键词 |
| **发布渠道** | `references/digest-prompt.md` | Discord + Telegram + Email，按需增删 |
| **发送时间** | Cron 任务配置 | 默认：日报和周报均为早上 7:00 |

## 目录结构

```
tech-digest/
├── SKILL.md                          # Skill 主文件（给 agent 读）
├── README.md                         # English docs
├── README_CN.md                      # 本文件
├── LICENSE                           # MIT 许可证
├── config/
│   ├── tech-digest-rss-feeds.json    # RSS 源配置（需复制到 workspace）
│   ├── tech-digest-kol-list.json     # Twitter KOL 配置（需复制到 workspace）
│   └── tech-digest-topics.json       # 话题定义（需复制到 workspace）
├── references/
│   ├── digest-prompt.md              # 统一 prompt 模板（日报和周报共用）
│   └── config-schema.md             # 配置文件字段说明
└── scripts/
    └── fetch-rss.py                  # 并行 RSS 抓取 + 归档清理
```

## 致谢

- [vigorX777/ai-daily-digest](https://github.com/vigorX777/ai-daily-digest) — RSS 源灵感来源
- [Andrej Karpathy](https://x.com/karpathy) — HN 顶级博客推荐列表
- [OpenClaw](https://github.com/openclaw/openclaw) — Agent 运行时框架

## 许可证

MIT
