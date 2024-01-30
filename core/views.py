from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import login, update_session_auth_hash
from django.views.generic import TemplateView
from django.db.models import Avg
from django.core.paginator import Paginator
from PIL import Image as PilImage
from io import BytesIO
from django.core.files import File

from .forms import AdvertiseForm, MultiImageForm, ImageForm, RatingForm, AddressForm, ReportAdvertiseForm, \
    UsernameChangeForm
from .models import AdvertiseModel, Image, CityList, AdvertiseCategory, AdvertiseRating, Address, ReportAdvertise


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


class ChangePassword(FormView):
    template_name = 'core/auth/change_password.html'
    success_url = reverse_lazy('profile_detail')
    form_class = PasswordChangeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # def form_valid(self, form):
    #     user = form.save()
    #     # Aktualizacja sesji, aby użytkownik nie został wylogowany
    #     update_session_auth_hash(self.request, user)
    #     return super().form_valid(form)


class ChangeUsername(UpdateView):
    model = User
    template_name = 'core/auth/change_username.html'
    success_url = reverse_lazy('profile_detail')
    form_class = UsernameChangeForm

    def get_object(self, queryset=None):
        return self.request.user


class WelcomePage(ListView):
    model = AdvertiseCategory
    context_object_name = 'category'
    queryset = AdvertiseCategory.objects.all()
    template_name = 'core/index.html'


class SerachBarAutoComplete(View):
    def get(self, request, *args, **kwargs):
        # serach bar
        if 'term' in request.GET:
            query_set = CityList.objects.filter(city_name__istartswith=request.GET.get('term'))
            city_list = list()
            for city in query_set:
                city_list.append(city.city_name)
            return JsonResponse(city_list, safe=False)
        else:
            return HttpResponse('<p>null</p>')


# png not upload
class AdvertiseCreate(LoginRequiredMixin, CreateView):
    model = AdvertiseModel
    form_class = AdvertiseForm
    template_name = 'core/advertise/advertise_create.html'
    context_object_name = 'advertise'
    success_url = reverse_lazy('user_advertise')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['address'] = AddressForm(self.request.POST)
        else:
            data['address'] = AddressForm()
        return data

    def form_valid(self, form):
        # form is advertiseForm
        context = self.get_context_data()
        address = context['address']
        if address.is_valid():
            address = address.save()  # zapisz najpierw formularz adresu
            form.instance.address = address  # ustaw adres na formularzu AdvertiseModel
        if form.is_valid():
            form.instance.user = self.request.user
            form.save()
        messages.success(self.request, "Advertise created.")
        # compression
        # pil_image = PilImage.open(form.instance.img)
        # output_io = BytesIO()
        # pil_image.save(output_io, format='JPEG', quality=60)
        # form.instance.img = File(output_io, name=form.instance.img.name)
        return super().form_valid(form)


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
        context['address'] = self.object.address
        # ratings_list = AdvertiseRating.objects.filter(advertise=self.object)
        # paginator = Paginator(ratings_list, 2)
        # page = self.request.GET.get('page')
        # context['ratings'] = paginator.get_page(page)
        return context


class AdvertiseGallery(ListView):
    model = Image
    context_object_name = 'gallery'
    template_name = 'core/advertise/advertise_gallery.html'
    paginate_by = 6

    def get_queryset(self):
        id_advertise = self.kwargs['pk']
        search_input = self.request.GET.get('search_image') or ''
        object_advertise = get_object_or_404(AdvertiseModel, id=id_advertise)
        gallery = super().get_queryset().filter(advertise=object_advertise, title__icontains=search_input).order_by(
            "-created_at")
        return gallery

    def get_context_data(self, **kwargs):
        id_advertise = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        object_advertise = get_object_or_404(AdvertiseModel, id=id_advertise)

        context['id_advertise'] = id_advertise
        # context['user'] = object_advertise.user
        context['is_owner'] = self.request.user == object_advertise.user
        context['search_input'] = self.request.GET.get('search_image') or ''

        print(context['is_owner'])
        return context


