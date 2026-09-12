# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.db.models.functions import Lower
from django.forms import Form
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.html import format_html, format_html_join
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from babybuddy.mixins import LoginRequiredMixin, PermissionRequiredMixin
from babybuddy.views import BabyBuddyFilterView, BabyBuddyPaginatedView
from core import filters, forms, models, timeline


def _prepare_timeline_context_data(context, date, child=None):
    date = timezone.datetime.strptime(date, "%Y-%m-%d")
    date = timezone.localtime(timezone.make_aware(date))
    context["timeline_objects"] = timeline.get_objects(date, child)
    context["date"] = date
    context["date_previous"] = date - timezone.timedelta(days=1)
    if date.date() < timezone.localdate():
        context["date_next"] = date + timezone.timedelta(days=1)
    pass


class CoreAddView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    def get_success_message(self, cleaned_data):
        cleaned_data["model"] = self.model._meta.verbose_name.title()
        if "child" in cleaned_data:
            self.success_message = _("%(model)s entry for %(child)s added!")
        else:
            self.success_message = _("%(model)s entry added!")
        return self.success_message % cleaned_data

    def get_form_kwargs(self):
        """
        Check for and add "child" and "timer" from request query parameters.
          - "child" may provide a slug for a Child instance.
          - "timer" may provided an ID for a Timer instance.

        These arguments are used in some add views to pre-fill initial data in
        the form fields.

        :return: Updated keyword arguments.
        """
        kwargs = super(CoreAddView, self).get_form_kwargs()
        for parameter in ["child", "timer", "preset", "duration"]:
            value = self.request.GET.get(parameter, None)
            if value:
                kwargs.update({parameter: value})
        return kwargs


class CoreUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    def get_success_message(self, cleaned_data):
        cleaned_data["model"] = self.model._meta.verbose_name.title()
        if cleaned_data.get("child"):
            self.success_message = _("%(model)s entry for %(child)s updated.")
        else:
            self.success_message = _("%(model)s entry updated.")
        return self.success_message % cleaned_data


class CoreDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    def get_success_message(self, cleaned_data):
        return _("%(model)s entry deleted.") % {
            "model": self.model._meta.verbose_name.title()
        }


class BMIList(PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView):
    model = models.BMI
    template_name = "core/bmi_list.html"
    permission_required = ("core.view_bmi",)
    filterset_class = filters.BMIFilter


class BMIAdd(CoreAddView):
    model = models.BMI
    permission_required = ("core.add_bmi",)
    form_class = forms.BMIForm
    success_url = reverse_lazy("core:bmi-list")


class BMIUpdate(CoreUpdateView):
    model = models.BMI
    permission_required = ("core.change_bmi",)
    form_class = forms.BMIForm
    success_url = reverse_lazy("core:bmi-list")


class BMIDelete(CoreDeleteView):
    model = models.BMI
    permission_required = ("core.delete_bmi",)
    success_url = reverse_lazy("core:bmi-list")


class ChildList(PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView):
    model = models.Child
    template_name = "core/child_list.html"
    permission_required = ("core.view_child",)
    filterset_fields = ("first_name", "last_name")


class ChildAdd(CoreAddView):
    model = models.Child
    permission_required = ("core.add_child",)
    form_class = forms.ChildForm
    success_url = reverse_lazy("core:child-list")
    success_message = _("%(first_name)s %(last_name)s added!")


class ChildDetail(PermissionRequiredMixin, DetailView):
    model = models.Child
    permission_required = ("core.view_child",)

    def get_context_data(self, **kwargs):
        context = super(ChildDetail, self).get_context_data(**kwargs)
        date = self.request.GET.get("date", str(timezone.localdate()))
        _prepare_timeline_context_data(context, date, self.object)
        return context


class ChildUpdate(CoreUpdateView):
    model = models.Child
    permission_required = ("core.change_child",)
    form_class = forms.ChildForm
    success_url = reverse_lazy("core:child-list")


class ChildDelete(CoreUpdateView):
    model = models.Child
    form_class = forms.ChildDeleteForm
    template_name = "core/child_confirm_delete.html"
    permission_required = ("core.delete_child",)
    success_url = reverse_lazy("core:child-list")

    def get_success_message(self, cleaned_data):
        """This class cannot use `CoreDeleteView` because of the confirmation
        step required so the success message must be overridden."""
        success_message = _("%(model)s entry deleted.") % {
            "model": self.model._meta.verbose_name.title()
        }
        return success_message % cleaned_data


