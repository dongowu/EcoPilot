# EcoPilot AI 修复功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现 AI 自动修复 GitLab CI 配置功能，检测问题后自动生成修复代码并创建修复 MR

**Architecture:** 在现有 Reporter 基础上新增 `AIRepairService`，复用现有 LLM 客户端，扩展 GitLabClient 支持分支和文件操作

**Tech Stack:** Python, httpx, Anthropic API, GitLab API

---

## Task 1: 扩展 GitLabClient 支持分支和文件操作

**Files:**
- Modify: `ecopilot/gitlab_client.py:67-EOF`

**Step 1: 添加创建分支方法**

```python
def create_branch(self, project_id: int, branch: str, ref: str) -> dict:
    """Create a new branch from ref (commit SHA or branch name)."""
    path = f"/projects/{project_id}/repository/branches"
    data = self._request("POST", path, json={"branch": branch, "ref": ref})
    return dict(data) if isinstance(data, dict) else {}
```

**Step 2: 添加提交文件方法**

```python
def commit_file(self, project_id: int, branch: str, file_path: str, 
                content: str, commit_message: str) -> dict:
    """Create or update a file in repository."""
    import base64
    path = f"/projects/{project_id}/repository/files/{quote_plus(file_path)}"
    data = self._request("PUT", path, json={
        "branch": branch,
        "content": base64.b64encode(content.encode()).decode(),
        "commit_message": commit_message,
    })
    return dict(data) if isinstance(data, dict) else {}
```

**Step 3: 添加创建 MR 方法**

```python
def create_mr(self, project_id: int, source_branch: str, target_branch: str,
              title: str, description: str) -> dict:
    """Create a merge request."""
    path = f"/projects/{project_id}/merge_requests"
    data = self._request("POST", path, json={
        "source_branch": source_branch,
        "target_branch": target_branch,
        "title": title,
        "description": description,
    })
    return dict(data) if isinstance(data, dict) else {}
```

**Step 4: 验证代码无语法错误**

Run: `python -c "from ecopilot.gitlab_client import GitLabClient; print('OK')"`
Expected: OK

---

## Task 2: 创建 AI 修复服务

**Files:**
- Create: `ecopilot/repair.py`
- Test: `tests/test_repair.py`

**Step 1: 编写测试文件**

```python
import pytest
from ecopilot.repair import build_repair_prompt, AIRepairService
from ecopilot.models import Finding

def test_build_repair_prompt():
    yaml_content = "stages: [test]"
    findings = [
        Finding(
            rule_id="missing_cache",
            title="Cache not configured",
            severity="high",
            evidence={"jobs": ["test"]},
            recommendation="Add cache",
            savings_ratio=0.15,
        )
    ]
    prompt = build_repair_prompt(yaml_content, findings)
    assert "stages: [test]" in prompt
    assert "missing_cache" in prompt

def test_air_repair_service_init():
    service = AIRepairService(llm_client=None)
    assert service._llm_client is None
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_repair.py -v`
Expected: FAIL - module not found

**Step 3: 创建 repair.py**

```python
from __future__ import annotations

from ecopilot.models import Finding


def build_repair_prompt(ci_yaml: str, findings: list[Finding]) -> str:
    """Build prompt for AI to generate CI fix."""
    lines = [
        "You are a GitLab CI optimization expert.",
        "Generate optimized .gitlab-ci.yml based on findings.",
        "Only return the YAML content, no explanations.",
        "",
        "Original .gitlab-ci.yml:",
        ci_yaml,
        "",
        "Findings to fix:",
    ]
    for f in findings:
        lines.append(f"- {f.rule_id}: {f.title} ({f.severity})")
        lines.append(f"  Recommendation: {f.recommendation}")
    lines.append("")
    lines.append("Return optimized .gitlab-ci.yml:")
    return "\n".join(lines)


class AIRepairService:
    def __init__(self, llm_client: object | None = None):
        self._llm_client = llm_client

    def generate_fix(self, ci_yaml: str, findings: list[Finding]) -> str | None:
        """Generate fixed CI YAML using LLM."""
        if not findings:
            return None
        
        prompt = build_repair_prompt(ci_yaml, findings)
        
        if self._llm_client is None:
            return None
        
        try:
            response = self._llm_client.generate(prompt)
            if isinstance(response, str) and response.strip():
                return response.strip()
        except Exception:
            pass
        return None

    def create_fix_mr(
        self,
        gitlab_client: object,
        project_id: int,
        source_branch: str,
        target_branch: str,
        fix_content: str,
        original_mr_iid: int,
    ) -> dict | None:
        """Create MR with fixed CI config."""
        fix_branch = f"ecopilot-fix-mr-{original_mr_iid}"
        
        try:
            gitlab_client.create_branch(project_id, fix_branch, source_branch)
        except Exception:
            pass
        
        try:
            gitlab_client.commit_file(
                project_id,
                fix_branch,
                ".gitlab-ci.yml",
                fix_content,
                f"EcoPilot: Auto-fix CI configuration (MR !{original_mr_iid})",
            )
        except Exception:
            return None
        
        try:
            mr = gitlab_client.create_mr(
                project_id,
                fix_branch,
                target_branch,
                f"CI Optimization: Auto-fix for MR !{original_mr_iid}",
                f"Auto-generated by EcoPilot AI to fix CI issues.\n\n"
                f"Original MR: !{original_mr_iid}",
            )
            return {"web_url": mr.get("web_url"), "iid": mr.get("iid")}
        except Exception:
            return None
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_repair.py -v`
Expected: PASS

