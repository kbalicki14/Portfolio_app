from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views
from .views import TaskList, TaskDetail, TaskCreate, TaskUpdate, TaskDelete, CustomLoginView, RegisterView, \
    imageUpload, AdvertList, AdvertiseCreate, AddMultiImage, CreateImagesToGallery, WelcomePage, AdvertiseUpdate, \
    AddImageToGallery, AdvertiseDetails, CurrentUserAdvertise, AdvertiseDelete, AdvertiseGallery, ProfileDetail

from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    path('index/', WelcomePage.as_view(), name='welcome'),
    path('', TaskList.as_view(), name='task'),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task_detail'),
    path('create/', TaskCreate.as_view(), name='task_create'),
    path('update/<int:pk>/', TaskUpdate.as_view(), name='task_update'),
    path('delete/<int:pk>/', TaskDelete.as_view(), name='task_delete'),

    # path('upload/', imageUpload, name='upload'),
    path('advert/', AdvertList.as_view(), name='advert_list'),
    path('advertise_create/', AdvertiseCreate.as_view(), name='advertise'),
    path('advertise_details/<int:pk>/', AdvertiseDetails.as_view(), name='advertise_details'),
    path('advertise_update/<int:pk>/', AdvertiseUpdate.as_view(), name='advertise_update'),
    path('advertise_delete/<int:pk>/', AdvertiseDelete.as_view(), name='advertise_delete'),

    path('advertise_details/<int:pk>/gallery/', AdvertiseGallery.as_view(), name='gallery'),
    path('multi_image/', CreateImagesToGallery.as_view(), name='multi_image'),
    path('add_image/<int:advertise_pk>/', AddImageToGallery.as_view(), name='add_image'),
    # path('gallery/', AdvertiseCreate.as_view(), name='advertise'),
    path('multi_image_work/', AddMultiImage, name='multi_image_work'),
    path('user_advertise/', CurrentUserAdvertise.as_view(), name='user_advertise'),
    path('user_profile/', ProfileDetail.as_view(), name='profile_detail'),

    # <int:advertiseModel_pk>
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
