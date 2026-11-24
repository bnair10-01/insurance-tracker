import anthropic

from app.config import settings

MAX_TEXT_CHARS = 50_000

_nullable_string = {"anyOf": [{"type": "string"}, {"type": "null"}]}

SUBMIT_INSURANCE_DETAILS_TOOL = {
    "name": "submit_insurance_details",
    "description": "Submit structured insurance policy details extracted from a document's text.",
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "item_name": {
                "type": "string",
                "description": (
                    "Short human-readable label for the insured item, e.g. '2021 Honda Civic', "
                    "'Home - 123 Main St', 'iPhone 15 Pro'. Infer from context if not stated verbatim."
                ),
            },
            "category": {
                "type": "string",
                "enum": ["auto", "home", "health", "life", "gadget", "travel", "pet", "other"],
            },
            "provider_name": {"type": "string", "description": "The insurer or underwriting company."},
            "provider_contact": {
                "type": "object",
                "properties": {
                    "phone": _nullable_string,
                    "email": _nullable_string,
                    "website": _nullable_string,
                    "agent_name": _nullable_string,
                },
                "required": ["phone", "email", "website", "agent_name"],
                "additionalProperties": False,
            },
            "policy_number": _nullable_string,
            "coverage_start": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "ISO-8601 date (YYYY-MM-DD). Null only if genuinely absent from the text.",
            },
            "coverage_end": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "ISO-8601 date (YYYY-MM-DD), or null if the policy states no end date.",
            },
            "premium": {
                "type": "object",
                "properties": {
                    "amount": {"anyOf": [{"type": "number"}, {"type": "null"}]},
                    "frequency": {
                        "anyOf": [
                            {"type": "string", "enum": ["monthly", "annual", "one-time"]},
                            {"type": "null"},
                        ]
                    },
                },
                "required": ["amount", "frequency"],
                "additionalProperties": False,
            },
            "coverage_summary": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "1-3 sentence plain-language summary of what is covered.",
            },
            "extraction_confidence": {
                "type": "number",
                "description": (
                    "Your confidence from 0.0 to 1.0 that these fields are accurate and complete, "
                    "given how clear and complete the source text is."
                ),
            },
        },
        "required": [
            "item_name",
            "category",
            "provider_name",
            "provider_contact",
            "policy_number",
            "coverage_start",
            "coverage_end",
            "premium",
            "coverage_summary",
            "extraction_confidence",
        ],
        "additionalProperties": False,
    },
}


async def extract_insurance_details(raw_text: str) -> dict:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model=settings.claude_model,
        max_tokens=8192,
        output_config={"effort": "medium"},
        tools=[SUBMIT_INSURANCE_DETAILS_TOOL],
        tool_choice={"type": "tool", "name": "submit_insurance_details"},
        messages=[
            {
                "role": "user",
                "content": (
                    "Extract structured insurance policy details from this document text. "
                    "Use null for any field the document does not state — do not invent values.\n\n"
                    f"{raw_text[:MAX_TEXT_CHARS]}"
                ),
            }
        ],
    )

    tool_use = next(block for block in response.content if block.type == "tool_use")
    return tool_use.input
