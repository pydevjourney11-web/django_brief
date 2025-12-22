from __future__ import annotations

import json
import logging
import threading
import urllib.error
import urllib.request
from typing import Dict

from django.db import transaction

from .models import Brief, BriefAnswer, BriefBlock, BriefQuestion, BriefQuestionOption

logger = logging.getLogger(__name__)


@transaction.atomic
def clone_brief(*, source: Brief, as_template: bool = False, created_from_template: bool = False) -> Brief:
    new_brief = Brief.objects.create(
        title=source.title,
        description=source.description,
        webhook_url=source.webhook_url,
        is_template=as_template,
        status=Brief.Status.DRAFT,
        completed_at=None,
        source_template=source if created_from_template else source.source_template,
    )

    block_map: Dict[int, BriefBlock] = {}
    question_map: Dict[int, BriefQuestion] = {}

    for block in source.blocks.all().order_by("position", "id"):
        new_block = BriefBlock.objects.create(
            brief=new_brief,
            title=block.title,
            description=block.description,
            position=block.position,
        )
        block_map[block.id] = new_block

    source_questions = (
        BriefQuestion.objects.select_related("block")
        .filter(block__brief=source)
        .order_by("block__position", "position", "id")
    )

    for q in source_questions:
        new_q = BriefQuestion.objects.create(
            block=block_map[q.block_id],
            name=q.name,
            type=q.type,
            label=q.label,
            placeholder=q.placeholder,
            default_value=q.default_value,
            webhook_variable_name=q.webhook_variable_name,
            position=q.position,
        )
        question_map[q.id] = new_q

    source_options = BriefQuestionOption.objects.select_related("question").filter(
        question__block__brief=source
    )

    for opt in source_options.order_by("question_id", "position", "id"):
        new_q = question_map.get(opt.question_id)
        if not new_q:
            continue
        BriefQuestionOption.objects.create(
            question=new_q,
            value=opt.value,
            label=opt.label,
            position=opt.position,
        )

    return new_brief


def build_webhook_payload(*, brief: Brief) -> dict:
    rows = (
        BriefAnswer.objects.select_related("question")
        .filter(brief=brief)
        .values_list("question__webhook_variable_name", "value")
    )

    payload: dict = {}
    for var_name, value in rows:
        if not var_name:
            continue
        if var_name in payload:
            logger.warning(
                "Duplicate webhook_variable_name=%s for brief_id=%s; overriding previous value",
                var_name,
                brief.id,
            )
        payload[var_name] = value

    return payload


def _send_webhook_sync(*, url: str, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "User-Agent": "briefs-webhook/1.0",
        },
    )

    # Важно: таймаут, чтобы не зависать даже в фоне
    with urllib.request.urlopen(req, timeout=5) as resp:
        # просто читаем тело, чтобы соединение корректно закрывалось
        resp.read()


def send_brief_webhook_async(*, brief_id: int) -> None:
    try:
        brief = Brief.objects.get(pk=brief_id)
    except Brief.DoesNotExist:
        logger.warning("Webhook skipped: brief_id=%s not found", brief_id)
        return

    if not brief.webhook_url:
        return
    if brief.is_template:
        return
    if brief.status != Brief.Status.COMPLETED:
        return

    payload = build_webhook_payload(brief=brief)

    def runner() -> None:
        try:
            _send_webhook_sync(url=brief.webhook_url, payload=payload)
        except urllib.error.HTTPError as exc:
            logger.exception(
                "Webhook HTTPError brief_id=%s url=%s status=%s body=%s",
                brief.id,
                brief.webhook_url,
                getattr(exc, "code", None),
                getattr(exc, "reason", None),
            )
        except Exception:
            logger.exception("Webhook error brief_id=%s url=%s", brief.id, brief.webhook_url)

    threading.Thread(target=runner, daemon=True).start()
