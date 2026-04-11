# 飞书文档写入工具

## 项目概述

这是一个 Claude Code 技能，用于将本地 Markdown 文件写入飞书文档。

## 目录结构

```
feishu-document-writing/
├── CLAUDE.md           # 项目说明（本文件）
├── README.md           # 用户使用文档
├── skill.md            # 技能定义文件
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量示例
├── data/               # 测试数据目录
└── scripts/            # 代码目录
    ├── __init__.py     # 模块导出
    ├── feishu_writer.py # 命令行入口
    ├── writer.py       # 主入口类
    ├── auth.py         # 认证模块
    ├── uploader.py     # 图片上传模块
    ├── parser.py       # Markdown 解析模块
    └── doc_writer.py   # 文档写入模块
```

## 核心模块

### scripts/

| 文件 | 类名 | 职责 |
|------|------|------|
| `auth.py` | `FeishuAuth` | 管理飞书 API 认证，获取 tenant_access_token，支持 token 过期自动刷新和线程安全 |
| `uploader.py` | `FeishuImageUploader` | 上传本地/网络图片、文件附件、import_tasks 专用上传，返回 file_token |
| `parser.py` | `MarkdownParser` | 解析 MD 为飞书 Block 格式，处理内联样式 |
| `file_parser.py` | `FileParser` | 解析 txt/csv/xlsx/docx 为飞书 Block 格式，接口与 MarkdownParser 兼容 |
| `doc_writer.py` | `FeishuDocWriter` | 创建/更新文档，管理 Block 内容，写入知识库，文件附件块操作，import_tasks 导入 |
| `writer.py` | `FeishuWriter` | 主入口类，整合所有功能 |
| `feishu_writer.py` | - | 命令行入口 |

## 飞书 API 端点

- 认证：`POST /auth/v3/tenant_access_token/internal`
- 上传图片/文件：`POST /drive/v1/medias/upload_all`
- 创建文档：`POST /docx/v1/documents`
- 写入内容：`POST /docx/v1/documents/{doc_id}/blocks/{block_id}/children`
- 更新块内容：`PATCH /docx/v1/documents/{doc_id}/blocks/{block_id}`
- 在知识库创建文档：`POST /wiki/v2/spaces/{space_id}/nodes`
- 获取知识库节点信息：`GET /wiki/v2/spaces/get_node?token={node_token}`
- 创建导入任务：`POST /drive/v1/import_tasks`
- 查询导入任务：`GET /drive/v1/import_tasks/{ticket}`

## 飞书 Block 类型映射

| block_type | 类型 |
|------------|------|
| 2 | text（文本） |
| 3-11 | heading1-heading9（标题） |
| 12 | bullet（无序列表） |
| 13 | ordered（有序列表） |
| 14 | code（代码块） |
| 15 | quote（引用） |
| 22 | divider（分割线） |
| 23 | file（文件附件，内层块） |
| 27 | image（图片） |
| 31 | table（表格） |
| 32 | table_cell（表格单元格，自动生成） |
| 33 | view（文件附件外层容器，自动生成） |

## 开发注意事项

1. 飞书 API 每次最多写入 50 个 Block，代码中已做分批处理
2. 图片必须先上传获取 token 才能在文档中使用
3. 代码块语言需要映射为飞书的语言代码（数字）
4. **block_type 必须是数字类型**，不能是字符串
5. 文件读写统一使用 `encoding='utf-8'`
6. **知识库文档需要直接在知识库中创建**，而不是先创建再移动
7. **应用必须被添加为目标知识库/文件夹的协作者**才有写入权限
8. **表格单元格按行优先顺序排列**，不是嵌套的行-单元格结构
9. **所有 HTTP 请求均设置 30 秒超时**，避免无限阻塞
10. **token 支持过期自动刷新**，距离过期不足 60 秒时自动重新获取
11. **token 操作线程安全**，使用 threading.Lock 保护
12. **文件夹列表支持分页**，通过 page_token 遍历所有页面
13. **删除块时检查响应**，失败时记录日志并返回 False
14. **批处理中单文件异常不会中断**，每个文件独立 try/except 保护
15. **默认 space 模式文档不可见**，文档创建在应用自身云空间，飞书客户端无法浏览，只能通过链接访问；推荐使用 wiki 或 folder 模式
16. **创建成功后输出文档链接**，wiki 模式输出 `/wiki/{node_token}`，其他模式输出 `/docx/{document_id}`
17. **文件附件上传是三步操作**：① 创建空文件块（`file: {}`，不能有 name/token 字段）→ 取内层 block_id；② 上传文件，`parent_node = 内层 block_id`，必须用 `MultipartEncoder`；③ PATCH 内层块 `replace_file: {token: file_token}`（详见 `references/troubleshooting.md`）
18. **文件附件块的结构**：block_type 23（文件内容）被自动包裹在 block_type 33（View 容器）中，创建时只需传 23，API 返回的是 33，内层 23 的 block_id 在 `children[0].children[0]` 中
19. **非 MD 文件解析**：txt/csv/xlsx/docx 由 `FileParser`（`file_parser.py`）解析为飞书 blocks，与 `MarkdownParser` 接口一致（`blocks`、`pending_images`、`pending_tables`），直接复用 `_write_content_with_images` 写入
20. **import_tasks 仅支持 folder**：`/drive/v1/import_tasks` 的 `mount_type` 只有 1（folder）和 2（space），不支持 wiki；需要写入 wiki 时必须用 block 方式解析写入
21. **import_tasks 三步流程**：① `upload_for_import()`（`parent_type="ccm_import_open"`，`extra={"obj_type":..., "file_extension":...}`）→ file_token；② `create_import_task()` → ticket；③ `poll_import_task()` 轮询 `job_status`（0=成功，1/2=处理中）

## 知识库权限配置

应用需要被添加为知识库协作者才能写入：

1. 打开知识库页面
2. 点击右上角 **「···」** > **「更多」** > **「添加文档应用」**
3. 搜索应用并授予 **「可编辑」** 权限

## 云文件夹权限配置

云空间文件夹不支持直接添加文档应用，需通过群组中介方式授权：

1. 新建一个飞书群组（专门用于授权）
2. 在群设置中添加应用对应的机器人
3. 将目标文件夹分享给该群组，授予 **「可编辑」** 权限
4. 应用机器人通过"群成员"身份获得文件夹访问权限

## 环境变量配置

```dotenv
FEISHU_APP_ID=应用ID
FEISHU_APP_SECRET=应用密钥
FEISHU_DEFAULT_WIKI_SPACE_ID=默认知识库space_id（可选）
FEISHU_DEFAULT_WIKI_NODE_TOKEN=默认知识库node_token（可选）
```

## 关键文件路径速查

| 功能 | 路径 |
|------|------|
| 命令行入口 | `scripts/feishu_writer.py` |
| 主入口类 | `scripts/writer.py` |
| MD 解析器 | `scripts/parser.py` |
| 非 MD 文件解析器 | `scripts/file_parser.py`（新增，解析 txt/csv/xlsx/docx） |
| 图片/文件上传 | `scripts/uploader.py` |
| 文档写入 / 导入任务 | `scripts/doc_writer.py` |
| 认证模块 | `scripts/auth.py` |
| 测试文件 | `data/test-import.{txt,csv,xlsx,docx}` |
| 生成测试文件脚本 | `data/create_test_files.py` |

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入凭证

# 测试运行（写入到默认知识库）
python -m scripts.feishu_writer ./data/test.md --target wiki
```

## 技能调用

通过 `/feishu-write` 命令调用，详见 skill.md。
