import json

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles import finders
from django.templatetags.static import static

from .models import Brief, BriefAnswer, BriefBlock, BriefQuestion, BriefQuestionOption
from .services import clone_brief, send_brief_webhook_async


@staff_member_required
@require_POST
def admin_copy_brief(request: HttpRequest, brief_id: int) -> HttpResponse:
    source = get_object_or_404(Brief, pk=brief_id)
    new_brief = clone_brief(source=source, as_template=False, created_from_template=source.is_template)
    messages.success(request, "Бриф скопирован")
    return redirect(reverse("admin:briefs_brief_change", args=(new_brief.pk,)))


@staff_member_required
@require_POST
def admin_create_from_template(request: HttpRequest, brief_id: int) -> HttpResponse:
    source = get_object_or_404(Brief, pk=brief_id)
    if not source.is_template:
        raise Http404("Brief is not a template")

    new_brief = clone_brief(source=source, as_template=False, created_from_template=True)
    messages.success(request, "Бриф создан из шаблона")
    return redirect(reverse("admin:briefs_brief_change", args=(new_brief.pk,)))


@staff_member_required
def admin_brief_progress(request: HttpRequest, brief_id: int) -> HttpResponse:
    brief = get_object_or_404(Brief, pk=brief_id)

    total_questions = BriefQuestion.objects.filter(block__brief=brief).count()
    answered_questions = BriefAnswer.objects.filter(brief=brief).exclude(value__isnull=True).count()
    percent = int((answered_questions / total_questions) * 100) if total_questions else 0

    blocks = list(brief.blocks.all().order_by("position", "id"))
    block_rows = []
    for block in blocks:
        q_ids = list(block.questions.values_list("id", flat=True))
        block_total = len(q_ids)
        block_answered = 0
        if q_ids:
            block_answered = (
                BriefAnswer.objects.filter(brief=brief, question_id__in=q_ids)
                .exclude(value__isnull=True)
                .count()
            )
        block_percent = int((block_answered / block_total) * 100) if block_total else 0
        block_rows.append(
            {
                "block": block,
                "total": block_total,
                "answered": block_answered,
                "percent": block_percent,
            }
        )

    context = {
        **admin.site.each_context(request),
        "title": f"Заполненность: {brief.title}",
        "brief": brief,
        "total_questions": total_questions,
        "answered_questions": answered_questions,
        "percent": percent,
        "block_rows": block_rows,
        "public_url": reverse("briefs:brief_fill", args=(brief.public_uuid,)),
    }

    return render(request, "admin/briefs/brief/progress.html", context)


@staff_member_required
def admin_brief_choose_template(request: HttpRequest) -> HttpResponse:
    templates = Brief.objects.filter(is_template=True).order_by("-created_at")

    if request.method == "POST":
        template_id = request.POST.get("template_id")
        try:
            template_id_int = int(template_id) if template_id else None
        except ValueError:
            template_id_int = None

        if not template_id_int:
            messages.error(request, "Выберите шаблон")
            return redirect(reverse("briefs_admin:admin_brief_choose_template"))

        source = get_object_or_404(Brief, pk=template_id_int, is_template=True)
        new_brief = clone_brief(source=source, as_template=False, created_from_template=True)
        messages.success(request, "Бриф создан из шаблона")
        return redirect(reverse("admin:briefs_brief_change", args=(new_brief.pk,)))

    context = {
        **admin.site.each_context(request),
        "title": "Создать бриф из шаблона",
        "templates": templates,
    }
    return render(request, "admin/briefs/brief/choose_template.html", context)


