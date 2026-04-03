# 常见问题排查

本文档按错误类型分类，帮助快速定位和解决飞书文档写入过程中的问题。

## 文档相关

### 文档创建成功但在飞书里找不到

**原因**：使用默认的 `--target space` 模式时，文档会创建在应用自身的云空间中。这个空间在飞书客户端上没有入口可以直接浏览，属于应用而不是任何个人用户。

**解决方案**：
1. 通过程序输出的文档链接直接访问（格式：`https://feishu.cn/docx/{document_id}`）
2. 改用 `--target wiki` 或 `--target folder` 模式，将文档写入可见的知识库或文件夹中
3. 建议在 `.env` 中配置 `FEISHU_DEFAULT_WIKI_NODE_TOKEN` 或 `FEISHU_DEFAULT_FOLDER_TOKEN`，避免使用 space 模式

## 认证相关

### "获取 token 失败"

**原因**：App ID 或 App Secret 配置错误。

**解决方案**：
1. 检查 `.env` 文件中的 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 是否正确
2. 确认没有多余的空格或换行符
3. 确认凭证来自 [飞书开放平台](https://open.feishu.cn/app) 应用详情页的「凭证与基础信息」

### "invalid app_id or app_secret"

**原因**：飞书 API 返回的认证错误，凭证无效。

**解决方案**：
1. 重新复制 App ID 和 App Secret（注意不要复制到多余字符）
2. 确认应用未被停用或删除
3. 确认 `.env` 文件位于项目根目录下

## 权限相关

### "permission denied" 或 HTTP 403

**原因**：应用未开通必需权限，或权限未发布生效，或未被添加为协作者。

**解决方案**：
1. 在飞书开放平台进入应用 > **「权限管理」**
2. 确认以下权限已开通：
   - `docx:document`（云空间文档）
   - `drive:drive`（云空间文件）
   - `drive:drive:readonly`（云空间文件只读）
   - `wiki:wiki`（知识库，写入知识库时需要）
3. **重要**：开通权限后需要 **创建新版本并发布**，权限才会生效
4. 如果已发布但仍报错，根据目标类型检查协作者权限：
   - **知识库**：通过「添加文档应用」直接添加应用为协作者
   - **云文件夹**：需通过群组中介方式授权——新建群组 → 添加应用机器人到群 → 将文件夹分享给该群组（详见 `setup-guide.md` 第 4.1 节）

### "node permission denied, tenant needs edit permission"

**原因**：应用没有目标知识库的编辑权限。

**解决方案**：
1. 打开目标知识库页面
2. 点击右上角 **「···」** > **「更多」** > **「添加文档应用」**
3. 搜索你的应用并授予 **「可编辑」** 权限
4. 如果看不到「添加文档应用」选项，说明你不是知识库的管理员，请联系管理员操作

### "forbidden" (HTTP 403 / 错误码 1061004)

**原因**：通常是图片上传时 `parent_type` 不正确或缺少云空间写入权限。

**解决方案**：
1. 确认 `drive:drive` 权限已开通并发布
2. 确认应用已被添加为目标文档的协作者
3. 如果是图片上传问题，这是代码内部处理，确保使用最新版本

## Token 相关

### "parent node not exist"（错误码 1061044）

**原因**：传入的 token 无效，或对应的文件夹/文档不存在。

**解决方案**：
1. 重新从浏览器地址栏获取 token（参见 `token-guide.md`）
2. 确认目标文件夹或知识库节点未被删除
3. 检查 token 格式：
   - folder_token 为字母数字混合字符串（从浏览器地址栏 `/drive/folder/` 后获取）
   - node_token 为字母数字混合字符串

### "invalid param"（错误码 1770001）

**原因**：API 参数格式错误。

**解决方案**：
1. 检查传入的 token 是否包含多余字符（空格、换行等）
2. 确认 `.env` 中的 token 值没有被引号包裹（不需要引号）

### "未配置知识库 space_id"

**原因**：写入知识库时未提供任何知识库标识。

**解决方案**（任选其一）：
1. 使用 `--wiki-token` 参数指定目标知识库节点
2. 在 `.env` 中配置 `FEISHU_DEFAULT_WIKI_NODE_TOKEN`
3. 在 `.env` 中配置 `FEISHU_DEFAULT_WIKI_SPACE_ID`

## 图片上传相关

### 图片上传失败

**可能原因和解决方案**：

| 可能原因 | 解决方案 |
|---------|---------|
| 图片路径错误 | 确认图片文件存在，路径相对于 MD 文件所在目录 |
| 图片格式不支持 | 支持的格式：jpg、jpeg、png、gif、webp、bmp、svg |
| 图片体积过大 | 飞书限制单张图片不超过 20MB |
| 缺少 `drive:drive` 权限 | 在飞书开放平台开通并发布 |

### 网络图片下载失败

**可能原因和解决方案**：

| 可能原因 | 解决方案 |
|---------|---------|
| 图片 URL 不可访问 | 在浏览器中测试 URL 是否可以打开 |
| 网络代理/防火墙限制 | 检查网络环境，确认可以访问目标域名 |
| 图片 URL 需要认证 | 工具不支持需要登录才能访问的图片，请先手动下载到本地 |
| URL 格式异常 | 确认 URL 以 `http://` 或 `https://` 开头 |

## API 调用相关

### 请求超时

**原因**：网络连接不稳定或飞书 API 响应慢。

**解决方案**：
1. 检查网络连接是否正常
2. 确认是否在企业网络环境中，可能需要配置代理
3. 程序已设置 30 秒超时，可稍后重试

### 部分表格单元格为空

**原因**：API 调用过快被限流。

**解决方案**：
- 程序已内置 100ms 延时机制
- 如果仍有问题，可能是表格过大，建议拆分文档重试

### "block count exceeds limit"

**原因**：单次 API 调用写入的 Block 数量超过 50 个限制。

**解决方案**：
- 程序已内置分批处理（每次最多 50 个 Block）
- 如果仍遇到此错误，请确保使用最新版本

## 文件附件上传相关

### 文档中显示"视频或文件上传失败，无法查看"

**根本原因**：文件附件块（block_type 23）的创建是一个**三步流程**，缺少任何一步都会导致附件无法正常显示。

**正确的三步流程**：

```
步骤1：创建空文件块 → 拿到内层 block_id
步骤2：上传文件，parent_node = 内层 block_id → 拿到 file_token
步骤3：PATCH 内层块，replace_file: {token: file_token} → 文件正确绑定
```

**详细说明**：

当你调用创建子块接口 `POST /docx/v1/documents/{doc_id}/blocks/{doc_id}/children` 时，传入 `{"block_type": 23, "file": {}}` 会生成两层结构：
- 外层：block_type **33**（View 容器块，程序返回的就是这一层）
- 内层：block_type **23**（真正的文件块，在外层的 `children[0]` 里）

内层块初始状态 `file.token` 为空，需要先上传文件、再 PATCH 才能填充。

**Python 示例**：

```python
import requests
from requests_toolbelt import MultipartEncoder

# 步骤1：创建空文件块（注意：file 必须为空 {}，不能传 name 或 file_token）
resp = requests.post(
    f'{BASE_URL}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children',
    headers=json_headers,
    json={'children': [{'block_type': 23, 'file': {}}], 'index': 0}
)
inner_block_id = resp.json()['data']['children'][0]['children'][0]

# 步骤2：上传文件，parent_node 必须是内层 block_id（不是文档 ID）
with open(file_path, 'rb') as f:
    form = MultipartEncoder({
        'file_name': file_name,
        'parent_type': 'docx_file',
        'parent_node': inner_block_id,   # ← 关键：用内层块 ID
        'size': str(file_size),
        'file': (file_name, f, 'application/octet-stream')
    })
    up_resp = requests.post(
        f'{BASE_URL}/drive/v1/medias/upload_all',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': form.content_type},
        data=form
    )
file_token = up_resp.json()['data']['file_token']

# 步骤3：PATCH 内层块，绑定文件
requests.patch(
    f'{BASE_URL}/docx/v1/documents/{doc_id}/blocks/{inner_block_id}',
    headers=json_headers,
    json={'replace_file': {'token': file_token}}
)
```

---

### "invalid param"（错误码 1770001）出现在创建文件块时

**原因**：创建文件块时在 `file` 对象中传入了 `name` 字段。飞书 API **不支持**在创建阶段通过 `name` 指定文件名，`name` 会在步骤3 PATCH 时由 `replace_file` 自动从上传文件中读取。

**错误示例**：
```json
// ❌ 会导致 1770001
{"block_type": 23, "file": {"file_token": "xxx", "name": "test.html"}}

// ❌ 也会导致 1770001（即使 name 为空字符串）
{"block_type": 23, "file": {"file_token": "xxx", "name": ""}}
```

**正确示例**：
```json
// ✅ 创建时 file 必须为空对象
{"block_type": 23, "file": {}}
```

---

### 上传文件后附件仍显示失败（file.token 为空）

**原因**：上传时 `parent_node` 使用了**文档 ID** 而不是**内层文件块的 block_id**。

| 上传方式 | 结果 |
|---------|------|
| `parent_node = doc_id` | 上传成功（有 file_token），但块的 token 不会自动填充 |
| `parent_node = 内层 block_id` | 上传成功，file_token 可正确通过 PATCH 绑定到块 |

两种方式上传 API 都返回 code=0，区别在于后续 PATCH 是否能正常工作。

---

### 上传接口必须使用 MultipartEncoder

**原因**：飞书 `drive/v1/medias/upload_all` 对 multipart/form-data 的格式要求较严格，使用 `requests` 原生的 `files=` 参数方式可能导致上传成功但内容不完整（文件可下载但打开后为空）。

**正确依赖**：
```bash
pip install requests-toolbelt
```

```python
from requests_toolbelt import MultipartEncoder

form = MultipartEncoder({
    'file_name': 'test.html',
    'parent_type': 'docx_file',
    'parent_node': inner_block_id,
    'size': str(file_size),
    'file': ('test.html', open(file_path, 'rb'), 'application/octet-stream')
})
headers['Content-Type'] = form.content_type
```