class DiaperChangeList(
    PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView
):
    model = models.DiaperChange
    template_name = "core/diaperchange_list.html"
    permission_required = ("core.view_diaperchange",)
    filterset_class = filters.DiaperChangeFilter


class DiaperChangeAdd(CoreAddView):
    model = models.DiaperChange
    permission_required = ("core.add_diaperchange",)
    form_class = forms.DiaperChangeForm
    success_url = reverse_lazy("core:diaperchange-list")


class DiaperChangeUpdate(CoreUpdateView):
    model = models.DiaperChange
    permission_required = ("core.change_diaperchange",)
    form_class = forms.DiaperChangeForm
    success_url = reverse_lazy("core:diaperchange-list")


class DiaperChangeDelete(CoreDeleteView):
    model = models.DiaperChange
    permission_required = ("core.delete_diaperchange",)
    success_url = reverse_lazy("core:diaperchange-list")


class FeedingList(PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView):
    model = models.Feeding
    template_name = "core/feeding_list.html"
    permission_required = ("core.view_feeding",)
    filterset_class = filters.FeedingFilter


class FeedingAdd(CoreAddView):
    model = models.Feeding
    permission_required = ("core.add_feeding",)
    form_class = forms.FeedingForm
    success_url = reverse_lazy("core:feeding-list")


class BottleFeedingAdd(CoreAddView):
    model = models.Feeding
    permission_required = ("core.add_feeding",)
    form_class = forms.BottleFeedingForm
    success_url = reverse_lazy("core:feeding-list")


class FeedingUpdate(CoreUpdateView):
    model = models.Feeding
    permission_required = ("core.change_feeding",)
    form_class = forms.FeedingForm
    success_url = reverse_lazy("core:feeding-list")


class FeedingDelete(CoreDeleteView):
    model = models.Feeding
    permission_required = ("core.delete_feeding",)
    success_url = reverse_lazy("core:feeding-list")


class BreastfeedingStart(PermissionRequiredMixin, RedirectView):
    http_method_names = ["post"]
    permission_required = ("core.view_child", "core.view_timer", "core.add_timer")

    def post(self, request, *args, **kwargs):
        child = get_object_or_404(models.Child, slug=kwargs["slug"])
        try:
            with transaction.atomic():
                purpose = (
                    models.TimerPurpose.objects.select_related("timer")
                    .filter(
                        child=child,
                        purpose=models.Timer.PURPOSE_BREASTFEEDING,
                    )
                    .first()
                )
                if purpose:
                    timer = purpose.timer
                    created = False
                else:
                    timer = models.Timer.objects.create(
                        child=child,
                        user=request.user,
                    )
                    models.TimerPurpose.objects.create(
                        timer=timer,
                        child=child,
                        purpose=models.Timer.PURPOSE_BREASTFEEDING,
                    )
                    created = True
        except (IntegrityError, ValidationError):
            timer = models.Timer.objects.get(
                purpose_record__child=child,
                purpose_record__purpose=models.Timer.PURPOSE_BREASTFEEDING,
            )
            created = False

        if created:
            messages.success(request, _("Breastfeeding timer started."))
        else:
            messages.info(request, _("Breastfeeding timer is already running."))
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("dashboard:dashboard-child", kwargs={"slug": kwargs["slug"]})


class BreastfeedingFinish(PermissionRequiredMixin, RedirectView):
    http_method_names = ["post"]
    permission_required = (
        "core.view_child",
        "core.view_timer",
        "core.add_feeding",
        "core.delete_timer",
    )
    methods = {"left breast", "right breast", "both breasts"}

    def post(self, request, *args, **kwargs):
        method = request.POST.get("method")
        if method not in self.methods:
            messages.error(request, _("Select the breast used to finish feeding."))
            return super().get(request, *args, **kwargs)

        with transaction.atomic():
            timer = get_object_or_404(
                models.Timer.objects.select_for_update(),
                pk=kwargs["pk"],
                purpose_record__purpose=models.Timer.PURPOSE_BREASTFEEDING,
            )
            self.child_slug = timer.child.slug
            feeding = models.Feeding(
                child=timer.child,
                start=timer.start,
                end=timezone.now(),
                type="breast milk",
                method=method,
            )
            try:
                feeding.full_clean()
            except ValidationError as error:
                error_messages = error.message_dict.get("__all__", error.messages)
                messages.error(
                    request,
                    format_html_join(
                        " ", "{}", ((message,) for message in error_messages)
                    ),
                )
            else:
                feeding.save()
                self.feeding_id = feeding.pk
                timer.delete()
                messages.success(
                    request,
                    format_html(
                        '{} <a href="{}">{}</a>',
                        _("Breastfeeding saved."),
                        reverse("core:feeding-update", args=[feeding.pk]),
                        _("Edit entry"),
                    ),
                )
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        timer = (
            models.Timer.objects.filter(pk=kwargs["pk"]).select_related("child").first()
        )
        if timer:
            return reverse(
                "dashboard:dashboard-child", kwargs={"slug": timer.child.slug}
            )
        if getattr(self, "child_slug", None):
            return reverse(
                "dashboard:dashboard-child", kwargs={"slug": self.child_slug}
            )
        return reverse("dashboard:dashboard")


