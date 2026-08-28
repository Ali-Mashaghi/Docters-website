from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.consultations.models import ConsultationRequest
from apps.articles.models import Article
from apps.doctors.models import Doctor, DoctorManager

MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\x0d\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)


class PermissionTestCase(TestCase):
    def setUp(self):
        self.image = SimpleUploadedFile(
            "test.png", MINIMAL_PNG, content_type="image/png"
        )
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="testpass123",
        )
        self.staff_a = User.objects.create_user(
            username="staff_a",
            password="testpass123",
            is_staff=True,
        )
        self.staff_b = User.objects.create_user(
            username="staff_b",
            password="testpass123",
            is_staff=True,
        )

        self.doctor_a = Doctor.objects.create(
            name="دکتر الف",
            slug="doctor-a",
            specialty="پوست",
            bio="بیوگرافی",
            profile_image=self.image,
        )
        self.doctor_b = Doctor.objects.create(
            name="دکتر ب",
            slug="doctor-b",
            specialty="قلب",
            bio="بیوگرافی",
            profile_image=SimpleUploadedFile(
                "test2.png", MINIMAL_PNG, content_type="image/png"
            ),
        )

        DoctorManager.objects.create(user=self.staff_a, doctor=self.doctor_a)
        DoctorManager.objects.create(user=self.staff_b, doctor=self.doctor_b)

        self.request_a = ConsultationRequest.objects.create(
            doctor=self.doctor_a,
            name="کاربر الف",
            phone="09121111111",
        )
        self.request_b = ConsultationRequest.objects.create(
            doctor=self.doctor_b,
            name="کاربر ب",
            phone="09122222222",
        )

        self.client = Client()

    def test_staff_a_cannot_access_doctor_b_consultation(self):
        self.client.login(username="staff_a", password="testpass123")
        url = reverse(
            "dashboard:consultation_detail",
            kwargs={"pk": self.request_b.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_a_can_access_own_consultation(self):
        self.client.login(username="staff_a", password="testpass123")
        url = reverse(
            "dashboard:consultation_detail",
            kwargs={"pk": self.request_a.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_access_all(self):
        self.client.login(username="admin", password="testpass123")
        url = reverse(
            "dashboard:consultation_detail",
            kwargs={"pk": self.request_b.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_non_staff_cannot_access_dashboard(self):
        user = User.objects.create_user(
            username="regular",
            password="testpass123",
        )
        self.client.login(username="regular", password="testpass123")
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 403)

    def test_consultation_form_submission(self):
        url = reverse(
            "doctors:doctor_detail",
            kwargs={"slug": self.doctor_a.slug},
        )
        response = self.client.post(url, {
            "name": "علی احمدی",
            "phone": "09123456789",
            "email": "ali@test.com",
            "message": "سلام",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ConsultationRequest.objects.filter(name="علی احمدی").exists()
        )


class ManagerAdminTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="testpass123",
        )
        self.staff = User.objects.create_user(
            username="staff_a",
            password="testpass123",
            is_staff=True,
        )
        self.client = Client()

    def test_staff_cannot_access_managers(self):
        self.client.login(username="staff_a", password="testpass123")
        response = self.client.get(reverse("dashboard:managers"))
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_create_manager(self):
        self.client.login(username="admin", password="testpass123")
        response = self.client.post(
            reverse("dashboard:manager_create"),
            {
                "username": "new_manager",
                "email": "mgr@test.com",
                "first_name": "مدیر",
                "last_name": "جدید",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="new_manager")
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_can_assign_doctors(self):
        image = SimpleUploadedFile(
            "doc.png",
            MINIMAL_PNG,
            content_type="image/png",
        )
        doctor = Doctor.objects.create(
            name="دکتر تست",
            slug="doc-test",
            specialty="عمومی",
            bio="bio",
            profile_image=image,
        )
        manager = User.objects.create_user(
            username="mgr1",
            password="testpass123",
            is_staff=True,
        )

        self.client.login(username="admin", password="testpass123")
        response = self.client.post(
            reverse("dashboard:manager_assign", kwargs={"pk": manager.pk}),
            {"doctors": [doctor.pk]},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            DoctorManager.objects.filter(user=manager, doctor=doctor).exists()
        )


class ArticleDashboardTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin",
            password="testpass123",
        )
        self.staff = User.objects.create_user(
            username="staff_a",
            password="testpass123",
            is_staff=True,
        )
        self.client = Client()

    def test_staff_cannot_manage_articles(self):
        self.client.login(username="staff_a", password="testpass123")
        response = self.client.get(reverse("dashboard:articles"))
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_create_article(self):
        self.client.login(username="admin", password="testpass123")
        response = self.client.post(
            reverse("dashboard:article_create"),
            {
                "title": "مقاله تست",
                "slug": "test-article",
                "excerpt": "خلاصه مقاله",
                "content": "متن کامل مقاله",
                "is_published": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        article = Article.objects.get(slug="test-article")
        self.assertTrue(article.is_published)
        self.assertEqual(article.author, self.superuser)