@staff_member_required
def admin_brief_quick_create(request: HttpRequest) -> HttpResponse:
    context = {**admin.site.each_context(request), "title": "Быстро создать бриф"}
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        description = (request.POST.get("description") or "").strip()
        include_contacts = request.POST.get("include_contacts") == "on"

        if not title:
            messages.error(request, "Введите название брифа")
            return render(request, "admin/briefs/brief/quick_create.html", context)

        with transaction.atomic():
            brief = Brief.objects.create(title=title, description=description, is_template=False)

            pos = 1
            if include_contacts:
                block = BriefBlock.objects.create(
                    brief=brief,
                    title="Контакты",
                    description="Контактные данные заказчика",
                    position=pos,
                )
                pos += 1
                BriefQuestion.objects.bulk_create(
                    [
                        BriefQuestion(
                            block=block,
                            position=1,
                            name="fio",
                            type=BriefQuestion.QuestionType.STRING,
                            label="Фамилия Имя Отчество",
                            placeholder="Иванов Иван Иванович",
                            webhook_variable_name="fio",
                        ),
                        BriefQuestion(
                            block=block,
                            position=2,
                            name="phones",
                            type=BriefQuestion.QuestionType.STRING,
                            label="Телефоны",
                            placeholder="+7 900 000-00-00",
                            webhook_variable_name="phones",
                        ),
                        BriefQuestion(
                            block=block,
                            position=3,
                            name="email",
                            type=BriefQuestion.QuestionType.STRING,
                            label="E-mail",
                            placeholder="name@example.com",
                            webhook_variable_name="email",
                        ),
                        BriefQuestion(
                            block=block,
                            position=4,
                            name="current_site",
                            type=BriefQuestion.QuestionType.STRING,
                            label="Текущий сайт",
                            placeholder="https://",
                            webhook_variable_name="current_site",
                        ),
                    ]
                )

        messages.success(request, "Бриф создан")
        return redirect(reverse("admin:briefs_brief_change", args=(brief.pk,)))

    return render(request, "admin/briefs/brief/quick_create.html", context)