class BreastfeedingCancel(PermissionRequiredMixin, RedirectView):
    http_method_names = ["post"]
    permission_required = ("core.view_child", "core.view_timer", "core.delete_timer")

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            timer = get_object_or_404(
                models.Timer.objects.select_for_update(),
                pk=kwargs["pk"],
                purpose_record__purpose=models.Timer.PURPOSE_BREASTFEEDING,
            )
            self.child_slug = timer.child.slug
            timer.delete()
        messages.success(request, _("Breastfeeding timer discarded."))
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("dashboard:dashboard-child", kwargs={"slug": self.child_slug})


class FormulaBottleQuickLog(PermissionRequiredMixin, RedirectView):
    http_method_names = ["post"]
    permission_required = ("core.view_child", "core.add_feeding")
    allowed_amounts = {30, 40, 50, 60}

    def post(self, request, *args, **kwargs):
        child = get_object_or_404(models.Child, slug=kwargs["slug"])
        try:
            amount = int(request.POST.get("amount", ""))
        except (ValueError, TypeError):
            amount = None
        if amount not in self.allowed_amounts:
            messages.error(request, _("Invalid amount."))
            return super().get(request, *args, **kwargs)
        now = timezone.now()
        feeding = models.Feeding(
            child=child,
            start=now,
            end=now,
            type="formula",
            method="bottle",
            amount=amount,
        )
        try:
            feeding.full_clean()
        except ValidationError as error:
            error_messages = error.message_dict.get("__all__", error.messages)
            messages.error(
                request,
                format_html_join(" ", "{}", ((message,) for message in error_messages)),
            )
        else:
            feeding.save()
            messages.success(
                request,
                format_html(
                    '{} <a href="{}">{}</a>',
                    _("Formula bottle saved."),
                    reverse("core:feeding-update", args=[feeding.pk]),
                    _("Edit entry"),
                ),
            )
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("dashboard:dashboard-child", kwargs={"slug": kwargs["slug"]})


class DiaperChangeQuickLog(PermissionRequiredMixin, RedirectView):
    http_method_names = ["post"]
    permission_required = ("core.view_child", "core.add_diaperchange")
    allowed_kinds = {
        "wet": {"wet": True, "solid": False, "color": ""},
        "solid_yellow": {"wet": False, "solid": True, "color": "yellow"},
        "solid_brown": {"wet": False, "solid": True, "color": "brown"},
    }

    def post(self, request, *args, **kwargs):
        child = get_object_or_404(models.Child, slug=kwargs["slug"])
        kind = request.POST.get("kind", "")
        if kind not in self.allowed_kinds:
            messages.error(request, _("Invalid diaper change type."))
            return super().get(request, *args, **kwargs)
        attrs = self.allowed_kinds[kind]
        change = models.DiaperChange(
            child=child,
            time=timezone.now(),
            wet=attrs["wet"],
            solid=attrs["solid"],
            color=attrs["color"],
        )
        try:
            change.full_clean()
        except ValidationError as error:
            error_messages = error.message_dict.get("__all__", error.messages)
            messages.error(
                request,
                format_html_join(" ", "{}", ((message,) for message in error_messages)),
            )
        else:
            change.save()
            messages.success(
                request,
                format_html(
                    '{} <a href="{}">{}</a>',
                    _("Diaper change saved."),
                    reverse("core:diaperchange-update", args=[change.pk]),
                    _("Edit entry"),
                ),
            )
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("dashboard:dashboard-child", kwargs={"slug": kwargs["slug"]})


