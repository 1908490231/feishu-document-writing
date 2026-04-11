---
name: feishu-document-writing
description: 当用户需要将本地文件发布到飞书文档时使用。用户说"发布到飞书"、"写入飞书文档"、"上传到知识库"、"上传到文件夹"、"上传附件到飞书"、"把这个文件传到飞书"时触发。支持 MD、TXT、CSV、XLSX、DOCX 内容写入，以及任意文件作为附件上传。
---

# 飞书文档写入

将本地文件一键发布到飞书文档，支持 MD/TXT/CSV/XLSX/DOCX 内容解析写入，以及同步上传文件附件到文档最前面。**请严格按照以下步骤执行，不要检查环境、不要检查配置、不要安装依赖，直接执行命令。**

## 第一步：确定文件路径和目标位置

从用户消息中提取：
1. **文件路径**：用户要上传的文件路径
2. **判断上传方式**（见下方规则）
3. **目标位置**：按以下优先级判断（脚本内置了自动路由，大多数情况下不需要指定 `--target`）

### 上传方式判断规则

**默认规则（无需用户说明时使用）**：

| 文件类型 | 默认处理方式 |
|---|---|
| `.md` | 解析内容写入飞书文档（标题、代码块、表格、图片等） |
| `.txt` | 解析内容写入飞书文档（按段落写入，识别 `#`/`##` 标题） |
| `.csv` | 解析内容写入飞书文档（整体转为飞书表格） |
| `.xlsx` | 解析内容写入飞书文档（每个 Sheet 生成独立表格） |
| `.docx` | 解析内容写入飞书文档（保留标题层级/段落/表格） |
| **其他文件**（PDF、ZIP、图片、HTML 等） | 提示使用 `--attachment` 上传为文件附件 |

**用户明确指定时，以用户指定为准**：

| 用户指定 | 执行方式 |
|---|---|
| "把这个文件作为附件上传" | 走 `--attachment` |
| "用 import 方式导入" | 加 `--import` 参数（文件放入 folder，不可写入 wiki） |
| 同时提到 md 文件 + 其他文件 | 各走各自的默认流程 |

**路由优先级**（从高到低）：
1. 用户提供了 `folder_token` → 上传到指定文件夹
2. 用户提供了 `node_token` → 上传到指定知识库节点
3. 用户未提供 token → 脚本自动检测 `.env` 中的默认配置，按 folder → wiki → space 顺序选择

## 第二步：立即执行上传命令

**不要做任何前置检查**，直接执行命令。重复文件会自动创建新文档，无需额外参数。

### 最简命令（自动路由到 .env 中配置的默认位置）
```bash
# MD / TXT / CSV / XLSX / DOCX 均可直接传入，自动解析内容写入飞书文档
python -m scripts.feishu_writer "<文件绝对路径>"
```

### 同时上传附件到文档最前面
```bash
python -m scripts.feishu_writer "<md文件路径>" --attachment "<附件文件路径>"
```

### 用户指定了 folder_token
```bash
python -m scripts.feishu_writer "<文件绝对路径>" --folder-token <folder_token>
```

### 用户指定了 node_token
```bash
python -m scripts.feishu_writer "<文件绝对路径>" --wiki-token <node_token>
```

### 批量上传目录（自动收集 md/txt/csv/xlsx/docx）
```bash
python -m scripts.feishu_writer "<目录绝对路径>"
```

### 使用 import_tasks 导入到 folder（非内容解析方式）
```bash
# 注意：--import 只能配合 folder_token 使用，不支持 wiki
python -m scripts.feishu_writer "<文件绝对路径>" --import --folder-token <folder_token>
```

## 第三步：报告结果

命令执行成功后，从输出中提取并告知用户：
- **文档名称**
- **文档链接**（输出中的 `链接:` 行）
- **图片上传情况**
- **附件上传情况**（输出中的 `[附件]` 行，告知附件已插入文档最前面）
- **重复文件信息**（如果输出中包含"重复文件"相关信息，告知用户哪些文件已存在同名文档并已自动新建）

## 支持的格式

**内容写入格式（解析为可编辑飞书文档）**：

| 格式 | 支持内容 |
|---|---|
| `.md` | 标题(h1-h9)、段落（加粗/斜体/行内代码）、代码块、无序/有序列表、引用、图片（自动上传）、表格、链接、分割线 |
| `.txt` | 段落文本，识别 `#` / `##` 标题 |
| `.csv` | 整体转为飞书表格（含表头） |
| `.xlsx` | 每个 Sheet 生成独立二级标题 + 表格 |
| `.docx` | 标题层级、段落、表格 |

**附件上传**：PDF、HTML、ZIP、图片等其他格式，使用 `--attachment` 参数上传为可下载文件块。

## 仅在报错时参考以下内容

如果第二步的命令执行失败，根据错误信息采取对应措施：

| 错误信息 | 原因 | 解决方式 |
|---|---|---|
| `ModuleNotFoundError` | 依赖未安装 | 执行 `pip install requests python-dotenv markdown requests-toolbelt` 后重试 |
| `获取 token 失败` / `FEISHU_APP_ID` | .env 配置缺失 | 提示用户参考 `references/setup-guide.md` 配置 .env |
| `permission denied` | 应用权限不足 | 提示用户参考 `references/setup-guide.md` 添加协作者权限 |
| `路径不存在` | 文件路径错误 | 确认文件路径后重试 |
| 图片上传失败 | 图片路径或格式问题 | 参考 `references/troubleshooting.md` |
| 附件显示失败 | 文件附件上传流程问题 | 参考 `references/troubleshooting.md` 文件附件章节 |

## 参数速查

| 参数 | 说明 | 示例 |
|---|---|---|
| `path` | 文件或目录路径（md/txt/csv/xlsx/docx） | `./doc.md`、`./data.csv`、`./docs/` |
| `--attachment` | 附件文件路径，上传并插入到文档最前面 | `--attachment ./template.html` |
| `--import` / `-i` | 强制用 import_tasks 导入（仅支持 folder，不支持 wiki） | `--import` |
| `--target` | 目标：space、folder、wiki（通常不需要手动指定） | `--target wiki` |
| `--folder-token` | 文件夹 token（指定后自动设为 folder 模式） | `--folder-token LlqxfXXXXXX` |
| `--wiki-token` | 知识库 node_token（指定后自动设为 wiki 模式） | `--wiki-token FWn9wXXXXXX` |
| `--on-duplicate` | 重复处理：new（默认）、update、skip、ask | `--on-duplicate update` |

## Token 获取方式

| Token | 从浏览器地址栏获取 |
|---|---|
| folder_token | `https://xxx.feishu.cn/drive/folder/LlqxfXXXX` → `/folder/` 后面的部分 |
| node_token | `https://xxx.feishu.cn/wiki/FWn9wEcZ...` → `/wiki/` 后面的部分 |

## 首次使用配置

如果用户从未配置过飞书应用，引导用户参考 `references/setup-guide.md` 完成配置。

## references 目录说明

| 文件 | 内容 |
|---|---|
| `references/setup-guide.md` | 飞书应用创建、权限开通、.env 配置、协作者添加的完整指南 |
| `references/token-guide.md` | folder_token、node_token、space_id 等各类 token 的用途和获取方法 |
| `references/troubleshooting.md` | 按错误类型分类的常见问题排查，包括认证、权限、图片、文件附件等问题 |
