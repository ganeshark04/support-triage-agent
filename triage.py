#!/usr/bin/env python3

import csv
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class Status(Enum):
    REPLIED = "replied"
    ESCALATED = "escalated"


class RequestType(Enum):
    PRODUCT_ISSUE = "product_issue"
    FEATURE_REQUEST = "feature_request"
    BUG = "bug"
    INVALID = "invalid"


@dataclass
class TriageResult:
    status: str
    product_area: str
    response: str
    justification: str
    request_type: str


class SupportCorpus(ABC):
    def __init__(self, domain: str):
        self.domain = domain
        self.knowledge_base = {}
        self.load_knowledge_base()

    @abstractmethod
    def load_knowledge_base(self):
        pass

    @abstractmethod
    def search(self, query: str) -> List[Tuple[str, str, float]]:
        pass


class HackerRankCorpus(SupportCorpus):
    def load_knowledge_base(self):
        self.knowledge_base = {
            "account_access": {
                "keywords": ["login", "password", "reset", "account"],
                "articles": [
                    ("Password Reset", "Use 'Forgot Password' on login page."),
                ]
            }
        }

    def search(self, query: str):
        results = []
        query_lower = query.lower()

        for category, data in self.knowledge_base.items():
            keywords = data["keywords"]

            keyword_matches = sum(1 for kw in keywords if kw in query_lower)

            if keyword_matches > 0:
                for title, content in data["articles"]:
                    results.append((category, content, 0.7))

        # better fallback
        if not results:
            return [("general", "Please check support documentation or contact support.", 0.3)]

        return results


class ClaudeCorpus(HackerRankCorpus):
    pass


class VisaCorpus(HackerRankCorpus):
    pass


class TriageAgent:

    def __init__(self):
        self.corpora = {
            "HackerRank": HackerRankCorpus("HackerRank"),
            "Claude": ClaudeCorpus("Claude"),
            "Visa": VisaCorpus("Visa"),
        }

        self.escalation_keywords = [
            "fraud", "unauthorized", "hacked", "charged twice"
        ]

    def infer_company(self, text: str, company: Optional[str]):
        if company and company.strip().lower() != "none":
            return company.strip()

        text = text.lower()

        if "visa" in text or "card" in text:
            return "Visa"
        if "hackerrank" in text or "test" in text:
            return "HackerRank"
        if "claude" in text:
            return "Claude"

        return "Unknown"

    def detect_request_type(self, text: str):
        text = text.lower()

        if any(w in text for w in ["feature", "add", "request"]):
            return RequestType.FEATURE_REQUEST.value
        elif any(w in text for w in ["error", "bug", "fail", "not working"]):
            return RequestType.BUG.value
        elif any(w in text for w in ["how", "help", "issue", "problem", "cannot", "unable"]):
            return RequestType.PRODUCT_ISSUE.value
        else:
            return RequestType.PRODUCT_ISSUE.value

    def triage(self, issue, subject="", company=None):

        full_text = f"{subject} {issue}".lower()

        request_type = self.detect_request_type(full_text)

        inferred_company = self.infer_company(full_text, company)

        if inferred_company == "Unknown":
            return TriageResult(
                status="escalated",
                product_area="general",
                response="Unable to determine service. Please specify HackerRank, Claude, or Visa.",
                justification="Unknown domain",
                request_type=request_type
            )

        if any(word in full_text for word in self.escalation_keywords):
            return TriageResult(
                status="escalated",
                product_area="security",
                response="This is a sensitive issue and has been escalated.",
                justification="Sensitive keywords detected",
                request_type=request_type
            )

        corpus = self.corpora.get(inferred_company)

        results = corpus.search(full_text)

        best = results[0]

        # better product area
        if "login" in full_text or "password" in full_text:
            product_area = "account_access"
        elif "test" in full_text or "assessment" in full_text:
            product_area = "assessments"
        elif "payment" in full_text or "card" in full_text or "charge" in full_text:
            product_area = "billing"
        else:
            product_area = best[0]

        return TriageResult(
            status="replied",
            product_area=product_area,
            response=f"For {inferred_company} support: {best[1]} Please follow the instructions carefully.",
            justification=f"Identified as {request_type} and matched to {inferred_company} support system",
            request_type=request_type
        )


def main():
    agent = TriageAgent()

    with open("support_tickets.csv", "r", encoding="utf-8") as infile, \
         open("output.csv", "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["status", "product_area", "response", "justification", "request_type"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            issue = (row.get("issue") or row.get("Issue") or "").strip()
            subject = (row.get("subject") or row.get("Subject") or "").strip()
            company = (row.get("company") or row.get("Company") or "").strip()

            if not issue:
                continue

            result = agent.triage(issue, subject, company)

            writer.writerow({
                "status": result.status,
                "product_area": result.product_area,
                "response": result.response,
                "justification": result.justification,
                "request_type": result.request_type
            })

    print("✅ Done")


if __name__ == "__main__":
    main()