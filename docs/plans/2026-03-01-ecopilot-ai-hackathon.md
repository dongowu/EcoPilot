# EcoPilot AI 黑客松设计方案

## 项目概述

- **项目名**: EcoPilot AI
- **目标**: GitLab CI 成本优化 + AI 一键修复 MR
- **团队**: 1-2 人
- **展示方式**: 视频演示 (3 分钟)

## 问题陈述

开发团队普遍面临 CI/CD 成本居高不下的问题。尽管存在优化空间，但手动优化费时费力，缺乏动力。EcoPilot AI 通过自动化检测 + AI 修复，将成本优化变成 MR 审批的副产品。

## 核心功能

### 已有功能 (继承)
1. MR Webhook 接收 (`opened`/`reopened`/`updated`)
2. 5 种 CI 反模式检测规则
3. 成本/碳排估算 (USD, kgCO2e)
4. MR Comment 优化建议
5. 自动标签 + Issue 创建

### 新增功能 (MVP)
1. **AI 修复代码生成** - 调用 LLM 基于检测结果生成修复方案
2. **自动创建修复 MR** - 将 AI 生成的修复提交为新的 MR

## 技术架构

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ GitLab MR   │────▶│  EcoPilot    │────▶│  Claude API │
│  Webhook    │     │  分析引擎    │     │  生成修复   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────┐     ┌─────────────┐
                    │ MR Comment   │◀────│  修复 MR    │
                    │ 优化建议     │     │  (自动创建) │
                    └──────────────┘     └─────────────┘
```

## 数据流

1. MR 事件触发 Webhook
2. 解析 `.gitlab-ci.yml`，提取 Jobs
3. 运行 5 种检测规则，生成 Finding 列表
4. 调用 LLM (Claude) 生成修复代码
5. 将修复提交为新 MR，关联原 MR
6. 在原 MR 评论区贴优化建议 + 修复 MR 链接

## AI 修复 Prompt 设计

```python
SYSTEM_PROMPT = """你是一个 GitLab CI 优化专家。
根据检测到的问题，生成最优的 .gitlab-ci.yml 修复代码。
只返回修复后的 YAML，不要解释。"""

USER_PROMPT = """
原始 .gitlab-ci.yml:
{yaml_content}

检测到的问题:
{findings}

请生成修复后的 .gitlab-ci.yml。
"""
```

## 关键实现

### 1. AI 修复服务
```python
class AIRepairService:
    def generate_fix(self, ci_yaml: str, findings: list[Finding]) -> str:
        # 调用 Claude API 生成修复代码
        
    def create_fix_mr(self, project_id: int, source_branch: str, 
                      target_branch: str, fix_content: str) -> dict:
        # 创建新的修复 MR
```

### 2. 修复 MR 创建
- 基于原 MR 的 `source_branch` 创建新分支
- 提交修复后的 `.gitlab-ci.yml`
- 创建 MR 指向 `target_branch`
- 返回修复 MR 的 Web URL

## 48h 时间线

| 时间段 | 任务 |
|--------|------|
| 0-2h | 确认选题，整理现有代码 |
| 2-8h | 实现 AI 修复代码生成 |
| 8-12h | 实现自动创建修复 MR |
| 12-20h | 测试、边界处理、稳定性 |
| 20-24h | 准备演示环境、测试数据 |
| 24-28h | 写演讲稿、画架构图 |
| 28-32h | 录制视频 |
| 32-36h | 剪辑、加字幕 |
| 36-48h | 彩排、备份 |

## 验收标准

- [ ] MR webhook 触发后 30s 内完成分析
- [ ] AI 修复 MR 成功创建并可合并
- [ ] 成本节省数据正确计算
- [ ] 3 分钟视频演示流畅

## 风险与对策

| 风险 | 对策 |
|------|------|
| LLM API 调用失败 | 降级到纯规则模式，只贴建议不自动修复 |
| 修复 MR 冲突 | 检测冲突并提示手动解决 |
| 演示环境不稳定 | 准备 2 个演示账号 |
