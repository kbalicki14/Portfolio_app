from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from .models import AdvertiseCategory, AdvertiseModel, Address, AdvertiseRating


# Create your tests here.

# Login register change username test


class AuthTest(TestCase):
    def setUp(self):
        self.username = 'Adam'
        self.password = 'testpassword123!'
        self.user = User.objects.create_user(self.username, password=self.password)

    def test_login(self):
        response = self.client.post(reverse('login'), {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, 302)  # przekierowanie po udanym logowaniu
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_registration(self):
        new_username = 'newuser'
        new_password = 'newpassword123!'
        response = self.client.post(reverse('register'),
                                    {'username': new_username, 'password1': new_password, 'password2': new_password})
        self.assertEqual(response.status_code, 302)  # przekierowanie po udanej rejestracji
        new_user = User.objects.get(username=new_username)
        self.assertIsNotNone(new_user)
        self.assertTrue(new_user.is_authenticated)

    def test_redirect_if_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 302)

    def test_change_user_name(self):
        change_username = 'John'
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('change_username'), {'username': change_username})
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username=change_username)
        self.assertEqual(user.username, change_username)

    # def test_change_user_password(self):
    #     change_password = 'changepassword123!'
    #     self.client.login(username=self.username, password=self.password)
    #     response = self.client.post(reverse('change_password'),
    #                                 {'old_password': self.password,
    #                                  'new_password1': change_password,
    #                                  'new_password2': change_password})
    #     self.assertEqual(response.status_code, 302)
    #     user = User.objects.get(username=self.username)
    #     self.assertTrue(user.check_password(change_password))


class AdvertiseTest(TestCase):
    def setUp(self):
        self.username = 'Adam'
        self.password = 'testpassword123!'
        self.user = User.objects.create_user(self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

        self.address = Address.objects.create(
            street='Testowa',
            street_number='123',
            town='Wroclaw',
            zip_code='12345'
        )
        self.category = AdvertiseCategory.objects.create(category_name='Barber')
        self.advertise1 = AdvertiseModel.objects.create(
            user=self.user,
            title='Test Advertise 1',
            description='This is a test advertise.',
            phone_number='+48123456789',
            advertise_status='accepted',
            advertise_category=self.category,
            address=self.address
        )

    def test_create_advertise(self):
        advertise = AdvertiseModel.objects.create(
            user=self.user,
            title='Test Advertise',
            description='This is a test advertise.',
            phone_number='+48123456789',
            advertise_status='accepted',
            advertise_category=self.category,
            address=Address.objects.create(
                street='Test Street',
                street_number='123',
                town='Test Town',
                zip_code='12345'))
        self.assertEqual(advertise.title, 'Test Advertise')
        self.assertEqual(advertise.description, 'This is a test advertise.')
        self.assertEqual(advertise.phone_number, '+48123456789')
        self.assertEqual(advertise.advertise_status, 'accepted')
        self.assertEqual(advertise.advertise_category, self.category)
        self.assertEqual(advertise.address, advertise.address)

    def test_address_str(self):
        self.assertEqual(str(self.address), 'Testowa 123 Wroclaw')

    def user_create_advertise(self):
        response = self.client.post(reverse('advertise'), {
            'user': self.user,
            'title': "User advertise",
            'description': "This is a test advertise.",
            'phone_number': "+48123456789",
            'advertise_status': "accepted",
            'advertise_category': self.category,
            'address': self.address,
        })
        self.assertEqual(response.status_code, 200)
        advert = AdvertiseModel.objects.get(title="User advertise")
        self.assertEqual(advert.title, "User advertise")

    def test_advert_list(self):
        response = self.client.get(reverse('advert_list'),
                                   {'search_area': 'Wroclaw', 'search_category': self.category.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['advert']), 1)

    def test_rating_advertise(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('rating', kwargs={'pk': self.advertise1.pk}), {
            'rating': 5.0,
            'comment': 'Great!'
        })
        self.assertEqual(response.status_code, 302)  # przekierowanie po udanym dodaniu oceny
        rating = AdvertiseRating.objects.get(advertise=self.advertise1)
        self.assertEqual(rating.rating, 5.0)
        self.assertEqual(rating.comment, 'Great!')
