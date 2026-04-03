# 飞书文档写入工具

一站式飞书内容发布工具。支持将 Markdown 内容解析为飞书文档块（含标题、代码块、表格、图片自动上传等），也支持将任意格式文件（HTML、PDF、TXT 等）作为附件插入文档。可写入知识库、云文件夹或个人空间，单文件或批量均可。

## 功能特性

- 支持写入到我的空间、指定文件夹、知识库
- 自动上传本地图片和网络图片
- **支持上传文件附件（HTML、PDF 等），自动插入到文档最前面**
- 保留代码块语法高亮
- 支持表格解析与写入
- 支持单个文件或批量处理
- 重复文档检测与处理
- 支持配置默认知识库，简化命令
- token 过期自动刷新，支持线程安全
- 所有 HTTP 请求 30 秒超时，避免无限阻塞
- 批处理中单文件异常不会中断整体流程

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置凭证

复制 `.env.example` 为 `.env`，填入飞书应用凭证：

```dotenv
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# 可选：配置默认知识库（配置后可直接使用 --target wiki）
FEISHU_DEFAULT_WIKI_SPACE_ID=你的知识库space_id
FEISHU_DEFAULT_WIKI_NODE_TOKEN=你的知识库node_token
```

### 3. 获取飞书凭证

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 在「权限管理」中开通以下权限：
   - `docs:doc` - 云空间文件管理
   - `drive:drive` - 云空间文件访问
   - `wiki:wiki` - 知识库管理（如需写入知识库）

### 4. 将应用添加为协作者

**重要**：应用需要被添加为目标知识库/文件夹的协作者才能写入内容。不同目标的授权方式不同。

#### 4a. 知识库授权

知识库支持直接添加文档应用：

1. 打开目标知识库页面
2. 点击右上角 **「···」** 图标
3. 选择 **「更多」** > **「添加文档应用」**
4. 搜索并选择目标应用
5. 为应用分配 **「可编辑」** 权限
6. 点击 **「添加」**

#### 4b. 云文件夹授权（通过群组中介）

云空间文件夹**不支持**直接添加文档应用。需要通过群组作为中介，将应用机器人加入群，再把文件夹分享给该群：

1. 在飞书中**新建一个群组**（群名随意，如"文档权限授权群"）
2. 进入该群的设置 > **「机器人」** > **「添加机器人」**，搜索并添加你创建的应用对应的机器人
3. 打开飞书**云文档 > 我的空间**，找到目标文件夹
4. 点击文件夹右侧的 **「分享」** 按钮
5. 在协作者搜索框中搜索刚才新建的**群组名称**
6. 将该群组添加为协作者，分配 **「可编辑」** 权限

完成后，应用机器人通过"群成员"身份获得该文件夹的访问权限。

### 5. 使用

```bash
# 写入到我的空间（仅可通过链接访问，见下方说明）
python -m scripts.feishu_writer ./doc.md

# 写入到指定文件夹（推荐）
python -m scripts.feishu_writer ./doc.md --target folder --folder-token LlqxfXXXXXX

# 写入到知识库（推荐，使用 .env 中配置的默认知识库）
python -m scripts.feishu_writer ./doc.md --target wiki

# 写入到指定知识库
python -m scripts.feishu_writer ./doc.md --target wiki --wiki-token FWn9wEcZhixVLrk2z5scBx8DnTe

# 同时上传附件文件到文档最前面
python -m scripts.feishu_writer ./doc.md --target wiki --attachment ./template.html

# 批量处理目录
python -m scripts.feishu_writer ./docs/ --target folder --folder-token LlqxfXXXXXX
```

> **注意**：成功创建文档后，程序会输出文档链接，可直接点击访问。

## 命令参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `path` | - | MD 文件或目录路径 | 必填 |
| `--target` | `-t` | 目标位置 (space/folder/wiki) | space |
| `--attachment` | `-a` | 附件文件路径，上传并插入到文档最前面 | - |
| `--folder-token` | `-f` | 文件夹 token | - |
| `--wiki-token` | `-w` | 知识库 node_token（可在 .env 中配置默认值） | - |
| `--on-duplicate` | - | 重复处理 (ask/update/skip/new) | ask |
| `--no-check-duplicate` | - | 不检查重复 | false |

### target 模式说明

| 模式 | 文档存放位置 | 能否在飞书客户端浏览 | 说明 |
|------|-------------|-------------------|------|
| `space`（默认） | 应用自身的云空间 | 不能，仅可通过程序输出的链接访问 | 通过应用 API 创建的文档属于应用，不属于任何个人用户，飞书客户端没有入口浏览应用的云空间 |
| `folder` | 指定的云文档文件夹 | 能，在云文档对应文件夹中查看 | 需要通过 `--folder-token` 指定目标文件夹 |
| `wiki` | 指定的知识库 | 能，在知识库页面中查看 | 需要通过 `--wiki-token` 或环境变量配置知识库 |

> **建议**：实际使用时推荐 `folder` 或 `wiki` 模式，避免使用默认的 `space` 模式，否则文档只能通过链接访问，不方便管理。

