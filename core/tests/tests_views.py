# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.http import Http404
from django.test import RequestFactory, TestCase
from django.test import Client as HttpClient
from django.utils import timezone

from faker import Faker

from core import models
from core.views import BreastfeedingCancel, BreastfeedingFinish


class ViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ViewsTestCase, cls).setUpClass()
        fake = Faker()
        call_command("migrate", verbosity=0)
        call_command("fake", verbosity=0)

        cls.c = HttpClient()

        fake_user = fake.simple_profile()
        cls.credentials = {
            "username": fake_user["username"],
            "password": fake.password(),
        }
        cls.user = get_user_model().objects.create_user(
            is_superuser=True, **cls.credentials
        )

        cls.c.login(**cls.credentials)

    def test_bmi_views(self):
        page = self.c.get("/bmi/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/bmi/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.BMI.objects.first()
        page = self.c.get("/bmi/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/bmi/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_child_views(self):
        page = self.c.get("/children/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/children/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.Child.objects.first()
        page = self.c.get("/children/{}/".format(entry.slug))
        self.assertEqual(page.status_code, 200)
        page = self.c.get(
            "/children/{}/".format(entry.slug),
            {"date": timezone.localdate() - timezone.timedelta(days=1)},
        )
        self.assertEqual(page.status_code, 200)

        page = self.c.get("/children/{}/edit/".format(entry.slug))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/children/{}/delete/".format(entry.slug))
        self.assertEqual(page.status_code, 200)

    def test_diaperchange_views(self):
        page = self.c.get("/changes/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/changes/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.DiaperChange.objects.first()
        page = self.c.get("/changes/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/changes/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_feeding_views(self):
        page = self.c.get("/feedings/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/feedings/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.Feeding.objects.first()
        page = self.c.get("/feedings/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/feedings/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_headcircumference_views(self):
        page = self.c.get("/head-circumference/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/head-circumference/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.HeadCircumference.objects.first()
        page = self.c.get("/head-circumference/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/head-circumference/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_height_views(self):
        page = self.c.get("/height/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/height/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.Height.objects.first()
        page = self.c.get("/height/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/height/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_note_views(self):
        page = self.c.get("/notes/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/notes/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.Note.objects.first()
        page = self.c.get("/notes/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/notes/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_pumping_views(self):
        page = self.c.get("/pumping/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/pumping/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.Pumping.objects.first()
        page = self.c.get("/pumping/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/pumping/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_sleep_views(self):
        page = self.c.get("/sleep/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/sleep/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.Sleep.objects.first()
        page = self.c.get("/sleep/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/sleep/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_tags_views(self):
        page = self.c.get("/tags/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/tags/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.Tag.objects.first()
        page = self.c.get("/tags/{}/".format(entry.slug))
        self.assertEqual(page.status_code, 200)
        entry = models.Tag.objects.first()
        page = self.c.get("/tags/{}/edit".format(entry.slug))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/tags/{}/delete/".format(entry.slug))
        self.assertEqual(page.status_code, 200)

    def test_temperature_views(self):
        page = self.c.get("/temperature/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/temperature/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.Temperature.objects.first()
        page = self.c.get("/temperature/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/temperature/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_medication_views(self):
        page = self.c.get("/medication/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/medication/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.Medication.objects.first()
        page = self.c.get("/medication/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/medication/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_timer_views(self):
        page = self.c.get("/timers/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/timers/add/")
        self.assertEqual(page.status_code, 200)

        page = self.c.get("/timers/add/quick/")
        self.assertEqual(page.status_code, 405)
        page = self.c.post("/timers/add/quick/", follow=True)
        self.assertEqual(page.status_code, 200)

        entry = models.Timer.objects.first()
        page = self.c.get("/timers/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/timers/{}/edit/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/timers/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

        page = self.c.get("/timers/{}/restart/".format(entry.id))
        self.assertEqual(page.status_code, 405)
        page = self.c.post("/timers/{}/restart/".format(entry.id), follow=True)
        self.assertEqual(page.status_code, 200)

    def test_timeline_views(self):
        child = models.Child.objects.first()
        response = self.c.get("/timeline/")
        self.assertRedirects(response, "/children/{}/".format(child.slug))

        models.Child.objects.create(
            first_name="Second", last_name="Child", birth_date="2000-01-01"
        )
        response = self.c.get("/timeline/")
        self.assertEqual(response.status_code, 200)

    def test_tummytime_views(self):
        page = self.c.get("/tummy-time/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/tummy-time/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.TummyTime.objects.first()
        page = self.c.get("/tummy-time/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/tummy-time/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)

    def test_weight_views(self):
        page = self.c.get("/weight/")
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/weight/add/")
        self.assertEqual(page.status_code, 200)

        entry = models.Weight.objects.first()
        page = self.c.get("/weight/{}/".format(entry.id))
        self.assertEqual(page.status_code, 200)
        page = self.c.get("/weight/{}/delete/".format(entry.id))
        self.assertEqual(page.status_code, 200)


class BreastfeedingQuickLogViewsTestCase(TestCase):
    def setUp(self):
        call_command("migrate", verbosity=0)
        self.credentials = {"username": "caregiver", "password": "password"}
        self.user = get_user_model().objects.create_user(
            is_superuser=True, **self.credentials
        )
        self.client.login(**self.credentials)
        self.child = models.Child.objects.create(
            first_name="Quick", last_name="Log", birth_date=timezone.localdate()
        )

    def start_url(self):
        return "/children/{}/breastfeeding/start/".format(self.child.slug)

    def create_timer(self, start=None, purpose=models.Timer.PURPOSE_BREASTFEEDING):
        timer = models.Timer.objects.create(
            child=self.child,
            start=start or timezone.now() - timezone.timedelta(minutes=20),
            user=self.user,
        )
        if purpose == models.Timer.PURPOSE_BREASTFEEDING:
            models.TimerPurpose.objects.create(
                timer=timer, child=self.child, purpose=purpose
            )
        return timer

    def test_start_is_post_only_and_idempotent(self):
        self.assertEqual(self.client.get(self.start_url()).status_code, 405)
        response = self.client.post(self.start_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        timer = models.Timer.objects.get(
            child=self.child,
            purpose_record__purpose=models.Timer.PURPOSE_BREASTFEEDING,
        )
        self.assertEqual(timer.user, self.user)

        response = self.client.post(self.start_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            models.Timer.objects.filter(
                child=self.child,
                purpose_record__purpose=models.Timer.PURPOSE_BREASTFEEDING,
            ).count(),
            1,
        )
        self.assertContains(response, "already running")

    def test_start_requires_permissions(self):
        self.client.logout()
        user = get_user_model().objects.create_user(
            username="unprivileged", password="password"
        )
        self.client.login(username=user.username, password="password")
        self.assertEqual(self.client.post(self.start_url()).status_code, 403)

    def test_finish_methods_create_normal_feeding_and_delete_timer(self):
        for method in ("left breast", "right breast", "both breasts"):
            with self.subTest(method=method):
                timer = self.create_timer()
                response = self.client.post(
                    "/timers/{}/breastfeeding/finish/".format(timer.pk),
                    {"method": method},
                    follow=True,
                )
                self.assertEqual(response.status_code, 200)
                feeding = models.Feeding.objects.get()
                self.assertEqual(feeding.child, self.child)
                self.assertEqual(feeding.start, timer.start)
                self.assertEqual(feeding.type, "breast milk")
                self.assertEqual(feeding.method, method)
                self.assertGreater(feeding.duration, timezone.timedelta())
                self.assertFalse(models.Timer.objects.filter(pk=timer.pk).exists())
                self.assertContains(response, "/feedings/{}/".format(feeding.pk))
                feeding.delete()

    def test_finish_rejects_invalid_method_without_deleting_timer(self):
        timer = self.create_timer()
        response = self.client.post(
            "/timers/{}/breastfeeding/finish/".format(timer.pk),
            {"method": "bottle"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(models.Timer.objects.filter(pk=timer.pk).exists())
        self.assertFalse(models.Feeding.objects.exists())
        self.assertContains(response, "Select the breast used")

    def test_finish_rejects_generic_timer(self):
        timer = self.create_timer(purpose=models.Timer.PURPOSE_GENERIC)
        request = RequestFactory().post(
            "/timers/{}/breastfeeding/finish/".format(timer.pk),
            {"method": "both breasts"},
        )
        request.user = self.user
        with self.assertRaises(Http404):
            BreastfeedingFinish.as_view()(request, pk=timer.pk)
        self.assertTrue(models.Timer.objects.filter(pk=timer.pk).exists())

    def test_cancel_is_post_only_and_discards_without_feeding(self):
        timer = self.create_timer()
        url = "/timers/{}/breastfeeding/cancel/".format(timer.pk)
        self.assertEqual(self.client.get(url).status_code, 405)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(models.Timer.objects.filter(pk=timer.pk).exists())
        self.assertFalse(models.Feeding.objects.exists())
        self.assertContains(response, "timer discarded")

    def test_cancel_rejects_generic_timer(self):
        timer = self.create_timer(purpose=models.Timer.PURPOSE_GENERIC)
        request = RequestFactory().post(
            "/timers/{}/breastfeeding/cancel/".format(timer.pk)
        )
        request.user = self.user
        with self.assertRaises(Http404):
            BreastfeedingCancel.as_view()(request, pk=timer.pk)
        self.assertTrue(models.Timer.objects.filter(pk=timer.pk).exists())

    def test_cancel_requires_permissions(self):
        timer = self.create_timer()
        self.client.logout()
        user = get_user_model().objects.create_user(
            username="cancel-unprivileged", password="password"
        )
        self.client.login(username=user.username, password="password")
        response = self.client.post("/timers/{}/breastfeeding/cancel/".format(timer.pk))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(models.Timer.objects.filter(pk=timer.pk).exists())

    def test_overlap_keeps_timer_and_links_conflicting_feeding(self):
        timer = self.create_timer()
        conflicting = models.Feeding.objects.create(
            child=self.child,
            start=timer.start + timezone.timedelta(minutes=5),
            end=timer.start + timezone.timedelta(minutes=10),
            type="breast milk",
            method="left breast",
        )
        response = self.client.post(
            "/timers/{}/breastfeeding/finish/".format(timer.pk),
            {"method": "both breasts"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(models.Timer.objects.filter(pk=timer.pk).exists())
        self.assertEqual(models.Feeding.objects.count(), 1)
        self.assertContains(response, "/feedings/{}/".format(conflicting.pk))


class FormulaBottleQuickLogTestCase(TestCase):
    def setUp(self):
        call_command("migrate", verbosity=0)
        self.credentials = {"username": "formula-caregiver", "password": "password"}
        self.user = get_user_model().objects.create_user(
            is_superuser=True, **self.credentials
        )
        self.client.login(**self.credentials)
        self.child = models.Child.objects.create(
            first_name="Formula", last_name="Baby", birth_date=timezone.localdate()
        )

    def url(self):
        return "/children/{}/quick/formula-bottle/".format(self.child.slug)

    def test_get_returns_405(self):
        self.assertEqual(self.client.get(self.url()).status_code, 405)

    def test_valid_amounts_create_feeding_and_redirect(self):
        for amount in [30, 40, 50, 60]:
            with self.subTest(amount=amount):
                response = self.client.post(self.url(), {"amount": amount}, follow=True)
                self.assertEqual(response.status_code, 200)
                feeding = models.Feeding.objects.filter(
                    child=self.child, type="formula", method="bottle", amount=amount
                ).last()
                self.assertIsNotNone(feeding)
                self.assertContains(response, "Formula bottle saved")
                self.assertContains(response, "/feedings/{}/".format(feeding.pk))
                feeding.delete()

    def test_invalid_amount_creates_nothing(self):
        for bad in ["", "0", "25", "abc", "31"]:
            with self.subTest(amount=bad):
                count_before = models.Feeding.objects.count()
                response = self.client.post(self.url(), {"amount": bad}, follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(models.Feeding.objects.count(), count_before)

    def test_requires_permission(self):
        self.client.logout()
        unprivileged = get_user_model().objects.create_user(
            username="formula-unpriv", password="password"
        )
        self.client.login(username="formula-unpriv", password="password")
        response = self.client.post(self.url(), {"amount": 30})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.Feeding.objects.count(), 0)

    def test_formula_feeding_fields(self):
        self.client.post(self.url(), {"amount": 50}, follow=True)
        feeding = models.Feeding.objects.get(child=self.child)
        self.assertEqual(feeding.type, "formula")
        self.assertEqual(feeding.method, "bottle")
        self.assertEqual(feeding.amount, 50)


class DiaperChangeQuickLogTestCase(TestCase):
    def setUp(self):
        call_command("migrate", verbosity=0)
        self.credentials = {"username": "diaper-caregiver", "password": "password"}
        self.user = get_user_model().objects.create_user(
            is_superuser=True, **self.credentials
        )
        self.client.login(**self.credentials)
        self.child = models.Child.objects.create(
            first_name="Diaper", last_name="Baby", birth_date=timezone.localdate()
        )

    def url(self):
        return "/children/{}/quick/diaper-change/".format(self.child.slug)

    def test_get_returns_405(self):
        self.assertEqual(self.client.get(self.url()).status_code, 405)

    def test_wet_creates_correct_change(self):
        response = self.client.post(self.url(), {"kind": "wet"}, follow=True)
        self.assertEqual(response.status_code, 200)
        change = models.DiaperChange.objects.get(child=self.child)
        self.assertTrue(change.wet)
        self.assertFalse(change.solid)
        self.assertEqual(change.color, "")
        self.assertContains(response, "Diaper change saved")

    def test_solid_yellow_creates_correct_change(self):
        response = self.client.post(self.url(), {"kind": "solid_yellow"}, follow=True)
        self.assertEqual(response.status_code, 200)
        change = models.DiaperChange.objects.get(child=self.child)
        self.assertFalse(change.wet)
        self.assertTrue(change.solid)
        self.assertEqual(change.color, "yellow")

    def test_solid_brown_creates_correct_change(self):
        response = self.client.post(self.url(), {"kind": "solid_brown"}, follow=True)
        self.assertEqual(response.status_code, 200)
        change = models.DiaperChange.objects.get(child=self.child)
        self.assertFalse(change.wet)
        self.assertTrue(change.solid)
        self.assertEqual(change.color, "brown")

    def test_invalid_kind_creates_nothing(self):
        for bad in ["", "yellow", "dry", "both"]:
            with self.subTest(kind=bad):
                count_before = models.DiaperChange.objects.count()
                response = self.client.post(self.url(), {"kind": bad}, follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(models.DiaperChange.objects.count(), count_before)

    def test_requires_permission(self):
        self.client.logout()
        get_user_model().objects.create_user(
            username="diaper-unpriv", password="password"
        )
        self.client.login(username="diaper-unpriv", password="password")
        response = self.client.post(self.url(), {"kind": "wet"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.DiaperChange.objects.count(), 0)


class TummyTimeQuickLogTestCase(TestCase):
    def setUp(self):
        call_command("migrate", verbosity=0)
        self.credentials = {"username": "tummy-caregiver", "password": "password"}
        self.user = get_user_model().objects.create_user(
            is_superuser=True, **self.credentials
        )
        self.client.login(**self.credentials)
        self.child = models.Child.objects.create(
            first_name="Tummy", last_name="Baby", birth_date=timezone.localdate()
        )

    def url(self):
        return "/children/{}/quick/tummy-time/".format(self.child.slug)

    def test_get_returns_405(self):
        self.assertEqual(self.client.get(self.url()).status_code, 405)

    def test_valid_durations_create_tummytime(self):
        for minutes in [5, 10, 15]:
            with self.subTest(minutes=minutes):
                response = self.client.post(
                    self.url(), {"duration": minutes}, follow=True
                )
                self.assertEqual(response.status_code, 200)
                tt = models.TummyTime.objects.filter(child=self.child).last()
                self.assertIsNotNone(tt)
                self.assertAlmostEqual(tt.duration.seconds, minutes * 60, delta=5)
                self.assertContains(response, "Tummy time saved")
                self.assertContains(response, "/tummy-time/{}/".format(tt.pk))
                tt.delete()

    def test_invalid_duration_creates_nothing(self):
        for bad in ["", "0", "3", "20", "abc"]:
            with self.subTest(duration=bad):
                count_before = models.TummyTime.objects.count()
                response = self.client.post(self.url(), {"duration": bad}, follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(models.TummyTime.objects.count(), count_before)

    def test_requires_permission(self):
        self.client.logout()
        get_user_model().objects.create_user(
            username="tummy-unpriv", password="password"
        )
        self.client.login(username="tummy-unpriv", password="password")
        response = self.client.post(self.url(), {"duration": 5})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(models.TummyTime.objects.count(), 0)

    def test_start_end_relationship(self):
        self.client.post(self.url(), {"duration": 10}, follow=True)
        tt = models.TummyTime.objects.get(child=self.child)
        delta = tt.end - tt.start
        self.assertAlmostEqual(delta.seconds, 600, delta=5)
