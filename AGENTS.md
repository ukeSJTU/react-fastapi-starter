# 项目定位

本项目维护一个有明确技术偏好、现代、精简且可用于生产项目的 React + FastAPI 全栈母模板。它首先服务于个人新项目，也应具备未来公开使用的质量。

本项目不是 SaaS 模板，也不是任何具体产品的示例应用。默认代码、命名、配置、文档和界面必须保持业务无关；不得预置用户、登录、商品、订单、后台管理等领域概念。未来可以在本项目之上派生 `react-fastapi-ai-starter` 等面向特定场景的模板。

只有跨业务且足够普遍的工程能力才应默认进入母模板。数据库技术栈是一个明确例外：本项目有意固定 PostgreSQL、SQLAlchemy、Alembic 和 psycopg，而不是保持存储中立。

## 本文的约束范围

本文同时描述当前代码的约束和项目的目标架构。某项能力尚未实现时，不得因为本文提到了目标状态，就在一个无关任务中擅自补齐整套模板；只在任务涉及对应区域时遵循这些已确定的选择。

开始修改前先检查当前实现、配置和 lockfile。lockfile 与实际配置是具体版本的事实来源；本文主要定义长期方向和边界。

# 仓库结构与边界

仓库采用协调式 monorepo：

- `frontend/` 与 `backend/` 分别拥有自己的依赖、构建、测试和部署边界。
- 根 `pyproject.toml` 与 `pnpm-workspace.yaml` 只协调 workspace；Python 与 pnpm 分别在根目录共享唯一的 lockfile 和开发环境。
- 根目录使用 Justfile 提供可选的统一快捷入口；Justfile 只编排 `pnpm`、`uv` 和 Docker Compose 等原生命令，不承载隐藏的业务逻辑。
- 不安装 `just` 时，开发者仍必须能直接使用各子项目的原生命令完成全部工作。
- 端到端测试放在根目录 `e2e/`，不归属于前端单元测试。

# 后端

## 固定技术选择

- Python 3.14，使用 `uv` workspace 管理环境和依赖，在仓库根目录提交 `.python-version` 与 `uv.lock`。
- FastAPI + Pydantic v2 + `pydantic-settings`。
- PostgreSQL + SQLAlchemy 2.x async + psycopg 3 + Alembic。
- 使用 structlog：本地输出易读日志，生产输出结构化 JSON，并绑定 request ID 和必要的请求上下文。
- Ruff 负责 lint、import 排序和格式化；mypy 负责严格类型检查。
- pytest、pytest-asyncio、HTTPX 和 Testcontainers 组成后端测试基础。

## 代码组织

