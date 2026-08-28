from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, UpdateView, View

from apps.articles.models import Article
from apps.consultations.models import ConsultationRequest
from apps.doctors.models import DoctorManager

from .forms import ArticleForm, DoctorAssignmentForm, StaffUserCreateForm
from .permissions import (
    get_accessible_consultations,
    get_accessible_doctors,
    get_dashboard_stats,
    user_can_access_consultation,
)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require authenticated staff users for dashboard access."""

    login_url = "login"

    def test_func(self):
        return self.request.user.is_staff


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require superuser for manager administration."""

    login_url = "login"

    def test_func(self):
        return self.request.user.is_superuser


class DashboardMixin(StaffRequiredMixin):
    """Base mixin with permission-scoped querysets."""

    def get_doctors_queryset(self):
        return get_accessible_doctors(self.request.user)

    def get_consultations_queryset(self):
        return get_accessible_consultations(self.request.user)


class DashboardView(DashboardMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        doctors = self.get_doctors_queryset().prefetch_related("portfolios")
        consultations = self.get_consultations_queryset()

        context["stats"] = get_dashboard_stats(user)
        context["doctors"] = doctors.annotate(
            request_count=Count("consultation_requests")
        )
        context["recent_requests"] = consultations[:10]
        return context


class ConsultationListView(DashboardMixin, ListView):
    model = ConsultationRequest
    template_name = "dashboard/consultations.html"
    context_object_name = "consultations"
    paginate_by = 15

    def get_queryset(self):
        queryset = self.get_consultations_queryset()

        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(phone__icontains=search)
                | Q(email__icontains=search)
                | Q(doctor__name__icontains=search)
            )

        status = self.request.GET.get("status", "").strip()
        if status:
            queryset = queryset.filter(status=status)

        doctor_id = self.request.GET.get("doctor", "").strip()
        if doctor_id.isdigit():
            queryset = queryset.filter(
                doctor_id=int(doctor_id),
                doctor__in=self.get_doctors_queryset(),
            )

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_status"] = self.request.GET.get("status", "")
        context["selected_doctor"] = self.request.GET.get("doctor", "")
        context["status_choices"] = ConsultationRequest.STATUS_CHOICES
        context["doctors"] = self.get_doctors_queryset()
        return context


class ConsultationDetailView(DashboardMixin, DetailView):
    model = ConsultationRequest
    template_name = "dashboard/consultation_detail.html"
    context_object_name = "consultation"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return self.get_consultations_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = ConsultationRequest.STATUS_CHOICES
        return context


class ConsultationStatusUpdateView(DashboardMixin, View):
    """Update consultation status with IDOR protection."""

    def post(self, request, pk):
        if not user_can_access_consultation(request.user, pk):
            raise PermissionDenied

        consultation = get_object_or_404(
            self.get_consultations_queryset(),
            pk=pk,
        )

        new_status = request.POST.get("status", "").strip()
        valid_statuses = dict(ConsultationRequest.STATUS_CHOICES)

        if new_status in valid_statuses:
            consultation.status = new_status
            consultation.save(update_fields=["status"])

        return self._redirect_back(request, pk)

    def _redirect_back(self, request, pk):
        from django.urls import reverse

        referer = request.META.get("HTTP_REFERER", "")
        detail_url = reverse("dashboard:consultation_detail", kwargs={"pk": pk})

        if detail_url in referer:
            return redirect("dashboard:consultation_detail", pk=pk)
        return redirect("dashboard:consultations")


class ManagerListView(SuperuserRequiredMixin, ListView):
    template_name = "dashboard/managers.html"
    context_object_name = "managers"
    paginate_by = 15

    def get_queryset(self):
        queryset = (
            User.objects.filter(is_staff=True, is_superuser=False)
            .prefetch_related(
                Prefetch(
                    "doctor_permissions",
                    queryset=DoctorManager.objects.select_related("doctor"),
                )
            )
            .order_by("-date_joined")
        )

        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context