## 如何获取 Token

### 文件夹 Token

1. 在飞书云文档中打开目标文件夹
2. 查看浏览器地址栏：`https://xxx.feishu.cn/drive/folder/LlqxfXXXXXX`
3. `/folder/` 后面的字符串即为 folder_token

### 知识库 Node Token

1. 打开目标知识库页面
2. 查看地址栏：`https://xxx.feishu.cn/wiki/FWn9wEcZhixVLrk2z5scBx8DnTe`
3. `/wiki/` 后面的字符串 `FWn9wEcZhixVLrk2z5scBx8DnTe` 即为 node_token

### 知识库 Space ID

Space ID 是知识库的内部标识（数字），可通过以下方式获取：
- 程序会自动通过 node_token 查询 space_id
- 也可手动配置在 `.env` 的 `FEISHU_DEFAULT_WIKI_SPACE_ID` 中

## 支持的 Markdown 格式

| 格式 | 示例 | 支持 |
|------|------|------|
| 标题 | `# H1` ~ `###### H6` | ✓ |
| 加粗 | `**text**` | ✓ |
| 斜体 | `*text*` | ✓ |
| 行内代码 | `` `code` `` | ✓ |
| 代码块 | ` ```python ` | ✓ |
| 无序列表 | `- item` | ✓ |
| 有序列表 | `1. item` | ✓ |
| 引用 | `> quote` | ✓ |
| 链接 | `[text](url)` | ✓ |
| 图片 | `![alt](path)` | ✓ |
| 分割线 | `---` | ✓ |
| 表格 | `| A | B |` | ✓ |

## 文件附件上传

使用 `--attachment` 参数可将本地文件作为附件插入到文档内容的最前面：

```bash
python -m scripts.feishu_writer ./article.md --target wiki --attachment ./template.html
```

附件会以可下载的文件块形式出现在文档顶部，用户点击即可下载原始文件。

**默认行为**：
- `.md` 文件 → 解析内容写入飞书文档（主流程）
- 其他所有文件类型（TXT、HTML、PDF、DOCX、ZIP 等）→ 上传为附件

**附件支持格式**：HTML、PDF、Word、Excel、PPT、TXT、ZIP 等常见格式均可上传，飞书会按文件类型显示对应图标。

## 作为 Claude Code 技能使用

在 Claude Code 中直接使用：

```
/feishu-write ./doc.md --target folder --folder-token LlqxfXXXXXX
```

## 常见问题

### Q: 文档创建成功但在飞书里找不到

使用默认的 `--target space` 模式时，文档会创建在**应用自身的云空间**中，这个空间在飞书客户端上没有入口可以直接浏览，只能通过程序输出的链接访问。

建议改用 `--target wiki` 或 `--target folder` 模式，将文档写入可见的知识库或文件夹中。

### Q: 提示「获取 token 失败」

检查 `.env` 中的 App ID 和 App Secret 是否正确。

### Q: 提示「权限不足」或「permission denied」

1. 确认应用权限已在飞书开放平台开通并发布
2. **知识库**：确认应用已通过「添加文档应用」被添加为知识库协作者（见上方「4a. 知识库授权」）
3. **云文件夹**：确认已通过群组中介方式为应用授权（见上方「4b. 云文件夹授权」）
4. 确认应用的协作者权限为「可编辑」或「可管理」

### Q: 提示「node permission denied, tenant needs edit permission」

应用没有目标知识库的编辑权限。请按照上方步骤将应用添加为知识库的协作者，并授予「可编辑」权限。

### Q: 图片上传失败

- 确保图片路径正确
- 检查图片格式是否支持（jpg/png/gif/webp/bmp/tiff）
- 确认应用有云空间写入权限（`drive:drive`）
- 图片大小不超过 20MB

### Q: 网络图片无法显示

工具会自动下载网络图片到本地临时目录后再上传到飞书。如果下载失败，请检查：
- 图片 URL 是否可访问
- 是否有网络代理或防火墙限制
- 图片 URL 是否需要特定的认证头

### Q: block_type 相关错误

飞书 API 要求 block_type 为数字类型。本工具已正确处理，如遇到此问题请更新到最新版本。

## 开发难点与重点

### 飞书 docx 文档图片上传流程

飞书新版文档（docx）的图片上传与旧版文档不同，需要**三步操作**才能正确显示图片：

#### 步骤 1：创建空图片块

```bash
POST /docx/v1/documents/{document_id}/blocks/{block_id}/children
```

```json
{
  "children": [
    {
      "block_type": 27,
      "image": {}
    }
  ]
}
```

返回值中包含新创建的图片块 `block_id`。

#### 步骤 2：上传图片文件

```bash
POST /drive/v1/medias/upload_all
```

| 参数 | 值 | 说明 |
|------|-----|------|
| `file` | 二进制文件 | 图片文件内容 |
| `file_name` | 文件名 | 如 `cover.png` |
| `parent_type` | `docx_image` | **必须是 docx_image** |
| `parent_node` | 图片块 ID | 步骤 1 返回的 block_id |
| `size` | 文件大小 | 字节数 |

返回值中包含 `file_token`。

#### 步骤 3：更新图片块 token（关键！）

```bash
PATCH /docx/v1/documents/{document_id}/blocks/{block_id}
```

```json
{
  "replace_image": {
    "token": "上一步返回的 file_token"
  }
}
```

**重点**：必须使用 `replace_image` 字段，而不是 `update_image` 或 `image`。

#### 常见错误

| 错误码 | 错误信息 | 原因 |
|--------|----------|------|
| 403 / 1061004 | forbidden | `parent_type` 不正确或缺少权限 |
| 400 / 1061044 | parent node not exist | `parent_node` 无效或为空 |
| 400 / 1770001 | invalid param | 更新图片块时使用了错误的字段名 |

#### 为什么需要三步？

1. **上传图片不会自动关联到图片块** - 即使 `parent_node` 正确，上传后图片块的 `token` 仍为空
2. **更新块 API 只支持文本元素** - 标准的 `update_text_elements` 不支持图片
3. **必须使用 `replace_image`** - 这是飞书专门为图片块设计的更新字段

这个三步流程是飞书 docx 文档 API 的设计特点，官方文档中没有明确说明，需要通过实践摸索。

### 飞书 docx 文档文件附件上传流程

文件附件块（block_type 23）的创建与图片类似，同样是**三步操作**：

#### 步骤 1：创建空文件块

```bash
POST /docx/v1/documents/{document_id}/blocks/{block_id}/children
```

```json
{
  "children": [{ "block_type": 23, "file": {} }],
  "index": 0
}
```

**注意**：`file` 必须为空 `{}`，**不能传 `name` 或 `file_token`**，否则返回 1770001 错误。

API 会返回两层结构：
- 外层：block_type **33**（View 容器，程序直接返回这一层）
- 内层：block_type **23**（真正的文件块，在 `children[0].children[0]` 里）

取内层的 `block_id` 用于后续步骤。

#### 步骤 2：上传文件

```bash
POST /drive/v1/medias/upload_all
```

| 参数 | 值 | 说明 |
|------|-----|------|
| `file` | 二进制文件 | 文件内容 |
| `file_name` | 文件名 | 如 `template.html` |
| `parent_type` | `docx_file` | **必须是 docx_file** |
| `parent_node` | 内层文件块 ID | 步骤 1 中取到的内层 block_id |
| `size` | 文件大小 | 字节数 |

**必须使用 `MultipartEncoder`**（`requests_toolbelt`），使用 `requests` 原生 multipart 会导致文件不完整。

返回值中包含 `file_token`。

#### 步骤 3：绑定 file_token 到文件块

```bash
PATCH /docx/v1/documents/{document_id}/blocks/{inner_block_id}
```

```json
{
  "replace_file": {
    "token": "步骤 2 返回的 file_token"
  }
}
```

完成后文件名和 token 自动填充，附件可正常下载。

#### 文件附件常见错误

| 错误码 | 错误信息 | 原因 |
|--------|----------|------|
| 400 / 1770001 | invalid param | 创建块时 `file` 对象中传了 `name` 字段 |
| 附件显示"上传失败" | - | 上传时 `parent_node` 用了文档 ID 而非内层 block_id |
| 附件显示"上传失败" | - | 缺少第三步 PATCH（file.token 仍为空） |

### 飞书 docx 文档表格创建流程

飞书表格的创建和填充也需要特殊处理：

#### 步骤 1：创建表格块

```bash
POST /docx/v1/documents/{document_id}/blocks/{block_id}/children
```

```json
{
  "children": [
    {
      "block_type": 31,
      "table": {
        "property": {
          "row_size": 4,
          "column_size": 3
        }
      }
    }
  ]
}
```

返回值中包含表格块 `block_id` 和所有单元格的 `block_id`。

#### 步骤 2：获取单元格列表

```bash
GET /docx/v1/documents/{document_id}/blocks/{table_block_id}/children
```

**重点**：表格的子块直接就是单元格（block_type=32），不是行！单元格按**行优先顺序**排列：

```
4行3列的表格，单元格顺序为：
[0,0] [0,1] [0,2] [1,0] [1,1] [1,2] [2,0] [2,1] [2,2] [3,0] [3,1] [3,2]
```

#### 步骤 3：填充单元格内容

```bash
POST /docx/v1/documents/{document_id}/blocks/{cell_block_id}/children
```

```json
{
  "children": [
    {
      "block_type": 2,
      "text": {
        "elements": [
          {
            "text_run": {
              "content": "单元格内容"
            }
          }
        ]
      }
    }
  ]
}
```

#### 常见错误

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 只有第一列有内容 | 误以为表格子块是行 | 直接遍历所有单元格，按行优先顺序填充 |
| 部分单元格为空 | API 调用过快被限流 | 每次填充后添加 100ms 延时 |

## 许可证

MIT License
