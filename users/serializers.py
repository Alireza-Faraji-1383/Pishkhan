from rest_framework import serializers

from users.models import User, VerificationCode



class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()



class UserRegistrationSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True, max_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'code']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True},
        }

    def validate(self, data):
        email = data.get('email')
        code = data.get('code')

        try:
            verification_record = VerificationCode.objects.get(user__email=email, code=code, is_used=False)
            if verification_record.is_expired():
                raise serializers.ValidationError({'code': 'کد تایید منقضی شده است.'})
            
            self.context['verification_record'] = verification_record
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError({'code': 'کد تایید اشتباه است.'})
        
        return data

    def create(self, validated_data):

        email = validated_data['email']
        user, _ = User.objects.get_or_create(email=email, defaults={'is_active': False})
        
        user.username = validated_data['username']
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.set_password(validated_data['password'])
        user.is_active = True
        user.save()
        
        verification_record = self.context['verification_record']
        verification_record.is_used = True
        verification_record.save()
        
        return user