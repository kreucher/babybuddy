# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client as HttpClient
from django.contrib.auth import get_user_model
from django.core.management import call_command

from faker import Faker

from core.models import Child, Timer, TimerPurpose


class ViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ViewsTestCase, cls).setUpClass()
        fake = Faker()
        call_command("migrate", verbosity=0)

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

    def test_dashboard_views(self):
        page = self.c.get("/dashboard/")
        self.assertEqual(page.url, "/welcome/")

        call_command("fake", verbosity=0, children=1, days=1)
        child = Child.objects.first()
        page = self.c.get("/dashboard/")
        self.assertEqual(page.url, "/children/{}/dashboard/".format(child.slug))

        page = self.c.get("/dashboard/")
        self.assertEqual(page.url, "/children/{}/dashboard/".format(child.slug))
        # Test the actual child dashboard (including cards).
        # TODO: Test cards more granularly.
        page = self.c.get("/children/{}/dashboard/".format(child.slug))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Start breastfeeding")
        self.assertNotContains(page, "Finish and save")

        timer = Timer.objects.create(
            child=child,
            user=self.user,
        )
        TimerPurpose.objects.create(
            timer=timer, child=child, purpose=Timer.PURPOSE_BREASTFEEDING
        )
        page = self.c.get("/children/{}/dashboard/".format(child.slug))
        self.assertContains(page, "Finish and save")
        self.assertNotContains(page, "Start breastfeeding")
        self.assertContains(page, "data-breastfeeding-start")

        # The purpose-specific timer is visible outside the dashboard too.
        page = self.c.get("/feedings/")
        self.assertContains(page, "Breastfeeding in progress")
        self.assertContains(page, "/children/{}/dashboard/".format(child.slug))
        timer.delete()

        Child.objects.create(
            first_name="Second", last_name="Child", birth_date="2000-01-01"
        )
        page = self.c.get("/dashboard/")
        self.assertEqual(page.status_code, 200)
