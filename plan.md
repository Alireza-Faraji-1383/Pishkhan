# Comment Feature Implementation Plan

## Overview
Implement a comment/review feature for the hotel reservation website allowing users to add reviews for hotels they've stayed at. The feature will include models, serializers, views, permissions, and API endpoints.

## Current State Analysis
- Existing models: Hotel, RoomType, Reservation, User (with roles: customer, hotel_owner)
- There's already a commented-out Review model in hotels/models.py
- Current permissions: IsHotelAdmin for hotel owners
- API structure uses DRF ViewSets with StandardResponseMixin

## Implementation Plan

### Phase 1: Model Implementation
1. **Uncomment and enhance the Review model** in hotels/models.py:
   - Add proper relationships (user, hotel, optional reservation)
   - Add rating (1-5 scale) and comment fields
   - Add created_at and updated_at timestamps
   - Add proper constraints (unique review per user/hotel combination)
   - Add proper verbose names in Persian

2. **Add reverse relationship** to Hotel model (already exists: related_name='reviews')

### Phase 2: Serializer Implementation
1. **Create ReviewSerializer** in hotels/serializers.py:
   - Include fields: id, user (read-only), hotel (read-only), rating, comment, created_at
   - Handle validation for rating range (1-5)
   - Prevent duplicate reviews per user/hotel

2. **Create CreateReviewSerializer**:
   - For creating new reviews
   - Validate that user has made a reservation at the hotel before reviewing

### Phase 3: View Implementation
1. **Create ReviewViewSet** in hotels/views.py:
   - Allow authenticated users to create reviews
   - Allow all users to read reviews
   - Implement proper filtering options
   - Add permission checks to prevent duplicate reviews
   - Add validation to ensure user has stayed at the hotel

2. **Add permissions**:
   - Users can only create reviews for hotels they've stayed at
   - Users can update/delete their own reviews
   - Hotel owners can moderate reviews for their hotels

### Phase 4: URL Configuration
1. **Add review endpoints** to hotels/urls.py:
   - Register ReviewViewSet with router
   - Add nested routes for hotel-specific reviews

### Phase 5: Integration with Existing Models
1. **Update HotelSerializer** to optionally include average rating and review count
2. **Consider adding a method** to Hotel model to calculate average rating

### Phase 6: Testing
1. **Write unit tests** for:
   - Model validation
   - Serializer validation
   - View permissions and functionality
   - API endpoint behavior

### Phase 7: Documentation
1. **Update API documentation** with new endpoints
2. **Add docstrings** to new classes and methods

## Technical Considerations

### Permissions Strategy
- Only authenticated users can create reviews
- Users can only review hotels they've stayed at (based on reservations)
- Users can only edit/delete their own reviews
- Hotel owners can moderate reviews for their hotels
- All users can read reviews

### Validation Rules
- Rating must be between 1-5
- Comment length limits (optional)
- Prevent duplicate reviews per user/hotel
- Verify reservation exists before allowing review

### Data Relationships
- Review belongs to User (many-to-one)
- Review belongs to Hotel (many-to-one)
- Review optionally belongs to Reservation (one-to-one, nullable)
- Hotel has many Reviews (one-to-many)

## Implementation Steps

### Step 1: Model Creation
```python
# Un-comment and enhance the Review model
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'hotel')
        ordering = ['-created_at']
```

### Step 2: Migration Creation
- Create and run migration for Review model

### Step 3: Serializer Development
- Create ReviewSerializer
- Create CreateReviewSerializer

### Step 4: View Development
- Create ReviewViewSet
- Implement CRUD operations with proper permissions

### Step 5: URL Configuration
- Add review endpoints to router

### Step 6: Integration
- Update Hotel model with average rating calculation
- Update HotelSerializer to include ratings info


## Success Criteria
- Users can submit reviews for hotels they've stayed at
- Reviews include rating (1-5) and comment
- Duplicate reviews per user/hotel are prevented
- Proper permissions are enforced
- API follows existing patterns and conventions
- All tests pass
- Feature is well-documented