class ManagerCreateView(SuperuserRequiredMixin, FormView):
    template_name = "dashboard/manager_create.html"
    form_class = StaffUserCreateForm
    success_url = reverse_lazy("dashboard:managers")

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            f"مدیر «{form.cleaned_data['username']}» با موفقیت ایجاد شد.",
        )
        return super().form_valid(form)


class ManagerAssignView(SuperuserRequiredMixin, FormView):
    template_name = "dashboard/manager_assign.html"
    form_class = DoctorAssignmentForm

    def dispatch(self, request, *args, **kwargs):
        self.manager_user = get_object_or_404(
            User,
            pk=self.kwargs["pk"],
            is_staff=True,
            is_superuser=False,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        assigned = self.manager_user.doctor_permissions.values_list(
            "doctor_id", flat=True
        )
        return {"doctors": list(assigned)}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["manager_user"] = self.manager_user
        return context

    def form_valid(self, form):
        selected_ids = set(form.cleaned_data["doctors"].values_list("pk", flat=True))
        current_ids = set(
            self.manager_user.doctor_permissions.values_list("doctor_id", flat=True)
        )

        to_remove = current_ids - selected_ids
        to_add = selected_ids - current_ids

        if to_remove:
            DoctorManager.objects.filter(
                user=self.manager_user,
                doctor_id__in=to_remove,
            ).delete()

        for doctor_id in to_add:
            DoctorManager.objects.create(
                user=self.manager_user,
                doctor_id=doctor_id,
            )

        messages.success(
            self.request,
            f"دسترسی‌های «{self.manager_user.username}» به‌روزرسانی شد.",
        )
        return redirect("dashboard:managers")

    def form_invalid(self, form):
        messages.error(self.request, "خطا در ذخیره تخصیص. لطفاً دوباره تلاش کنید.")
        return super().form_invalid(form)


class ManagerDeleteView(SuperuserRequiredMixin, View):
    """Remove staff status and doctor assignments."""

    def post(self, request, pk):
        manager = get_object_or_404(
            User,
            pk=pk,
            is_staff=True,
            is_superuser=False,
        )
        username = manager.username
        DoctorManager.objects.filter(user=manager).delete()
        manager.is_staff = False
        manager.save(update_fields=["is_staff"])
        messages.success(request, f"مدیر «{username}» حذف شد.")
        return redirect("dashboard:managers")


class ArticleListView(SuperuserRequiredMixin, ListView):
    model = Article
    template_name = "dashboard/articles.html"
    context_object_name = "articles"
    paginate_by = 15

    def get_queryset(self):
        queryset = Article.objects.select_related("author").order_by("-created_at")

        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(excerpt__icontains=search)
                | Q(content__icontains=search)
            )

        status = self.request.GET.get("status", "").strip()
        if status == "published":
            queryset = queryset.filter(is_published=True)
        elif status == "draft":
            queryset = queryset.filter(is_published=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_status"] = self.request.GET.get("status", "")
        return context


class ArticleCreateView(SuperuserRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "dashboard/article_form.html"
    success_url = reverse_lazy("dashboard:articles")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "مقاله با موفقیت ایجاد شد.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "ایجاد مقاله جدید"
        return context


class ArticleUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "dashboard/article_form.html"
    success_url = reverse_lazy("dashboard:articles")

    def form_valid(self, form):
        messages.success(self.request, "مقاله با موفقیت ویرایش شد.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "ویرایش مقاله"
        return context


class ArticleDeleteView(SuperuserRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        title = article.title
        article.delete()
        messages.success(request, f"مقاله «{title}» حذف شد.")
        return redirect("dashboard:articles")


class ArticleTogglePublishView(SuperuserRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        article.is_published = not article.is_published
        article.save(update_fields=["is_published"])
        status = "منتشر" if article.is_published else "پیش‌نویس"
        messages.success(request, f"وضعیت مقاله به «{status}» تغییر کرد.")
        return redirect("dashboard:articles")