class AdvertiseRatingList(ListView):
    model = AdvertiseRating
    context_object_name = 'ratings'
    template_name = 'core/advertise/advertise_rating_list.html'
    paginate_by = 4

    def get_queryset(self):
        id_advertise = self.kwargs['pk']
        object_advertise = get_object_or_404(AdvertiseModel, id=id_advertise)

        rating = super().get_queryset().filter(advertise=object_advertise).order_by("-created_at")
        return rating

    def get_context_data(self, **kwargs):
        id_advertise = self.kwargs['pk']
        context = super().get_context_data(**kwargs)
        object_advertise = get_object_or_404(AdvertiseModel, id=id_advertise)

        context['average_rating'] = AdvertiseRating.objects.filter(advertise=object_advertise).aggregate(Avg('rating'))[
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
        cutomRestrictedGetAdvertise(self.request.user, advertise_id)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if self.request.POST:
            data['address'] = AddressForm(self.request.POST, instance=self.object.address)
        else:
            data['address'] = AddressForm(instance=self.object.address)
        data['current_img'] = self.object.image
        data['is_edit_page'] = True

        return data

    def form_valid(self, form):
        try:
            advert_object = AdvertiseModel.objects.get(id=form.instance.id)
        except ObjectDoesNotExist as e:
            form.add_error(None, f"Not found this advertise")
            return super().form_invalid(form)

        if advert_object.user != self.request.user:
            form.add_error(None, "Only owner can edit advertise")
            return super().form_invalid(form)

        context = self.get_context_data()
        address = context['address']
        if address.is_valid():
            address.save()  # zapisz najpierw formularz adresu
            form.instance.address = address.instance  # ustaw adres na formularzu AdvertiseModel
        if form.is_valid():
            form.instance.advertise.set = advert_object
            form.save()
        messages.success(self.request, "Advertise details updated.")
        # compression
        # pil_image = PilImage.open(form.instance.img)
        # output_io = BytesIO()
        # pil_image.save(output_io, format='JPEG', quality=60)
        # form.instance.img = File(output_io, name=form.instance.img.name)
        return super().form_valid(form)


class AdvertiseDelete(LoginRequiredMixin, DeleteView):
    # its Addres model deltete casacde!!
    model = Address
    context_object_name = 'address_delete'
    template_name = 'core/advertise/advertise_confirm_delete.html'
    success_url = reverse_lazy('user_advertise')

    def get(self, request, *args, **kwargs):
        address_id = self.kwargs['pk']
        # cutomRestrictedGetAdvertise(self.request.user, address_id)
        advert_object = get_object_or_404(AdvertiseModel, address=address_id)
        if advert_object.user != self.request.user:
            raise 404
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        delete_id = self.kwargs['pk']
        try:
            advert_object = AdvertiseModel.objects.get(address=delete_id)
        except ObjectDoesNotExist as e:
            form.add_error(None, f"Not found this advertise")
            return super().form_invalid(form)

        if advert_object.user != self.request.user:
            form.add_error(None, "Only owner can delete advertise!")
            return super().form_invalid(form)

        # form.instance.advertise = advert_object
        messages.error(self.request, "Advertise deleted", extra_tags="danger")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        advert_object = get_object_or_404(AdvertiseModel, address=self.kwargs['pk'])
        context['advertise'] = advert_object
        return context


class AddImageToGallery(LoginRequiredMixin, CreateView):
    model = Image
    form_class = ImageForm
    template_name = 'core/advertise/add_to_gallery.html'
    context_object_name = 'image'

    # possible issues in url
    # redirect to gallery by kwargs id
    # def get_success_url(self):
    #     return self.request.path_info
    def get_success_url(self):
        advertise_id = self.kwargs['advertise_pk']
        return reverse_lazy('gallery', kwargs={'pk': advertise_id})

    def get(self, request, *args, **kwargs):
        advertise_id = self.kwargs['advertise_pk']
        cutomRestrictedGetAdvertise(self.request.user, advertise_id)
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

    def get_success_url(self):
        advertise_id = self.kwargs['advertise_pk']
        return reverse_lazy('gallery', kwargs={'pk': advertise_id})

    def get(self, request, *args, **kwargs):
        advertise_id = self.kwargs['advertise_pk']
        cutomRestrictedGetAdvertise(self.request.user, advertise_id)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_img'] = self.object.image

        return context


class ImageInGalleryDelete(DeleteView):
    model = Image
    context_object_name = 'image'
    template_name = 'core/advertise/image_gallery_confirm_delete.html'

    def get_success_url(self):
        advertise_id = self.kwargs['advertise_pk']
        return reverse_lazy('gallery', kwargs={'pk': advertise_id})

    def get(self, request, *args, **kwargs):
        advertise_id = self.kwargs['advertise_pk']
        cutomRestrictedGetAdvertise(self.request.user, advertise_id)
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
        filter_search = self.request.GET.get('filter_search') or ''
        # addres_qs = Address.objects.filter(town=search_input)
        # print(addres_qs)
        advert_qs = super().get_queryset().filter(address__town=search_input,
                                                  advertise_category=search_category,
                                                  advertise_status='accepted')
        # filter_by_rating = advert_qs.annotate(avg_rating=Avg('advertiserating__rating'))
        #
        # if filter_search == 'best_rating':
        #     filter_by_rating = filter_by_rating.order_by('-avg_rating')
        #     return filter_by_rating

        # __startswith
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
        user_adverts = super().get_queryset().filter(user=self.request.user).select_related('address')
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
        advert_object = get_object_or_404(AdvertiseModel, id=advertise_id)
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
        rating_object = get_object_or_404(AdvertiseRating, id=self.kwargs['pk'])
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

        rating_object = get_object_or_404(AdvertiseRating, id=self.kwargs['pk'])
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


def cutomRestrictedGetAdvertise(user, id):
    try:
        advert_object = AdvertiseModel.objects.get(id=id)
    except ObjectDoesNotExist as e:
        raise Http404

    if advert_object.user != user:
        raise Http404
    return advert_object


class ReportAdvertise(CreateView):
    model = ReportAdvertise
    form_class = ReportAdvertiseForm
    context_object_name = 'report'
    template_name = 'core/reports/report_advertise.html'

    def get_success_url(self):
        advertise_id = self.kwargs['advertise_pk']
        return reverse_lazy('advertise_details', kwargs={'pk': advertise_id})

    def form_valid(self, form):
        advertise_id = self.kwargs['advertise_pk']
        try:
            advertise_object = AdvertiseModel.objects.get(id=advertise_id)
        except ObjectDoesNotExist as e:
            form.add_error(None, f"Not found this advertise")
            return super().form_invalid(form)

        if self.request.user.is_authenticated:
            form.instance.user = self.request.user

        form.instance.advertise = advertise_object
        messages.success(self.request, "Report send")
        return super().form_valid(form)


class AboutUsPage(TemplateView):
    template_name = 'core/about_us.html'


def handler404(request, exception):
    return render(request, 'core/http_status/404.html', status=404)


def handler500(request, *args, **argv):
    return render(request, 'core/http_status/500.html', status=500)

# class TaskList(LoginRequiredMixin, ListView):
#     model = Task
#     # login_url = 'login'
#     context_object_name = 'tasks'
#     paginate_by = 3
#
#     def get_queryset(self):
#         search_input = self.request.GET.get('search_area') or ''
#         tasks = super().get_queryset().filter(user=self.request.user)
#         if search_input:
#             tasks = tasks.filter(title__startswith=search_input)
#         return tasks
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['count'] = self.get_queryset().filter(complete=False).count()
#         context['search_input'] = self.request.GET.get('search_area') or ''
#         return context
#
#
# class TaskDetail(LoginRequiredMixin, DetailView):
#     model = Task
#     context_object_name = 'detail'
#     template_name = 'core/task_detail_name.html'
#
#
# class TaskCreate(LoginRequiredMixin, CreateView):
#     model = Task
#     fields = ['title', 'description', 'complete']
#     success_url = reverse_lazy('task')
#
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         return super(TaskCreate, self).form_valid(form)
#
#
# class TaskUpdate(LoginRequiredMixin, UpdateView):
#     model = Task
#     fields = ['title', 'description', 'complete']
#     success_url = reverse_lazy('task')
#
#
# class TaskDelete(LoginRequiredMixin, DeleteView):
#     model = Task
#     context_object_name = 'task'
#     success_url = reverse_lazy('task')
