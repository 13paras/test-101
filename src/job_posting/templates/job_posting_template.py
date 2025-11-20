from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, List, Mapping, MutableSequence, Sequence


@dataclass(slots=True)
class JobPostingTemplateData:
    """Structured data required to render a job posting report."""

    company_name: str = "Company"
    job_title: str = "Open Role"
    location: str = "Location not specified"
    company_overview: str = ""
    job_summary: str = ""
    responsibilities: Sequence[str] = field(default_factory=tuple)
    requirements: Sequence[str] = field(default_factory=tuple)
    benefits: Sequence[str] = field(default_factory=tuple)
    how_to_apply: str = ""
    salary_range: str | None = None

    @property
    def salary_data_available(self) -> bool:
        return bool(self.salary_range and self.salary_range.strip())


def generate_job_posting_report(
    job_posting: JobPostingTemplateData | Mapping[str, Any],
) -> str:
    """
    Build a markdown job posting report from the provided data.

    Parameters
    ----------
    job_posting:
        Either a ``JobPostingTemplateData`` instance or a mapping with similar keys.

    Returns
    -------
    str
        A formatted markdown representation of the job posting.
    """

    data = (
        job_posting
        if isinstance(job_posting, JobPostingTemplateData)
        else _coerce_to_template_data(job_posting)
    )

    report: List[str] = []
    heading = (
        f"# {data.company_name} - {data.job_title}"
        if data.company_name
        else f"# {data.job_title}"
    )
    _append_section(report, heading)
    _append_section(report, "## Company Overview", data.company_overview)
    _append_section(report, "## Location", data.location)
    _append_section(report, "## Job Summary", data.job_summary)
    _append_bullets(report, "Responsibilities", data.responsibilities)
    _append_bullets(report, "Requirements", data.requirements)
    _append_bullets(report, "Benefits", data.benefits)
    _append_section(report, "## How to Apply", data.how_to_apply)

    report.append("## Salary Range")
    salary_range_value = (data.salary_range or "").strip()
    salary_data_available = data.salary_data_available
    if salary_data_available:
        report.append(f"Salary Range: {salary_range_value}")
    else:
        report.append("Salary Range: Not disclosed")

    return "\n".join(_remove_trailing_blanks(report))


def _append_section(report: MutableSequence[str], title: str, body: str | None = None) -> None:
    report.append(title)
    if body:
        report.append(body.strip())
    report.append("")


def _append_bullets(
    report: MutableSequence[str],
    title: str,
    items: Iterable[str] | None,
) -> None:
    normalized_items = [item.strip() for item in items or [] if str(item).strip()]
    if not normalized_items:
        return
    report.append(f"## {title}")
    for item in normalized_items:
        report.append(f"- {item}")
    report.append("")


def _coerce_to_template_data(data: Mapping[str, Any]) -> JobPostingTemplateData:
    def _text(*keys: str, default: str = "") -> str:
        for key in keys:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return default

    def _list(*keys: str) -> Sequence[str]:
        for key in keys:
            value = data.get(key)
            if not value:
                continue
            if isinstance(value, str):
                return (value.strip(),)
            if isinstance(value, Sequence):
                return tuple(str(item).strip() for item in value if str(item).strip())
        return ()

    salary_text = _text("salary_range")

    return JobPostingTemplateData(
        company_name=_text("company_name", "company", default="Company"),
        job_title=_text("job_title", "title", default="Open Role"),
        location=_text("location", "job_location", default="Location not specified"),
        company_overview=_text("company_overview", "company_description"),
        job_summary=_text("job_summary", "summary", "role_summary"),
        responsibilities=_list("responsibilities"),
        requirements=_list("requirements", "qualifications"),
        benefits=_list("benefits", "perks"),
        how_to_apply=_text("how_to_apply", "application_process"),
        salary_range=salary_text or None,
    )

def _remove_trailing_blanks(lines: Sequence[str]) -> Sequence[str]:
    trimmed = list(lines)
    while trimmed and not trimmed[-1].strip():
        trimmed.pop()
    return trimmed
