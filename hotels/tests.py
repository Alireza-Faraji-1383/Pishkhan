from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Hotel, RoomType, Reservation, Review
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.hotel = Hotel.objects.create(
            owner=self.user,
            name='Test Hotel',
            city='Test City',
            address='Test Address'
        )

    def test_create_review(self):
        """Test creating a review"""
        review = Review.objects.create(
            user=self.user,
            hotel=self.hotel,
            rating=5,
            comment='Great hotel!'
        )
        
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.hotel, self.hotel)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great hotel!')
        self.assertIsNotNone(review.created_at)
        self.assertIsNotNone(review.updated_at)

    def test_rating_validation(self):
        """Test rating validation (1-5)"""
        review = Review(
            user=self.user,
            hotel=self.hotel,
            rating=6,  # Invalid rating
            comment='Bad hotel!'
        )
        
        with self.assertRaises(Exception):  # Will raise validation error when saved
            review.full_clean()

    def test_unique_constraint(self):
        """Test that a user can't review the same hotel twice"""
        Review.objects.create(
            user=self.user,
            hotel=self.hotel,
            rating=5,
            comment='Great hotel!'
        )
        
        # Try to create another review for the same user and hotel
        with self.assertRaises(Exception):  # Will raise integrity error
            Review.objects.create(
                user=self.user,
                hotel=self.hotel,
                rating=3,
                comment='Average hotel'
            )


class ReviewAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', role='customer')
        self.owner = User.objects.create_user(username='hotelowner', password='testpass', role='hotel_owner')
        self.hotel = Hotel.objects.create(
            owner=self.owner,
            name='Test Hotel',
            city='Test City',
            address='Test Address'
        )
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            name='Deluxe Room',
            price_per_night=Decimal('100.00'),
            capacity=2,
            inventory=5
        )
        self.reservation = Reservation.objects.create(
            user=self.user,
            room_type=self.room_type,
            check_in_date=date.today() + timedelta(days=1),
            check_out_date=date.today() + timedelta(days=3),
            total_price=Decimal('200.00'),
            status=Reservation.STATUS_CONFIRMED
        )

    def test_create_review_with_reservation(self):
        """Test creating a review with a valid reservation"""
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('hotels:review-list')
        data = {
            'hotel': self.hotel.id,
            'rating': 5,
            'comment': 'Excellent stay!',
            'reservation': self.reservation.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Excellent stay!')

    def test_create_review_without_reservation_but_with_confirmed_stay(self):
        """Test creating a review when user has a confirmed reservation at the hotel"""
        # Change reservation status to completed to simulate past stay
        self.reservation.status = Reservation.STATUS_CONFIRMED
        self.reservation.save()
        
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('hotels:review-list')
        data = {
            'hotel': self.hotel.id,
            'rating': 4,
            'comment': 'Good experience.'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

    def test_create_review_without_any_reservation(self):
        """Test that a user cannot create a review without staying at the hotel"""
        # Create a different user who hasn't stayed at the hotel
        other_user = User.objects.create_user(username='otheruser', password='testpass', role='customer')
        self.client.login(username='otheruser', password='testpass')
        
        url = reverse('hotels:review-list')
        data = {
            'hotel': self.hotel.id,
            'rating': 3,
            'comment': 'Never stayed here but heard it\'s okay.'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('برای ثبت نظر باید حداقل یک بار در این هتل اقامت داشته باشید.', str(response.data))

    def test_create_duplicate_review(self):
        """Test that a user cannot create multiple reviews for the same hotel"""
        # Create first review
        Review.objects.create(
            user=self.user,
            hotel=self.hotel,
            rating=5,
            comment='Great hotel!'
        )
        
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('hotels:review-list')
        data = {
            'hotel': self.hotel.id,
            'rating': 3,
            'comment': 'Changed my mind.'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('شما قبلاً برای این هتل نظر داده‌اید.', str(response.data))

    def test_list_reviews(self):
        """Test listing all reviews"""
        # Create some reviews
        Review.objects.create(
            user=self.user,
            hotel=self.hotel,
            rating=5,
            comment='Great hotel!'
        )
        
        url = reverse('hotels:review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_reviews_by_hotel(self):
        """Test filtering reviews by hotel"""
        # Create reviews for different hotels
        hotel2 = Hotel.objects.create(
            owner=self.owner,
            name='Another Hotel',
            city='Another City',
            address='Another Address'
        )
        
        Review.objects.create(
            user=self.user,
            hotel=self.hotel,
            rating=5,
            comment='Great hotel!'
        )
        
        Review.objects.create(
            user=self.user,
            hotel=hotel2,
            rating=3,
            comment='Average hotel.'
        )
        
        url = reverse('hotels:review-list')
        response = self.client.get(url, {'hotel_id': self.hotel.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['hotel']['id'], self.hotel.id)

    def test_update_own_review(self):
        """Test that a user can update their own review"""
        review = Review.objects.create(
            user=self.user,
            hotel=self.hotel,
            rating=5,
            comment='Great hotel!'
        )
        
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('hotels:review-detail', kwargs={'pk': review.id})
        data = {
            'rating': 4,
            'comment': 'Good hotel, but could be better.'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['comment'], 'Good hotel, but could be better.')

    def test_update_other_users_review(self):
        """Test that a user cannot update another user's review"""
        other_user = User.objects.create_user(username='otheruser', password='testpass', role='customer')
        review = Review.objects.create(
            user=other_user,
            hotel=self.hotel,
            rating=3,
            comment='Average hotel.'
        )
        
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('hotels:review-detail', kwargs={'pk': review.id})
        data = {
            'rating': 5,
            'comment': 'Actually great!'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_review(self):
        """Test that a user can delete their own review"""
        review = Review.objects.create(
            user=self.user,
            hotel=self.hotel,
            rating=5,
            comment='Great hotel!'
        )
        
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('hotels:review-detail', kwargs={'pk': review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_delete_other_users_review(self):
        """Test that a user cannot delete another user's review"""
        other_user = User.objects.create_user(username='otheruser', password='testpass', role='customer')
        review = Review.objects.create(
            user=other_user,
            hotel=self.hotel,
            rating=3,
            comment='Average hotel.'
        )
        
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('hotels:review-detail', kwargs={'pk': review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 1)


class HotelModelReviewMethodsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')
        self.hotel = Hotel.objects.create(
            owner=self.user1,
            name='Test Hotel',
            city='Test City',
            address='Test Address'
        )

    def test_average_rating_calculation(self):
        """Test that the average rating is calculated correctly"""
        Review.objects.create(
            user=self.user1,
            hotel=self.hotel,
            rating=5,
            comment='Great!'
        )
        
        Review.objects.create(
            user=self.user2,
            hotel=self.hotel,
            rating=3,
            comment='Average.'
        )
        
        # Average should be (5 + 3) / 2 = 4.0
        self.assertEqual(self.hotel.average_rating(), 4.0)

    def test_average_rating_with_single_review(self):
        """Test average rating with only one review"""
        Review.objects.create(
            user=self.user1,
            hotel=self.hotel,
            rating=5,
            comment='Great!'
        )
        
        self.assertEqual(self.hotel.average_rating(), 5.0)

    def test_average_rating_with_no_reviews(self):
        """Test average rating when there are no reviews"""
        self.assertEqual(self.hotel.average_rating(), 0)

    def test_total_reviews_count(self):
        """Test that the total review count is calculated correctly"""
        Review.objects.create(
            user=self.user1,
            hotel=self.hotel,
            rating=5,
            comment='Great!'
        )
        
        Review.objects.create(
            user=self.user2,
            hotel=self.hotel,
            rating=3,
            comment='Average.'
        )
        
        self.assertEqual(self.hotel.total_reviews(), 2)

    def test_total_reviews_count_with_no_reviews(self):
        """Test total review count when there are no reviews"""
        self.assertEqual(self.hotel.total_reviews(), 0)