后端使用轻量分层、按需抽象的结构，目标形态如下：

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── router.py
│   │   └── routes/
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   ├── schemas/
│   └── services/
├── alembic/
└── tests/
```

- 不默认建立 repository 层。只有查询复杂、需要隔离外部数据源或确有替换需求时才增加抽象。
- 提供 `DeclarativeBase`、稳定的约束命名规则、异步 session 管理和完整 Alembic 配置，但母模板不创建示例业务表。
- 不强制所有模型拥有统一的 `id`、时间戳或软删除字段。
- session dependency 只负责创建、注入、异常回滚和关闭，不隐式 commit。写操作在 service 中显式定义事务边界。
- AsyncSession 代码不得依赖会触发隐式 I/O 的 lazy loading；查询需要明确表达所需关系。
- migration 不得在 FastAPI startup hook 中自动执行。开发快捷命令可以在启动前迁移；生产迁移必须由部署步骤或一次性 job 显式执行。

## 配置

- 使用唯一、强类型的 Pydantic `Settings` 对象。
- 本地开发可以读取不提交的 `.env`，仓库提供 `.env.example`。
- 测试显式覆盖配置；生产配置和 secret 通过环境注入。
- 不使用 `development.py`、`production.py` 等多套 Python 配置模块。

## HTTP API 约定

- 业务 API 统一位于 `/api/v1`。
- `GET /health` 位于业务版本之外，同时检查应用和 PostgreSQL；依赖不可用时返回 `503`，响应不得泄露连接信息或内部异常。
- FastAPI 的 OpenAPI schema 是前后端接口契约的唯一事实来源。
- 每个接口必须声明明确、唯一且稳定的 `operationId`，使用简洁的 camelCase 动词命名。修改 operation ID 是前端破坏性变更。
- Python 标识符和数据库列使用 `snake_case`；OpenAPI、JSON 和 query 参数对外使用 `camelCase`。通过统一 Pydantic base schema 实现 alias，不要逐字段重复配置。
- 所有 datetime 必须带时区；数据库使用 `TIMESTAMPTZ`，后端内部按 UTC 处理，API 使用 RFC 3339，并把 UTC 表示为 `Z`。禁止 naive datetime 和本地时区写库。
- 成功响应不使用全局 `{ data, meta }` 信封。返回明确的响应模型；只有接口确实需要 metadata 时才定义具名响应类型。
- 母模板不预设分页协议。派生项目应根据访问模式统一选择 offset 或 cursor pagination。
- 统一错误响应标准及其第三方库尚未决定。没有明确任务时，不要自行引入 RFC 9457 实现或新的错误框架。
- CORS 保持满足本地联调和显式部署需求的简单配置，不为假设中的跨域场景设计复杂策略。

## API 文档

- 开发与测试环境使用 `scalar-fastapi`，在 `/docs` 提供唯一的 Scalar 文档 UI，在 `/openapi.json` 提供 schema。
- 禁用 FastAPI 自带的 Swagger UI 和 ReDoc。
- 生产环境完全不挂载 `/docs` 与 `/openapi.json`，也不提供重新开启它们的环境变量。
- 构建期 OpenAPI 导出通过 Python 命令直接读取应用 schema，不依赖已启动的 HTTP 服务。

## 后端测试

- 数据库集成测试必须使用真实 PostgreSQL，不使用 SQLite 模拟 PostgreSQL 行为。
- Testcontainers 启动临时数据库，并通过 Alembic migration 建立 schema；测试使用事务或 schema 隔离。
- 纯函数和无 I/O service 可以使用单元测试与 mock，但 mock 不能替代数据库集成测试。

# 前端

## 固定技术选择

- Node.js 24 LTS + pnpm；在根 `package.json` 中声明 `packageManager`，由根 `pnpm-workspace.yaml` 定义成员并提交根 `pnpm-lock.yaml`。
- React 19 + TypeScript 7 + Vite。
- Tailwind CSS 4 + shadcn/ui，使用 Base UI primitives 与 Lucide Icons。
- TanStack Router 使用 file-based routing。
- TanStack Query 管理服务端状态；不要用 `useEffect + fetch` 重建请求生命周期。
- TanStack Form + Zod 负责表单状态和客户端运行时校验。
- Orval 根据 OpenAPI 生成 Fetch 请求函数、TanStack Query hooks、TypeScript models 与 MSW handlers。
- Vitest + React Testing Library + MSW 负责单元和组件测试；Playwright 负责少量全栈 smoke tests。
- Oxfmt 负责格式化、import 排序和 Tailwind CSS class 排序；Oxlint + `oxlint-tsgolint` 负责 lint 和类型感知规则。不要引入 ESLint 或 Prettier。

## 源码组织

前端延续轻量分层、按需抽象：

```text
frontend/src/
├── app/
│   ├── providers.tsx
│   └── router.tsx
├── routes/
├── api/
│   ├── client.ts
│   └── generated/
├── components/
│   └── ui/
├── hooks/
├── lib/
├── test/
│   ├── setup.ts
│   └── render.tsx
├── main.tsx
└── index.css
```

- `routes/` 放置文件路由页面，`components/` 放置可复用 UI，`hooks/` 放置通用 hooks，`lib/` 放置纯工具和跨功能基础设施。
- 不预设 `features/`、Redux store 或复杂领域目录；真实需求出现后再增加。
- `src/test/` 只保存 Vitest setup 和共享测试工具。具体单元/组件测试使用 `*.test.ts(x)` 并与源码就近放置。
- shadcn 生成到仓库中的组件属于项目源码，可以修改；不要叠加 MUI、Ant Design 等整套组件库。
- 母模板首页暂时保持极简且业务无关，不要求承担健康检查或技术演示职责。

## TypeScript 与生成代码

- TypeScript 保持 strict，并启用 `noUncheckedIndexedAccess` 与 `exactOptionalPropertyTypes`。
- 保留独立的 `tsc -b` 作为权威类型检查；不要用 Oxlint 的实验性 type-check 替代编译器检查。
- OpenAPI schema 与 Orval 生成代码都提交到 Git。CI 必须重新生成并检查无漂移。
- 生成目录视为只读：不得手工编辑、lint 或格式化 Orval 与 TanStack Router 的生成产物。
- Orval 使用内置 Fetch，不设置 base URL 或 mutator。OpenAPI `paths` 是浏览器请求的完整 origin-relative path；`/health` 与 `/api/v1/*` 均由开发和生产反向代理原样转发，不添加、移除或重写 `/api`。
- 只支持仍在维护的现代 evergreen 浏览器；不为 IE 或旧浏览器默认加入 polyfill。

# 开发工作流与质量门禁

## Justfile

- 根 Justfile 提供 `setup`、`dev`、`check`、`test`、`generate`、`build` 等稳定快捷入口。
- recipe 应尽量只是组合已有的 `uv`、`pnpm` 和 Docker Compose 命令；子项目原生命令始终可独立运行。
- `just setup` 同步全部 uv/pnpm workspace，并使用根 uv 开发依赖执行 `prek install --prepare-hooks`。

## prek

prek 只管理适合每次 commit 执行的快速检查，并根据暂存文件运行：

- Python：Ruff。
- 前端：Oxfmt、Oxlint。
- 通用检查：JSON、TOML、YAML、尾随空格、文件末尾换行。

mypy、完整 TypeScript 类型检查、测试、构建、OpenAPI/Orval 漂移检查和 Playwright 不进入 pre-commit hook，由完整检查命令和 CI 承担。

## 测试与 CI

- 任何行为变更都要添加与风险相称的测试；修复 bug 时优先添加可复现失败的回归测试。
- 后端和前端生成覆盖率报告，但暂不设置全局覆盖率硬阈值。
- GitHub Actions 在 pull request 和主分支 push 时执行后端检查与测试、前端检查与测试、生成代码漂移检查、Playwright smoke tests，以及前后端生产镜像构建。
- CI 不负责部署或推送镜像；母模板不绑定云平台。
- 使用 Dependabot 管理 pnpm、uv、GitHub Actions 和 Docker 依赖更新。默认创建 PR，不自动合并。

# 本地运行与部署

- 默认本地开发方式是在 Docker Compose 中运行 PostgreSQL，在宿主机运行 Vite 与 FastAPI，以保留最佳热更新和调试体验。
- 同时维护独立的前端、后端生产 Dockerfile 和完整全栈 Compose，用于容器化验证与部署起点。
- 默认生产拓扑为同源：Caddy 服务前端静态文件、处理 SPA fallback，并将 `/health` 与 `/api/*` 原样反向代理到独立 FastAPI 容器。
- 前后端镜像保持独立；具体部署平台需要拆分域名时可以在派生项目中调整。

# 明确不默认包含的能力

除非具体任务明确要求，不要给母模板加入：

- 认证、授权、用户或组织模型。
- Redis、缓存、任务队列、定时任务或后台 worker。
- 对象存储、邮件、短信、支付、分析或第三方云 SDK。
- AI SDK、模型供应商、向量数据库或 prompt 示例。
- dashboard、登录页、后台管理页或任何业务 CRUD 示例。
- GraphQL、全局客户端状态库、repository 强制层或 Clean Architecture 样板代码。

引入新的生产依赖前，必须说明它解决的普遍问题以及为什么现有技术栈不足。不要为假设中的未来需求预建抽象。

# 文档、许可证与维护策略

- 代码标识符、代码注释、运行时错误信息、README 和公开文档统一使用英文；本 `AGENTS.md` 使用中文。
- 默认许可证为 MIT。
- `main` 始终代表当前推荐的新项目起点。母模板不承诺为已派生项目提供自动升级路径、向后兼容层或 migration 工具。
- 对现有首页、配置和 API 做修改时，继续使用通用命名，不把模板包装成虚构产品。

# 代理工作原则

- 严格控制任务范围，先复用现有依赖、组件、配置和模式。
- 使用 git conventional commit messages
- 不因本文描述了目标架构而在无关任务中进行全仓重构。
- 不手工修改 lockfile 或生成代码；使用对应包管理器或生成命令。
- 不在应用启动时执行有副作用的 schema migration、seed 或外部资源创建。
- 修改 API schema、operation ID 或 camelCase alias 时，必须同步导出 OpenAPI、运行 Orval，并更新前端调用与测试。
- 修改数据库模型时必须生成并检查 Alembic revision；不得用 `create_all` 替代 migration。
- 提交前运行与改动范围对应的最快检查；交付前运行完整、与风险相称的检查并报告结果。
- 工作区可能包含用户的未提交修改。保留无关改动，不覆盖、不回滚、不顺手格式化任务范围之外的文件。