class TummyTimeQuickLog(PermissionRequiredMixin, RedirectView):
    http_method_names = ["post"]
    permission_required = ("core.view_child", "core.add_tummytime")
    allowed_durations = {5, 10, 15}

    def post(self, request, *args, **kwargs):
        child = get_object_or_404(models.Child, slug=kwargs["slug"])
        try:
            duration_min = int(request.POST.get("duration", ""))
        except (ValueError, TypeError):
            duration_min = None
        if duration_min not in self.allowed_durations:
            messages.error(request, _("Invalid duration."))
            return super().get(request, *args, **kwargs)
        end = timezone.now()
        start = end - timezone.timedelta(minutes=duration_min)
        tummytime = models.TummyTime(
            child=child,
            start=start,
            end=end,
        )
        try:
            tummytime.full_clean()
        except ValidationError as error:
            error_messages = error.message_dict.get("__all__", error.messages)
            messages.error(
                request,
                format_html_join(" ", "{}", ((message,) for message in error_messages)),
            )
        else:
            tummytime.save()
            messages.success(
                request,
                format_html(
                    '{} <a href="{}">{}</a>',
                    _("Tummy time saved."),
                    reverse("core:tummytime-update", args=[tummytime.pk]),
                    _("Edit entry"),
                ),
            )
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("dashboard:dashboard-child", kwargs={"slug": kwargs["slug"]})


class HeadCircumferenceList(
    PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView
):
    model = models.HeadCircumference
    template_name = "core/head_circumference_list.html"
    permission_required = ("core.view_head_circumference",)
    filterset_class = filters.HeadCircumferenceFilter


class HeadCircumferenceAdd(CoreAddView):
    model = models.HeadCircumference
    template_name = "core/head_circumference_form.html"
    permission_required = ("core.add_head_circumference",)
    form_class = forms.HeadCircumferenceForm
    success_url = reverse_lazy("core:head-circumference-list")


class HeadCircumferenceUpdate(CoreUpdateView):
    model = models.HeadCircumference
    template_name = "core/head_circumference_form.html"
    permission_required = ("core.change_head_circumference",)
    form_class = forms.HeadCircumferenceForm
    success_url = reverse_lazy("core:head-circumference-list")


class HeadCircumferenceDelete(CoreDeleteView):
    model = models.HeadCircumference
    template_name = "core/head_circumference_confirm_delete.html"
    permission_required = ("core.delete_head_circumference",)
    success_url = reverse_lazy("core:head-circumference-list")


class HeightList(PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView):
    model = models.Height
    template_name = "core/height_list.html"
    permission_required = ("core.view_height",)
    filterset_class = filters.HeightFilter


class HeightAdd(CoreAddView):
    model = models.Height
    permission_required = ("core.add_height",)
    form_class = forms.HeightForm
    success_url = reverse_lazy("core:height-list")


class HeightUpdate(CoreUpdateView):
    model = models.Height
    permission_required = ("core.change_height",)
    form_class = forms.HeightForm
    success_url = reverse_lazy("core:height-list")


class HeightDelete(CoreDeleteView):
    model = models.Height
    permission_required = ("core.delete_height",)
    success_url = reverse_lazy("core:height-list")


class MedicationList(
    PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView
):
    model = models.Medication
    template_name = "core/medication_list.html"
    permission_required = ("core.view_medication",)
    filterset_class = filters.MedicationFilter


class MedicationAdd(CoreAddView):
    model = models.Medication
    permission_required = ("core.add_medication",)
    form_class = forms.MedicationForm
    success_url = reverse_lazy("core:medication-list")


class MedicationUpdate(CoreUpdateView):
    model = models.Medication
    permission_required = ("core.change_medication",)
    form_class = forms.MedicationForm
    success_url = reverse_lazy("core:medication-list")


class MedicationDelete(CoreDeleteView):
    model = models.Medication
    permission_required = ("core.delete_medication",)
    success_url = reverse_lazy("core:medication-list")


class NoteList(PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView):
    model = models.Note
    template_name = "core/note_list.html"
    permission_required = ("core.view_note",)
    filterset_class = filters.NoteFilter


class NoteAdd(CoreAddView):
    model = models.Note
    permission_required = ("core.add_note",)
    form_class = forms.NoteForm
    success_url = reverse_lazy("core:note-list")


class NoteUpdate(CoreUpdateView):
    model = models.Note
    permission_required = ("core.change_note",)
    form_class = forms.NoteForm
    success_url = reverse_lazy("core:note-list")


class NoteDelete(CoreDeleteView):
    model = models.Note
    permission_required = ("core.delete_note",)
    success_url = reverse_lazy("core:note-list")


