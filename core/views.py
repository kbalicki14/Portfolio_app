from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib import messages

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import TemplateView
from django.db.models import Avg
from django.core.paginator import Paginator
from PIL import Image as PilImage
from io import BytesIO
from django.core.files import File

from .forms import AdvertiseForm, MultiImageForm, ImageForm, RatingForm
from .models import Task, AdvertiseModel, Image, CityList, AdvertiseCategory, AdvertiseRating


# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'core/auth/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('welcome')


class RegisterView(FormView):
    template_name = 'core/auth/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('welcome')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)

    # redirect register page
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('welcome')
        return super(RegisterView, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    # login_url = 'login'
    context_object_name = 'tasks'
    paginate_by = 3

    def get_queryset(self):
        search_input = self.request.GET.get('search_area') or ''
        tasks = super().get_queryset().filter(user=self.request.user)
        if search_input:
            tasks = tasks.filter(title__startswith=search_input)
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.get_queryset().filter(complete=False).count()
        context['search_input'] = self.request.GET.get('search_area') or ''
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


class WelcomePage(ListView):
    model = AdvertiseCategory
    context_object_name = 'category'
    queryset = AdvertiseCategory.objects.all()
    template_name = 'core/index.html'


# png not upload
class AdvertiseCreate(LoginRequiredMixin, CreateView):
    model = AdvertiseModel
    form_class = AdvertiseForm
    template_name = 'core/advertise/advertise_create.html'
    # success_url = reverse_lazy('upload')
    context_object_name = 'img_obj'
    success_url = reverse_lazy('user_advertise')

    # serach bar
    def get(self, request, *args, **kwargs):
        if 'term' in request.GET:
            query_set = CityList.objects.filter(city_name__istartswith=request.GET.get('term'))
            city_list = list()
            for city in query_set:
                city_list.append(city.city_name)
            return JsonResponse(city_list, safe=False)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Advertise created.")
        return super(AdvertiseCreate, self).form_valid(form)


class AdvertiseDetails(DetailView):
    model = AdvertiseModel
    context_object_name = 'detail'
    template_name = 'core/advertise/advertise_details.html'

    # def get_queryset(self):
    #     tasks = super().get_queryset()
    #     rating = AdvertiseRating.objects.filter(advertise=self.object)
    #     return rating

    def get_context_data(self, **kwargs):
        advertise_id = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        context['gallery'] = Image.objects.filter(advertise=advertise_id).order_by("-created_at")[:6]
        context['average_rating'] = AdvertiseRating.objects.filter(advertise=self.object).aggregate(Avg('rating'))[
            'rating__avg']
        context['ratings'] = AdvertiseRating.objects.filter(advertise=self.object).order_by("-created_at")[:5]

        # ratings_list = AdvertiseRating.objects.filter(advertise=self.object)
        # paginator = Paginator(ratings_list, 2)
        # page = self.request.GET.get('page')
        # context['ratings'] = paginator.get_page(page)
        return context


class AdvertiseGallery(ListView):
    model = Image
    context_object_name = 'gallery'
    template_name = 'core/advertise/advertise_gallery.html'
    paginate_by = 2

    def get_queryset(self):
        id_advertise = self.kwargs['pk']
        try:
            object_advertise = AdvertiseModel.objects.get(id=id_advertise)
        except ObjectDoesNotExist as e:
            raise Http404

        gallery = super().get_queryset().filter(advertise=object_advertise).order_by("-created_at")
        return gallery

    def get_context_data(self, **kwargs):
        id_advertise = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        try:
            object_advertise = AdvertiseModel.objects.get(id=id_advertise)
        except ObjectDoesNotExist as e:
            raise Http404
        context['id_advertise'] = id_advertise
        # context['user'] = object_advertise.user
        context['is_owner'] = self.request.user == object_advertise.user

        print(context['is_owner'])
        return context


class AdvertiseRatingList(ListView):
    model = AdvertiseRating
    context_object_name = 'ratings'
    template_name = 'core/advertise/advertise_rating_list.html'
    paginate_by = 4

    def get_queryset(self):
        id_advertise = self.kwargs['pk']
        try:
            object_advertise = AdvertiseModel.objects.get(id=id_advertise)
        except ObjectDoesNotExist as e:
            raise Http404

        rating = super().get_queryset().filter(advertise=object_advertise).order_by("-created_at")
        return rating

    def get_context_data(self, **kwargs):
        id_advertise = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        try:
            advert_object = AdvertiseModel.objects.get(id=id_advertise)

        except ObjectDoesNotExist as e:
            raise Http404
        context['average_rating'] = AdvertiseRating.objects.filter(advertise=advert_object).aggregate(Avg('rating'))[
            'rating__avg']
        context['id_advertise'] = id_advertise
        return context


class AdvertiseUpdate(LoginRequiredMixin, UpdateView):
    model = AdvertiseModel
    form_class = AdvertiseForm
    template_name = 'core/advertise/advertise_create.html'
    success_url = reverse_lazy('user_advertise')

    def get(self, request, *args, **kwargs):
        advertise_id = self.kwargs['pk']
        try:
            advert_object = AdvertiseModel.objects.get(id=advertise_id)
        except ObjectDoesNotExist as e:
            raise Http404

        if advert_object.user != self.request.user:
            raise Http404
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            advert_object = AdvertiseModel.objects.get(id=form.instance.id)
        except ObjectDoesNotExist as e:
            form.add_error(None, f"Not found this advertise")
            return super().form_invalid(form)

        if advert_object.user != self.request.user:
            form.add_error(None, "Only owner edit advertise")
            return super().form_invalid(form)
        form.instance.advertise.set = advert_object
        messages.success(self.request, "Advertise details updated.")
        return super().form_valid(form)


class AdvertiseDelete(LoginRequiredMixin, DeleteView):
    model = AdvertiseModel
    context_object_name = 'advertise'
    template_name = 'core/advertise/advertise_confirm_delete.html'
    success_url = reverse_lazy('user_advertise')

    def get(self, request, *args, **kwargs):
        advertise_id = self.kwargs['pk']
        try:
            advert_object = AdvertiseModel.objects.get(id=advertise_id)
        except ObjectDoesNotExist as e:
            raise Http404

        if advert_object.user != self.request.user:
            raise Http404
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        delete_id = self.kwargs['pk']
        try:
            advert_object = AdvertiseModel.objects.get(id=delete_id)
        except ObjectDoesNotExist as e:
            form.add_error(None, f"Not found this advertise")
            return super().form_invalid(form)

        if advert_object.user != self.request.user:
            form.add_error(None, "Only owner can delete advertise!")
            return super().form_invalid(form)
            # raise Http404
        # form.instance.advertise = advert_object
        messages.error(self.request, "Advertise deleted", extra_tags="danger")
        return super().form_valid(form)


class AddImageToGallery(LoginRequiredMixin, CreateView):
    model = Image
    form_class = ImageForm
    template_name = 'core/advertise/add_to_gallery.html'
    context_object_name = 'image'

    # possible issues in url
    def get_success_url(self):
        return self.request.path_info

    def get(self, request, *args, **kwargs):
        advertise_id = self.kwargs['advertise_pk']
        try:
            advert_object = AdvertiseModel.objects.get(id=advertise_id)
        except ObjectDoesNotExist as e:
            raise Http404

        if advert_object.user != self.request.user:
            raise Http404
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        pk_advertise = self.kwargs['advertise_pk']
        try:
            advert_object = AdvertiseModel.objects.get(id=pk_advertise)

        except ObjectDoesNotExist as e:
            form.add_error(None, f"Not found this advertise")
            return super().form_invalid(form)

        if advert_object.user != self.request.user:
            form.add_error(None, "Only owner can add image")
            return super().form_invalid(form)

        messages.success(self.request, "Image successfully added")
        form.instance.advertise = advert_object
        return super().form_valid(form)


class ImageInGalleryUpdate(UpdateView):
    model = Image
    form_class = ImageForm
    template_name = 'core/advertise/add_to_gallery.html'
    context_object_name = 'image'
    success_url = reverse_lazy('user_advertise')

    def get(self, request, *args, **kwargs):
        advertise_id = self.kwargs['advertise_pk']
        try:
            advert_object = AdvertiseModel.objects.get(id=advertise_id)
        except ObjectDoesNotExist as e:
            raise Http404

        if advert_object.user != self.request.user:
            raise Http404
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        pk_advertise = self.kwargs['advertise_pk']
        try:
            advert_object = AdvertiseModel.objects.get(id=pk_advertise)

        except ObjectDoesNotExist as e:
            form.add_error(None, f"Not found this advertise")
            return super().form_invalid(form)

        if advert_object.user != self.request.user:
            form.add_error(None, "Only owner can add image")
            return super().form_invalid(form)

        messages.success(self.request, "Image details updated.")
        form.instance.advertise = advert_object
        return super().form_valid(form)


class ImageInGalleryDelete(DeleteView):
    model = Image
    context_object_name = 'image'
    template_name = 'core/advertise/image_gallery_confirm_delete.html'
    success_url = reverse_lazy('user_advertise')

    def get(self, request, *args, **kwargs):
        advertise_id = self.kwargs['advertise_pk']
        cutomsRestrictedGet(self.request.user, advertise_id)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        delete_id = self.kwargs['advertise_pk']
        try:
            advertise_object = AdvertiseModel.objects.get(id=delete_id)
        except ObjectDoesNotExist as e:
            form.add_error(None, f"Not found this advertise")
            return super().form_invalid(form)

        if advertise_object.user != self.request.user:
            form.add_error(None, "Only owner can delete rating!")
            return super().form_invalid(form)
        messages.error(self.request, "Image deleted.", extra_tags="danger")
        return super().form_valid(form)


class CreateImagesToGallery(CreateView):
    model = Image
    form_class = MultiImageForm
    template_name = 'core/advertise/add_to_gallery.html'
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
    return render(request, 'core/advertise/add_to_gallery.html', context)


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
            return render(request, 'core/advertise/advertise_create.html', {'form': form, 'img_obj': img_obj})
    else:
        form = AdvertiseForm()
        return render(request, 'core/advertise/advertise_create.html', {'form': form})


class AdvertList(ListView):
    model = AdvertiseModel
    context_object_name = 'advert'
    template_name = 'core/advertise/advert_list.html'

    paginate_by = 4

    def get_queryset(self):
        search_input = self.request.GET.get('search_area') or ''
        search_category = self.request.GET.get('search_category')
        advert_qs = super().get_queryset().filter(town=search_input, advertise_category=search_category)
        return advert_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_input'] = self.request.GET.get('search_area') or ''
        context['search_category'] = int(self.request.GET.get('search_category'))
        context['category'] = AdvertiseCategory.objects.all()
        return context


class CurrentUserAdvertise(LoginRequiredMixin, ListView):
    model = AdvertiseModel
    context_object_name = 'user_adverts'
    template_name = 'core/advertise/user_adverts_list.html'
    paginate_by = 5

    def get_queryset(self):
        user_adverts = super().get_queryset().filter(user=self.request.user)
        return user_adverts


class ProfileDetail(LoginRequiredMixin, TemplateView):
    template_name = 'core/profile_detail.html'


class RatingAdvertise(CreateView):
    model = AdvertiseRating
    form_class = RatingForm
    template_name = 'core/advertise/rating_form.html'
    context_object_name = 'rating'

    def get_success_url(self):
        advertise_id = self.kwargs['pk']
        return reverse_lazy('advertise_details', kwargs={'pk': advertise_id})

    def form_valid(self, form):
        advertise_id = self.kwargs['pk']
        try:
            advert_object = AdvertiseModel.objects.get(id=advertise_id)
        except ObjectDoesNotExist as e:
            raise Http404
        form.instance.user = self.request.user
        form.instance.advertise = advert_object
        messages.success(self.request, "Rating added.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        advertise_id = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        context['id_advertise'] = advertise_id
        return context


class RatingUpdate(UpdateView):
    model = AdvertiseRating
    form_class = RatingForm
    context_object_name = 'rating'
    template_name = 'core/advertise/rating_form.html'

    def get_success_url(self):
        # advertise_pk in url is pk in detail url
        advertise_id = self.kwargs['advertise_pk']
        return reverse_lazy('advertise_details', kwargs={'pk': advertise_id})

    def get(self, request, *args, **kwargs):
        # advertise_id = self.kwargs['advertise_pk']
        try:
            rating_object = AdvertiseRating.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist as e:
            raise Http404

        if rating_object.user != self.request.user:
            raise Http404
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            rating_object = AdvertiseRating.objects.get(id=form.instance.id)
        except ObjectDoesNotExist as e:
            form.add_error(None, f"Not found this rating")
            return super().form_invalid(form)

        if rating_object.user != self.request.user:
            form.add_error(None, "Only owner can edit rating")
            return super().form_invalid(form)
        form.instance.advertise.set = rating_object
        messages.success(self.request, "Rating details updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        advertise_id = self.kwargs['advertise_pk']
        context = super().get_context_data(**kwargs)
        context['id_advertise'] = advertise_id
        return context


class RatingDelete(DeleteView):
    model = AdvertiseRating
    context_object_name = 'rating'
    template_name = 'core/advertise/rating_confirm_delete.html'

    def get_success_url(self):
        # advertise_pk in url is pk in detail url
        advertise_id = self.kwargs['advertise_pk']
        return reverse_lazy('advertise_details', kwargs={'pk': advertise_id})

    def get(self, request, *args, **kwargs):
        # advertise_id = self.kwargs['advertise_pk']
        try:
            rating_object = AdvertiseRating.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist as e:
            raise Http404

        if rating_object.user != self.request.user:
            raise Http404

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        delete_id = self.kwargs['pk']
        try:
            rating_object = AdvertiseRating.objects.get(id=delete_id)
        except ObjectDoesNotExist as e:
            form.add_error(None, f"Not found this rating")
            return super().form_invalid(form)

        if rating_object.user != self.request.user:
            form.add_error(None, "Only owner can delete rating!")
            return super().form_invalid(form)
            # raise Http404
        # form.instance.rating = rating_object

        messages.error(self.request, "Rating deleted.", extra_tags="danger")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        advertise_id = self.kwargs['advertise_pk']
        context = super().get_context_data(**kwargs)
        context['id_advertise'] = advertise_id
        return context


def cutomsRestrictedGet(user, id):
    try:
        advert_object = AdvertiseModel.objects.get(id=id)
    except ObjectDoesNotExist as e:
        raise Http404

    if advert_object.user != user:
        raise Http404
    return advert_object


def handler404(request, exception):
    return render(request, 'core/http_status/404.html', status=404)


def handler500(request, *args, **argv):
    return render('core/http_status/500.html', status=500)