@ensure_csrf_cookie
def brief_fill(request: HttpRequest, public_uuid) -> HttpResponse:
    brief = get_object_or_404(Brief, public_uuid=public_uuid, is_template=False)

    blocks = (
        brief.blocks.all()
        .prefetch_related("questions__options")
        .order_by("position", "id")
    )

    answers_by_question_id = dict(
        BriefAnswer.objects.filter(brief=brief).values_list("question_id", "value")
    )

    header_question_ids = []

    logo_url = None
    for candidate in [
        "logo.png",
        "logo.svg",
        "Логотип без фона 2.png",
        "img/logo.png",
        "Img/logo.png",
        "img/Логотип без фона 2.png",
        "Img/Логотип без фона 2.png",
    ]:
        try:
            if finders.find(candidate):
                logo_url = static(candidate)
                break
            if staticfiles_storage.exists(candidate):
                logo_url = staticfiles_storage.url(candidate)
                break
        except Exception:
            continue

    icon_candidates = {
        "fio": [
            "icons/user.svg",
            "Img/icons/user.svg",
            "icons/user.png",
            "Img/icons/user.png",
            "img/icons/user-svgrepo-com 2.svg",
            "Img/icons/user-svgrepo-com 2.svg",
            "img/icons/user-svgrepo-com 2.png",
            "Img/icons/user-svgrepo-com 2.png",
            "Img/icons/user-svgrepo-com 1.png",
            "img/icons/user-svgrepo-com 1.png",
            "Img/user-svgrepo-com 1.png",
            "img/user-svgrepo-com 1.png",
        ],
        "phones": [
            "icons/phone.svg",
            "Img/icons/phone.svg",
            "icons/phone.png",
            "Img/icons/phone.png",
            "img/icons/phone-svgrepo-com 2.svg",
            "Img/icons/phone-svgrepo-com 2.svg",
            "img/icons/phone-svgrepo-com 2.png",
            "Img/icons/phone-svgrepo-com 2.png",
            "Img/icons/user-svgrepo-com 1.png",
            "img/icons/user-svgrepo-com 1.png",
            "Img/phone-svgrepo-com 1.png",
            "img/phone-svgrepo-com 1.png",
            "Img/user-svgrepo-com 1.png",
            "img/user-svgrepo-com 1.png",
        ],
        "email": [
            "icons/mail.svg",
            "Img/icons/mail.svg",
            "icons/email.svg",
            "Img/icons/email.svg",
            "icons/mail.png",
            "Img/icons/mail.png",
            "img/icons/mail-svgrepo-com 2.svg",
            "Img/icons/mail-svgrepo-com 2.svg",
            "img/icons/mail-svgrepo-com 2.png",
            "Img/icons/mail-svgrepo-com 2.png",
            "Img/icons/mail-svgrepo-com 1.png",
            "img/icons/mail-svgrepo-com 1.png",
            "Img/mail-svgrepo-com 1.png",
            "img/mail-svgrepo-com 1.png",
            "Img/mail-svgrepo-com 2.png",
            "img/mail-svgrepo-com 2.png",
        ],
        "current_site": [
            "icons/globe.svg",
            "Img/icons/globe.svg",
            "icons/site.svg",
            "Img/icons/site.svg",
            "icons/globe.png",
            "Img/icons/globe.png",
            "img/icons/web-svgrepo-com 1.svg",
            "Img/icons/web-svgrepo-com 1.svg",
            "img/icons/web-svgrepo-com 1.png",
            "Img/icons/web-svgrepo-com 1.png",
            "Img/web-svgrepo-com 1.png",
            "img/web-svgrepo-com 1.png",
        ],
    }

    header_items = []
    qs = (
        BriefQuestion.objects.filter(block__brief=brief, show_in_header=True)
        .select_related("block")
        .order_by("header_position", "position", "id")
    )
    for q in qs:
        icon_url = None
        try:
            header_icon = getattr(q, "header_icon", None)
            if header_icon:
                if finders.find(header_icon):
                    icon_url = static(header_icon)
                elif staticfiles_storage.exists(header_icon):
                    icon_url = staticfiles_storage.url(header_icon)
        except Exception:
            pass
        if not icon_url:
            for p in icon_candidates.get(q.name, []):
                try:
                    if finders.find(p):
                        icon_url = static(p)
                        break
                    if staticfiles_storage.exists(p):
                        icon_url = staticfiles_storage.url(p)
                        break
                except Exception:
                    continue
        header_items.append({"q": q, "icon_url": icon_url})
        header_question_ids.append(q.id)

    block_cols = {}
    multiple_select_ids = set()
    for block in blocks:
        short_count = 0
        for q in block.questions.all():
            if q.id in header_question_ids:
                continue
            if q.type == BriefQuestion.QuestionType.TEXT:
                continue
            if q.type == BriefQuestion.QuestionType.SELECT and getattr(q, "is_multiple", False):
                multiple_select_ids.add(q.id)
            short_count += 1
        cols = 1
        if short_count >= 6:
            cols = 3
        elif short_count >= 4:
            cols = 2
        block_cols[block.id] = cols

    for qid in list(answers_by_question_id.keys()):
        if qid in multiple_select_ids:
            raw = answers_by_question_id.get(qid)
            if isinstance(raw, str) and raw:
                try:
                    parsed = json.loads(raw)
                    answers_by_question_id[qid] = parsed
                except Exception:
                    pass

    header_title = "Бриф"
    header_subtitle = "на создание сайта\nи контекстной рекламы"
    header_description = "Данный опросный лист поможет более четко понять цели и задачи контекстной рекламы."

    is_submitted = (request.GET.get("submitted") == "1") or (brief.status == Brief.Status.COMPLETED)

    calendar_icon_url = None
    for p in [
        "calendar-minimalistic-svgrepo-com 1.svg",
        "calendar-minimalistic-svgrepo-com 1.png",
        "img/calendar-minimalistic-svgrepo-com 1.svg",
        "img/calendar-minimalistic-svgrepo-com 1.png",
        "Img/calendar-minimalistic-svgrepo-com 1.svg",
        "Img/calendar-minimalistic-svgrepo-com 1.png",
    ]:
        try:
            if finders.find(p):
                calendar_icon_url = static(p)
                break
            if staticfiles_storage.exists(p):
                calendar_icon_url = staticfiles_storage.url(p)
                break
        except Exception:
            continue

    return render(
        request,
        "briefs/fill_brief.html",
        {
            "brief": brief,
            "blocks": blocks,
            "block_cols": block_cols,
            "answers_by_question_id": answers_by_question_id,
            "header_items": header_items,
            "header_question_ids": header_question_ids,
            "logo_url": logo_url,
            "header_title": header_title,
            "header_subtitle": header_subtitle,
            "header_description": header_description,
            "is_submitted": is_submitted,
            "calendar_icon_url": calendar_icon_url,
        },
    )


