from __future__ import annotations

from ecopilot.models import Finding
from ecopilot.models import MergeRequestContext


class ActionPublisher:
    def __init__(self, gitlab_client: object):
        self._gitlab_client = gitlab_client
        self._seen_event_ids: set[str] = set()

    def publish_comment(self, context: MergeRequestContext, body: str) -> bool:
        if self.is_duplicate_event(context):
            return False
        marker = self._event_marker(context.event_id)
        body_with_marker = f"{body}\n\n{marker}"
        self._gitlab_client.create_mr_note(context.project_id, context.mr_iid, body_with_marker)
        self._seen_event_ids.add(context.event_id)
        return True

    def apply_optional_actions(
        self,
        context: MergeRequestContext,
        findings: list[Finding],
        enable_auto_label: bool,
        enable_auto_issue: bool,
    ) -> dict[str, bool]:
        label_applied = False
        issue_created = False

        if enable_auto_label and findings:
            labels = ["ci-waste-detected"]
            self._gitlab_client.add_mr_label(context.project_id, context.mr_iid, labels)
            label_applied = True

        has_high_severity = any(finding.severity.lower() == "high" for finding in findings)
        if enable_auto_issue and has_high_severity:
            title = f"EcoPilot optimization follow-up for MR !{context.mr_iid}"
            lines = ["EcoPilot detected high-severity CI waste findings:", ""]
            for finding in findings:
                if finding.severity.lower() != "high":
                    continue
                lines.append(f"- [{finding.rule_id}] {finding.title}: {finding.recommendation}")
            self._gitlab_client.create_issue(
                context.project_id,
                title=title,
                description="\n".join(lines),
            )
            issue_created = True

        return {"label_applied": label_applied, "issue_created": issue_created}

    @staticmethod
    def _event_marker(event_id: str) -> str:
        return f"<!-- ecopilot:event_id={event_id} -->"

    def is_duplicate_event(self, context: MergeRequestContext) -> bool:
        if context.event_id in self._seen_event_ids:
            return True
        marker = self._event_marker(context.event_id)
        if self._marker_exists(context, marker):
            self._seen_event_ids.add(context.event_id)
            return True
        return False

    def _marker_exists(self, context: MergeRequestContext, marker: str) -> bool:
        list_notes = getattr(self._gitlab_client, "list_mr_notes", None)
        if not callable(list_notes):
            return False
        notes = list_notes(context.project_id, context.mr_iid)
        for note in notes:
            body = str(note.get("body", ""))
            if marker in body:
                return True
        return False
