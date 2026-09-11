from io import BytesIO

from PIL import Image
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.consultations.models import ConsultationRequest
from apps.articles.models import Article
from apps.doctors.models import Doctor, DoctorManager
from apps.dashboard.forms import DoctorForm

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
            birth_date="1370/01/01",
            job="پزشک",
            marital_status="married",
            address="تهران",
            medical_history="هیچکدام",
            surgery_history="no",
            surgery_details="",
            cold_sore="no",
            medication_history="هیچکدام",
            substance_use="هیچکدام",
            referral_source="friend",
        )
        self.request_b = ConsultationRequest.objects.create(
            doctor=self.doctor_b,
            name="کاربر ب",
            phone="09122222222",
            birth_date="1375/02/02",
            job="مهندس",
            marital_status="single",
            address="شیراز",
            medical_history="دیابت",
            surgery_history="yes",
            surgery_details="آپاندیس",
            cold_sore="yes",
            medication_history="ویتامین‌های D،A،K،E",
            substance_use="قلیان",
            referral_source="google",
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

    def test_staff_can_save_consultation_notes_and_four_case_images(self):
        self.client.login(username="staff_a", password="testpass123")
        url = reverse(
            "dashboard:consultation_detail",
            kwargs={"pk": self.request_a.pk},
        )
        files = {}
        for index in range(1, 5):
            image_file = BytesIO()
            Image.new("RGB", (2, 2), "white").save(image_file, format="PNG")
            image_file.seek(0)
            files[f"admin_image_{index}"] = SimpleUploadedFile(
                f"case-{index}.png",
                image_file.read(),
                content_type="image/png",
            )

        response = self.client.post(
            url,
            {"admin_notes": "نیاز به بررسی پزشک دارد.", **files},
        )

        self.assertRedirects(response, url)
        self.request_a.refresh_from_db()
        self.assertEqual(self.request_a.admin_notes, "نیاز به بررسی پزشک دارد.")
        for index in range(1, 5):
            self.assertTrue(
                getattr(self.request_a, f"admin_image_{index}").name.startswith(
                    "consultations/admin/"
                )
            )

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
            "doctors:doctor_consultation",
            kwargs={"slug": self.doctor_a.slug},
        )
        response = self.client.post(url, {
            "name": "علی احمدی",
            "phone": "09123456789",
            "birth_date": "1372/05/12",
            "job": "معلم",
            "marital_status": "single",
            "address": "تهران، خیابان انقلاب",
            "medical_history": ["allergy", "thyroid"],
            "surgery_history": "no",
            "surgery_details": "این مقدار نباید ذخیره شود",
            "cold_sore": "no",
            "medication_history": ["vitamins"],
            "other_medications": "آنتی‌بیوتیک",
            "substance_use": ["none"],
            "referral_source": "instagram",
            "message": "سلام",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ConsultationRequest.objects.filter(name="علی احمدی").exists()
        )
        consultation = ConsultationRequest.objects.get(name="علی احمدی")
        self.assertIn("حساسیت و آلرژی", consultation.medical_history)
        self.assertEqual(consultation.surgery_history, "no")
        self.assertEqual(consultation.surgery_details, "")
        self.assertEqual(consultation.other_medications, "آنتی‌بیوتیک")

    def test_none_choice_cannot_be_combined_with_other_history(self):
        form_data = {
            "name": "کاربر تست",
            "phone": "09123456789",
            "birth_date": "1372/05/12",
            "job": "معلم",
            "marital_status": "single",
            "address": "تهران",
            "medical_history": ["none", "diabetes"],
            "surgery_history": "no",
            "surgery_details": "نباید ذخیره شود",
            "cold_sore": "no",
            "medication_history": ["none"],
            "substance_use": ["none"],
            "referral_source": "other",
        }
        response = self.client.post(
            reverse(
                "doctors:doctor_consultation",
                kwargs={"slug": self.doctor_a.slug},
            ),
            form_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn("medical_history", response.context["form"].errors)
        self.assertFalse(
            ConsultationRequest.objects.filter(name="کاربر تست").exists()
        )

    def test_birth_date_uses_persian_date_picker(self):
        response = self.client.get(
            reverse(
                "doctors:doctor_consultation",
                kwargs={"slug": self.doctor_a.slug},
            )
        )
        self.assertContains(response, 'id="birth_date"')
        self.assertContains(response, "persianDatepicker")
        self.assertContains(response, 'format: "YYYY/MM/DD"')
        self.assertContains(response, "initialValue: false")
        self.assertContains(response, "autoClose: true")
        self.assertContains(response, 'maxDate: "1499/12/29"')

    def test_doctor_form_uses_specialty_choices(self):
        form = DoctorForm()
        specialty_values = [value for value, label in form.fields["specialty"].choices]
        self.assertIn("جراح رینوپلاستی", specialty_values)
        self.assertIn("دندان پزشکی", specialty_values)

    def test_birth_date_has_no_minimum_year_restriction(self):
        form_data = {
            "name": "کاربر تست",
            "phone": "09123456789",
            "birth_date": "1200/12/29",
            "job": "معلم",
            "marital_status": "single",
            "address": "تهران",
            "medical_history": ["none"],
            "surgery_history": "no",
            "surgery_details": "",
            "cold_sore": "no",
            "medication_history": ["none"],
            "substance_use": ["none"],
            "referral_source": "other",
        }
        response = self.client.post(
            reverse(
                "doctors:doctor_consultation",
                kwargs={"slug": self.doctor_a.slug},
            ),
            form_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ConsultationRequest.objects.filter(name="کاربر تست").exists()
        )

    def test_consultation_submission_saves_patient_image(self):
        url = reverse(
            "doctors:doctor_consultation",
            kwargs={"slug": self.doctor_a.slug},
        )
        image_file = BytesIO()
        Image.new("RGB", (2, 2), "white").save(image_file, format="PNG")
        image_file.seek(0)

        response = self.client.post(
            url,
            {
                "name": "مریم رضایی",
                "phone": "09123456789",
                "birth_date": "1372/05/12",
                "job": "معلم",
                "marital_status": "married",
                "address": "تهران",
                "medical_history": ["none"],
                "surgery_history": "yes",
                "surgery_details": "آپاندیس",
                "cold_sore": "no",
                "medication_history": ["none"],
                "substance_use": ["none"],
                "referral_source": "friend",
                "message": "",
                "patient_image": SimpleUploadedFile(
                    "consultation.png",
                    image_file.read(),
                    content_type="image/png",
                ),
            },
        )
        self.assertEqual(response.status_code, 200)
        consultation = ConsultationRequest.objects.get(name="مریم رضایی")
        self.assertTrue(consultation.patient_image.name.startswith("consultations/"))
        self.assertContains(response, "درخواست شما با موفقیت ثبت شد.")

    def test_doctor_detail_does_not_contain_consultation_form(self):
        response = self.client.get(
            reverse(
                "doctors:doctor_detail",
                kwargs={"slug": self.doctor_a.slug},
            )
        )
        self.assertNotContains(response, "name=\"name\"")
        self.assertContains(response, "consultation-form")

    def test_consultation_page_is_isolated(self):
        response = self.client.get(
            reverse(
                "doctors:doctor_consultation",
                kwargs={"slug": self.doctor_a.slug},
            )
        )
        self.assertContains(response, self.doctor_a.name)
        self.assertContains(response, self.doctor_a.specialty)
        self.assertNotContains(response, "پزشکان")
        self.assertNotContains(response, "مقالات")


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

    def test_superuser_can_create_published_article(self):
        self.client.login(username="admin", password="testpass123")
        response = self.client.post(
            reverse("dashboard:article_create"),
            {
                "title": "مقاله تست",
                "slug": "test-article",
                "excerpt": "خلاصه مقاله",
                "content": "متن کامل مقاله",
                "is_published": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        article = Article.objects.get(slug="test-article")
        self.assertTrue(article.is_published)
        self.assertEqual(article.author, self.superuser)

    def test_create_form_defaults_to_published_checked(self):
        self.client.login(username="admin", password="testpass123")
        response = self.client.get(reverse("dashboard:article_create"))
        self.assertContains(response, "checked", html=False)

    def test_draft_article_not_on_public_list(self):
        Article.objects.create(
            title="پیش‌نویس",
            slug="draft-article",
            excerpt="خلاصه",
            content="متن",
            is_published=False,
        )
        response = self.client.get(reverse("articles:article_list"))
        self.assertNotContains(response, "پیش‌نویس")

    def test_published_article_on_public_list(self):
        Article.objects.create(
            title="منتشر شده",
            slug="published-article",
            excerpt="خلاصه",
            content="متن",
            is_published=True,
        )
        response = self.client.get(reverse("articles:article_list"))
        self.assertContains(response, "منتشر شده")

    def test_persian_slug_url_resolves(self):
        Article.objects.create(
            title="غذای بد",
            slug="غذای-بد",
            excerpt="خلاصه",
            content="متن",
            is_published=True,
        )
        url = reverse("articles:article_detail", kwargs={"slug": "غذای-بد"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "غذای بد")
