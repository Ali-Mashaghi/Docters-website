from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView

from apps.consultations.forms import ConsultationRequestForm
from apps.consultations.models import ConsultationRequest

from .models import Doctor


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["doctors"] = (
            Doctor.objects.filter(is_active=True)
            .prefetch_related("portfolios")[:6]
        )
        return context


class DoctorListView(ListView):
    model = Doctor
    template_name = "doctors/doctor_list.html"
    context_object_name = "doctors"
    paginate_by = 8

    def get_queryset(self):
        queryset = (
            Doctor.objects.filter(is_active=True)
            .prefetch_related("portfolios")
            .order_by("-created_at")
        )

        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(specialty__icontains=search)
                | Q(bio__icontains=search)
            )

        specialty = self.request.GET.get("specialty", "").strip()
        if specialty:
            queryset = queryset.filter(specialty=specialty)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_specialty"] = self.request.GET.get("specialty", "")
        context["specialties"] = (
            Doctor.objects.filter(is_active=True)
            .values_list("specialty", flat=True)
            .distinct()
            .order_by("specialty")
        )
        return context


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "doctors/doctor_detail.html"
    context_object_name = "doctor"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Doctor.objects.filter(is_active=True).prefetch_related("portfolios")


class DoctorConsultationView(DetailView):
    model = Doctor
    template_name = "doctors/consultation_form.html"
    context_object_name = "doctor"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    consultation_forms = {
        "جراح رینوپلاستی": ConsultationRequestForm,
    }

    def get_form_class(self):
        return self.consultation_forms.get(
            self.object.specialty,
            ConsultationRequestForm,
        )

    def get_queryset(self):
        return Doctor.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", self.get_form_class()())
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form_class()(request.POST, request.FILES)

        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.doctor = self.object
            consultation.save()
            context = self.get_context_data(form=self.get_form_class()())
            context["success"] = True
            return self.render_to_response(context)

        return self.render_to_response(self.get_context_data(form=form))
