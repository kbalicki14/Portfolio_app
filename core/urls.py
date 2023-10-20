from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views
from .views import TaskList, TaskDetail, TaskCreate, TaskUpdate, TaskDelete, CustomLoginView, RegisterView, \
    imageUpload, AdvertList, AdvertiseCreate

from django.contrib.auth.views import LogoutView

# logout

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    path('', TaskList.as_view(), name='task'),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task_detail'),
    path('create/', TaskCreate.as_view(), name='task_create'),
    path('update/<int:pk>/', TaskUpdate.as_view(), name='task_update'),
    path('delete/<int:pk>/', TaskDelete.as_view(), name='task_delete'),
    # path('upload/', imageUpload, name='upload'),
    path('advert/', AdvertList.as_view(), name='advert_list'),
    path('upload/', AdvertiseCreate.as_view(), name='advertise'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