class PumpingList(PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView):
    model = models.Pumping
    template_name = "core/pumping_list.html"
    permission_required = ("core.view_pumping",)
    filterset_class = filters.PumpingFilter


class PumpingAdd(CoreAddView):
    model = models.Pumping
    permission_required = ("core.add_pumping",)
    form_class = forms.PumpingForm
    success_url = reverse_lazy("core:pumping-list")
    success_message = _("%(model)s entry added!")


class PumpingUpdate(CoreUpdateView):
    model = models.Pumping
    permission_required = ("core.change_pumping",)
    form_class = forms.PumpingForm
    success_url = reverse_lazy("core:pumping-list")
    success_message = _("%(model)s entry for %(child)s updated.")


class PumpingDelete(CoreDeleteView):
    model = models.Pumping
    permission_required = ("core.delete_pumping",)
    success_url = reverse_lazy("core:pumping-list")


class SleepList(PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView):
    model = models.Sleep
    template_name = "core/sleep_list.html"
    permission_required = ("core.view_sleep",)
    filterset_class = filters.SleepFilter


class SleepAdd(CoreAddView):
    model = models.Sleep
    permission_required = ("core.add_sleep",)
    form_class = forms.SleepForm
    success_url = reverse_lazy("core:sleep-list")


class SleepUpdate(CoreUpdateView):
    model = models.Sleep
    permission_required = ("core.change_sleep",)
    form_class = forms.SleepForm
    success_url = reverse_lazy("core:sleep-list")


class SleepDelete(CoreDeleteView):
    model = models.Sleep
    permission_required = ("core.delete_sleep",)
    success_url = reverse_lazy("core:sleep-list")


class TagAdminList(
    PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView
):
    model = models.Tag
    template_name = "core/tag_list.html"
    permission_required = ("core.view_tags",)
    filterset_class = filters.TagFilter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(Count("core_tagged_items"))
            .order_by(Lower("name"))
        )


class TagAdminDetail(PermissionRequiredMixin, DetailView):
    model = models.Tag
    permission_required = ("core.view_tags",)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            Count("feeding"),
            Count("diaperchange"),
            Count("pumping"),
            Count("sleep"),
            Count("tummytime"),
            Count("bmi"),
            Count("headcircumference"),
            Count("height"),
            Count("temperature"),
            Count("weight"),
        )
        return qs


class TagAdminAdd(CoreAddView):
    model = models.Tag
    permission_required = ("core.add_tag",)
    form_class = forms.TagAdminForm
    success_url = reverse_lazy("core:tag-list")


class TagAdminUpdate(CoreUpdateView):
    model = models.Tag
    permission_required = ("core.change_tag",)
    form_class = forms.TagAdminForm
    success_url = reverse_lazy("core:tag-list")


class TagAdminDelete(CoreDeleteView):
    model = models.Tag
    permission_required = ("core.delete_tag",)
    success_url = reverse_lazy("core:tag-list")

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(Count("core_tagged_items"))


class TemperatureList(
    PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView
):
    model = models.Temperature
    template_name = "core/temperature_list.html"
    permission_required = ("core.view_temperature",)
    filterset_class = filters.TemperatureFilter


class TemperatureAdd(CoreAddView):
    model = models.Temperature
    permission_required = ("core.add_temperature",)
    form_class = forms.TemperatureForm
    success_url = reverse_lazy("core:temperature-list")
    success_message = _("%(model)s reading added!")


class TemperatureUpdate(CoreUpdateView):
    model = models.Temperature
    permission_required = ("core.change_temperature",)
    form_class = forms.TemperatureForm
    success_url = reverse_lazy("core:temperature-list")
    success_message = _("%(model)s reading for %(child)s updated.")


class TemperatureDelete(CoreDeleteView):
    model = models.Temperature
    permission_required = ("core.delete_temperature",)
    success_url = reverse_lazy("core:temperature-list")


class Timeline(LoginRequiredMixin, TemplateView):
    template_name = "timeline/timeline.html"

    # Show the overall timeline or a child timeline if one Child instance.
    def get(self, request, *args, **kwargs):
        children = models.Child.objects.count()
        if children == 1:
            return HttpResponseRedirect(
                reverse("core:child", args={models.Child.objects.first().slug})
            )
        return super(Timeline, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Timeline, self).get_context_data(**kwargs)
        date = self.request.GET.get("date", str(timezone.localdate()))
        _prepare_timeline_context_data(context, date)
        return context


