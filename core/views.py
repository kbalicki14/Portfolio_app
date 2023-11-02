from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import TemplateView

from .forms import AdvertiseForm, MultiImageForm
from .models import Task, AdvertiseModel, Image, CityList


# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('task')


class RegisterView(FormView):
    template_name = 'core/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('task')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)

    # redirect register page
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('task')
        return super(RegisterView, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    # login_url = 'login'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search_area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)
            # title__icontains

        context['search_input'] = search_input
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'detail'
    template_name = 'core/task_detail_name.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('task')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('task')


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('task')


class WelcomePage(TemplateView):
    # model = AdvertiseModel
    # context_object_name = 'category'
    # queryset = AdvertiseModel.objects.only('advertise_category')
    template_name = 'core/index.html'


# png not upload
class AdvertiseCreate(CreateView):
    model = AdvertiseModel
    form_class = AdvertiseForm
    template_name = 'core/img_update.html'
    # success_url = reverse_lazy('upload')
    context_object_name = 'img_obj'
    success_url = reverse_lazy('advertise')

    def get(self, request, *args, **kwargs):
        if 'term' in request.GET:
            querySet = CityList.objects.filter(city_name__istartswith=request.GET.get('term'))
            city_list = list()
            for city in querySet:
                city_list.append(city.city_name)
            return JsonResponse(city_list, safe=False)
        return super().get(request, *args, **kwargs)


class CreateImageToGallery(CreateView):
    model = Image
    form_class = MultiImageForm
    template_name = 'core/add_to_gallery.html'
    context_object_name = 'image'
    success_url = reverse_lazy('task')

    def post(self, request, *args, **kwargs):
        form = MultiImageForm(request.POST, request.FILES)
        images = request.FILES.getlist("image")
        if form.is_valid():
            title = form.cleaned_data['title']
            advertise = form.cleaned_data['advertise']

            for image in images:
                Image.objects.create(title=title, advertise=advertise, image=image)
            return redirect('task')

    # def form_valid(self, form):
    #     # adverstment_gallery = form
    #     # title = form.cleaned_data['title']
    #     images = form.cleaned_data['image']
    #     # img = form.FILES.getlist('image')
    #
    #     # images = form.FILES.getlist('image')
    #     for image in images:
    #         Image.objects.create(image=image)


def AddMultiImage(request):
    form = MultiImageForm()

    if request.method == 'POST':
        form = MultiImageForm(request.POST, request.FILES)
        images = request.FILES.getlist("image")

        # images = form.cleaned_data.getlist('image')
        if form.is_valid():
            title = form.cleaned_data['title']
            advertise = form.cleaned_data['advertise']

            for image in images:
                Image.objects.create(title=title, advertise=advertise, image=image)
            return redirect('multi_image')

    context = {'form': form}
    return render(request, 'core/add_to_gallery.html', context)


def thanks(request):
    return HttpResponse('<h1>Form saved.</h1>')


def imageUpload(request):
    """Process images uploaded by users"""
    if request.method == 'POST':
        form = AdvertiseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            return render(request, 'core/img_update.html', {'form': form, 'img_obj': img_obj})
    else:
        form = AdvertiseForm()
        return render(request, 'core/img_update.html', {'form': form})


class AdvertList(ListView):
    model = AdvertiseModel
    context_object_name = 'advert'
    template_name = 'core/advert_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_input = self.request.GET.get('search_area') or ''
        search_category = self.request.GET.get('search_category') or ''
        context['advert'] = context['advert'].filter(town=search_input)
        # , advertise_category = search_category
        context['search_input'] = search_input
        context['search_category'] = search_category
        return context