@require_POST
def brief_autosave(request: HttpRequest, public_uuid) -> JsonResponse:
    brief = get_object_or_404(Brief, public_uuid=public_uuid, is_template=False)
    if brief.status == Brief.Status.COMPLETED:
        return JsonResponse({"error": "Бриф уже отправлен"}, status=409)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Некорректный JSON"}, status=400)

    question_id = payload.get("question_id")
    if not isinstance(question_id, int):
        return JsonResponse({"error": "question_id должен быть числом"}, status=400)

    raw_value = payload.get("value")

    try:
        question = BriefQuestion.objects.select_related("block__brief").get(
            pk=question_id,
            block__brief=brief,
        )
    except BriefQuestion.DoesNotExist:
        return JsonResponse({"error": "Вопрос не найден"}, status=404)

    normalized = raw_value
    if normalized == "":
        normalized = None

    if question.type in (BriefQuestion.QuestionType.STRING, BriefQuestion.QuestionType.TEXT):
        if normalized is None:
            pass
        elif not isinstance(normalized, str):
            normalized = str(normalized)

    elif question.type == BriefQuestion.QuestionType.INT:
        if normalized is None:
            pass
        else:
            try:
                normalized = int(str(normalized))
            except (TypeError, ValueError):
                return JsonResponse({"error": "Ожидается целое число"}, status=400)

    elif question.type == BriefQuestion.QuestionType.FLOAT:
        if normalized is None:
            pass
        else:
            try:
                normalized = float(str(normalized))
            except (TypeError, ValueError):
                return JsonResponse({"error": "Ожидается число"}, status=400)

    elif question.type == BriefQuestion.QuestionType.SELECT:
        if getattr(question, "is_multiple", False):
            if normalized is None:
                pass
            else:
                if isinstance(normalized, str):
                    try:
                        normalized = json.loads(normalized)
                    except Exception:
                        normalized = [normalized]
                if not isinstance(normalized, list):
                    return JsonResponse({"error": "Ожидается список значений"}, status=400)
                allowed = set(BriefQuestionOption.objects.filter(question=question).values_list("value", flat=True))
                for v in list(normalized):
                    if v not in allowed:
                        return JsonResponse({"error": f"Некорректный вариант: {v}"}, status=400)
                normalized = json.dumps(normalized, ensure_ascii=False)
        else:
            if normalized is None:
                pass
            else:
                if not isinstance(normalized, str):
                    normalized = str(normalized)
                exists = BriefQuestionOption.objects.filter(question=question, value=normalized).exists()
                if not exists:
                    return JsonResponse({"error": "Некорректный вариант"}, status=400)

    else:
        return JsonResponse({"error": "Неподдерживаемый тип вопроса"}, status=400)

    BriefAnswer.objects.update_or_create(
        brief=brief,
        question=question,
        defaults={"value": normalized},
    )

    return JsonResponse({"ok": True, "brief_status": brief.status})


@require_POST
def brief_submit(request: HttpRequest, public_uuid) -> HttpResponse:
    brief = get_object_or_404(Brief, public_uuid=public_uuid, is_template=False)
    if brief.status == Brief.Status.COMPLETED:
        return redirect(f"{reverse('briefs:brief_fill', args=(brief.public_uuid,))}?submitted=1")

    with transaction.atomic():
        brief.status = Brief.Status.COMPLETED
        brief.completed_at = timezone.now()
        brief.save(update_fields=("status", "completed_at", "updated_at"))

        brief_id = brief.id
        transaction.on_commit(lambda: send_brief_webhook_async(brief_id=brief_id))

    return redirect(f"{reverse('briefs:brief_fill', args=(brief.public_uuid,))}?submitted=1")