class TimerList(PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView):
    model = models.Timer
    template_name = "core/timer_list.html"
    permission_required = ("core.view_timer",)
    filterset_fields = ("user",)

    def get_queryset(self):
        return super().get_queryset().filter(purpose_record__isnull=True)


class TimerDetail(PermissionRequiredMixin, DetailView):
    model = models.Timer
    permission_required = ("core.view_timer",)

    def get_queryset(self):
        return super().get_queryset().filter(purpose_record__isnull=True)


class TimerAdd(PermissionRequiredMixin, CreateView):
    model = models.Timer
    permission_required = ("core.add_timer",)
    form_class = forms.TimerForm

    def get_form_kwargs(self):
        kwargs = super(TimerAdd, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse("core:timer-detail", kwargs={"pk": self.object.pk})


class TimerUpdate(CoreUpdateView):
    model = models.Timer
    permission_required = ("core.change_timer",)
    form_class = forms.TimerForm
    success_url = reverse_lazy("core:timer-list")

    def get_queryset(self):
        return super().get_queryset().filter(purpose_record__isnull=True)

    def get_form_kwargs(self):
        kwargs = super(TimerUpdate, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_success_url(self):
        instance = self.get_object()
        return reverse("core:timer-detail", kwargs={"pk": instance.pk})


class TimerAddQuick(PermissionRequiredMixin, RedirectView):
    http_method_names = ["post"]
    permission_required = ("core.add_timer",)

    def post(self, request, *args, **kwargs):
        instance = models.Timer.objects.create(user=request.user)
        # Find child from child pk in POST
        child_id = request.POST.get("child", False)
        child = models.Child.objects.get(pk=child_id) if child_id else None
        if child:
            instance.child = child
        # Add child relationship if there is only Child instance.
        elif models.Child.count() == 1:
            instance.child = models.Child.objects.first()
        instance.save()
        self.url = request.GET.get(
            "next", reverse("core:timer-detail", args={instance.id})
        )
        return super(TimerAddQuick, self).get(request, *args, **kwargs)


class TimerRestart(PermissionRequiredMixin, RedirectView):
    http_method_names = ["post"]
    permission_required = ("core.change_timer",)

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(
            models.Timer, id=kwargs["pk"], purpose_record__isnull=True
        )
        instance.restart()
        messages.success(request, "{} restarted.".format(instance))
        return super(TimerRestart, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("core:timer-detail", kwargs={"pk": kwargs["pk"]})


class TimerDelete(CoreDeleteView):
    model = models.Timer
    permission_required = ("core.delete_timer",)
    success_url = reverse_lazy("core:timer-list")

    def get_queryset(self):
        return super().get_queryset().filter(purpose_record__isnull=True)


class TummyTimeList(
    PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView
):
    model = models.TummyTime
    template_name = "core/tummytime_list.html"
    permission_required = ("core.view_tummytime",)
    filterset_class = filters.TummyTimeFilter


class TummyTimeAdd(CoreAddView):
    model = models.TummyTime
    permission_required = ("core.add_tummytime",)
    form_class = forms.TummyTimeForm
    success_url = reverse_lazy("core:tummytime-list")


class TummyTimeUpdate(CoreUpdateView):
    model = models.TummyTime
    permission_required = ("core.change_tummytime",)
    form_class = forms.TummyTimeForm
    success_url = reverse_lazy("core:tummytime-list")


class TummyTimeDelete(CoreDeleteView):
    model = models.TummyTime
    permission_required = ("core.delete_tummytime",)
    success_url = reverse_lazy("core:tummytime-list")


class WeightList(PermissionRequiredMixin, BabyBuddyPaginatedView, BabyBuddyFilterView):
    model = models.Weight
    template_name = "core/weight_list.html"
    permission_required = ("core.view_weight",)
    filterset_class = filters.WeightFilter


class WeightAdd(CoreAddView):
    model = models.Weight
    permission_required = ("core.add_weight",)
    form_class = forms.WeightForm
    success_url = reverse_lazy("core:weight-list")


class WeightUpdate(CoreUpdateView):
    model = models.Weight
    permission_required = ("core.change_weight",)
    form_class = forms.WeightForm
    success_url = reverse_lazy("core:weight-list")


class WeightDelete(CoreDeleteView):
    model = models.Weight
    permission_required = ("core.delete_weight",)
    success_url = reverse_lazy("core:weight-list")