**Step 5: Commit**

Run: `git add ecopilot/repair.py tests/test_repair.py && git commit -m "feat: add AI repair service"`

---

## Task 3: 集成 AI 修复到 Service 层

**Files:**
- Modify: `ecopilot/service.py:1-89`
- Modify: `ecopilot/action.py` (如果需要)

**Step 1: 修改 service.py 集成 AIRepairService**

在 import 部分添加:
```python
from ecopilot.repair import AIRepairService
```

在 EcoPilotService.__init__ 添加:
```python
self._repair_service = AIRepairService(reporter._llm_client if reporter else None)
```

在 process_event 方法中，在发布 comment 后添加:
```python
# Generate AI fix if enabled and findings exist
fix_mr_info = None
if posted and findings:
    fix_content = self._repair_service.generate_fix(
        collected.ci_yaml, findings
    )
    if fix_content:
        fix_mr_info = self._repair_service.create_fix_mr(
            gitlab_client=self._gitlab_client,
            project_id=context.project_id,
            source_branch=context.source_branch,
            target_branch=context.target_branch,
            fix_content=fix_content,
            original_mr_iid=context.mr_iid,
        )
```

在返回结果中添加:
```python
"fix_mr_url": fix_mr_info.get("web_url") if fix_mr_info else None,
```

**Step 2: 验证无语法错误**

Run: `python -c "from ecopilot.service import EcoPilotService; print('OK')"`
Expected: OK

**Step 3: 运行现有测试**

Run: `pytest tests/ -v --tb=short`
Expected: All PASS

**Step 4: Commit**

Run: `git add ecopilot/service.py && git commit -m "feat: integrate AI repair into service"`

---

## Task 4: 添加 MR Comment 中的修复 MR 链接

**Files:**
- Modify: `ecopilot/reporter.py`

**Step 1: 修改 reporter.py 添加修复链接**

在 render 方法返回的字符串中添加修复 MR 链接（如果提供）:

```python
def render(
    self,
    context: MergeRequestContext,
    findings: list[Finding],
    impact: ImpactSummary,
    fix_mr_url: str | None = None,
) -> tuple[str, str]:
    # ... existing code ...
    result = ...  # existing result
    
    if fix_mr_url:
        result += f"\n\n💡 **Auto-fix available**: [!{fix_mr_url.split('!')[-1]}]({fix_mr_url})"
    
    return result, llm_mode
```

**Step 2: 更新 service.py 传递 fix_mr_url**

修改 service.py 中调用 reporter.render 的地方，传入 fix_mr_url

**Step 3: 运行测试**

Run: `pytest tests/ -v --tb=short`

**Step 4: Commit**

---

## 验收标准

- [ ] GitLabClient 支持 create_branch, commit_file, create_mr
- [ ] AIRepairService.generate_fix 返回修复后的 YAML
- [ ] AIRepairService.create_fix_mr 成功创建 MR
- [ ] Service 层完整集成，收到 MR 事件后自动创建修复 MR
- [ ] MR Comment 中显示修复 MR 链接
- [ ] 现有测试全部通过
