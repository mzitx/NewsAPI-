from django.shortcuts import render
from django.shortcuts import render, redirect
from django.views.generic import *
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.db.models import Q
from rest_framework import status
from rest_framework import generics
from rest_framework import serializers,viewsets, routers
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class BaseMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategory'] = Category.objects.all()
        print(context)
        return context

class HomeView(BaseMixin,TemplateView ):
	template_name = 'home.html'


class NewsCreateView(BaseMixin,CreateView ):
    template_name = 'newscreate.html'
    form_class = NewsForm

    def form_valid(self, form):
        user = self.request.user
        form.instance.news_by = user
        self.news_id = form.save().id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("newsapp:newslist")


class NewsUpdateView(generics.RetrieveUpdateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    lookup_field = 'pk'


class NewsDeleteView(generics.RetrieveDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    lookup_field = 'pk'

class NewsListView(BaseMixin,ListView):
    template_name = 'newslist.html'
    model = News
    # queryset = News.objects.all()
    # serializer_class = NewsSerializer
    context_object_name = 'newslist'


class NewsDetailView(BaseMixin,DetailView):
    template_name = 'newsdetail.html'
    model = News
    context_object_name = 'newsdetail'

    # def newsdetail_count(request, news_id):
    #     # context = super().get_context_data(**kwargs)
    #     news = News.objects.all()
    #     news.count += 1
    #     news.save()
    #     # context['count'] = News.update_counter(self.count)
    #     # self.object.update_count()
    #     # self.object.save()
    #     return render(request, context={'news': news})

    def get(self, request, **kwargs):
        news = News.objects.get(id = self.kwargs['pk'])
        news.count += 1
        news.save()
        top_five = News.objects.all().order_by('-count')[0:2]
        for news in top_five:
            print(news.count)
        print(top_five)
        # context['count'] = News.update_counter(self.count)
        # self.object.update_count()
        # self.object.save()
        return render(request,'newsdetail.html', context={'newsdetail': news,'top_five': top_five}
            )

    #     news = News.objects.create(count = self.request.count+1)
    #     return JsonResponse({})

class CategoryUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'pk'


class CategoryDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'pk'


class CategoryDetailView( BaseMixin,DetailView):
    template_name = 'categorydetail.html'
    model = Category
    context_object_name = "categorydetail"

class EditorNewsCreateView(BaseMixin,CreateView ):
    template_name = 'editortemplates/editornewscreate.html'
    form_class = NewsForm
    success_url = reverse_lazy('newsapp:editornewslist')
    success_message = "News Created succesfully"


class EditorNewsListView(BaseMixin,ListView):
    template_name = 'editortemplates/editornewslist.html'
    model = News
    context_object_name = 'editornewslist'


class EditorNewsUpdateView(BaseMixin,UpdateView):
    template_name = 'admintemplates/adminnewscreate.html'
    model = News
    form_class = NewsForm
    success_url = reverse_lazy("newsapp:adminnewslist")
    success_message = "News updated succesfully"


class EditorNewsDeleteView(BaseMixin,DeleteView):
    template_name = 'admintemplates/adminnewsdelete.html'
    model = News
    success_url = reverse_lazy('newsapp:adminnewslist')
    success_message = "News deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EditorNewsDeleteView, self).delete(request, *args, **kwargs)


class EditorCategoryCreateView(BaseMixin,CreateView):
    template_name = 'editortemplates/editorcategorycreate.html'
    form_class = CategoryForm
    success_url = reverse_lazy('newsapp:editorcategorylist')
    success_message = "Category Created succesfully"


class EditorCategoryListView(BaseMixin,ListView):
    template_name = 'editortemplates/editorcategorylist.html'
    model = Category
    context_object_name = 'editorcategorylist'


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EditorCategoryUpdateView(BaseMixin,UpdateView):
    template_name = 'admintemplates/admincategorycreate.html'
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("newsapp:admincategorylist")
    success_message = "Category updated succesfully"


class EditorCategoryDeleteView(BaseMixin,DeleteView):
    template_name = 'admintemplates/admincategorydelete.html'
    model = Category
    success_url = reverse_lazy('newsapp:admincategorylist')
    success_message = "Category deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EditorCategoryDeleteView, self).delete(request, *args, **kwargs)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy("newsapp:adminpanel")

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            if Admin.objects.filter(user=user).exists():
                return HttpResponseRedirect(reverse_lazy('newsapp:adminpanel'))
            elif Editor.objects.filter(user=user).exists():
                return HttpResponseRedirect(reverse_lazy('newsapp:editorpanel'))
        else:
            return render(self.request, self.template_name, {
                'form': form,
                'errors': "Please correct username or password "
            })
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('newsapp:home')        


class EditorPanelView(BaseMixin,TemplateView):
	template_name = 'editortemplates/editorbase.html'





