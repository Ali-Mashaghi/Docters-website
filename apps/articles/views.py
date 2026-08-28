from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Article


class ArticleListView(ListView):
    model = Article
    template_name = "articles/article_list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        queryset = Article.objects.filter(is_published=True).select_related("author")

        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(excerpt__icontains=search)
                | Q(content__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = "articles/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Article.objects.filter(is_published=True).select_related("author")
