from rest_framework import serializers
from . import models

# Serializers take models and turn them into json objects

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = models.User
        fields = ['id', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True},
                        'first_name': {'required': True},
                        'last_name': {'required': True}}
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        chefdat = {
            'user': instance.id,
            'cuisine': 'Global',
            'meanrating': 0,
            'bio': 'New chef!',
            'working': False
        }
        chefser = ChefSerializer(data=chefdat)
        if chefser.is_valid():
            chefser.save()
        return instance
    
    def update(self, instance, validated_data):
        newpass = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if newpass is not None:
            instance.set_password(newpass)
        instance.save()
        return instance

class ChefSerializer(serializers.ModelSerializer):
    class Meta():
        model = models.Chef
        fields = ['id', 'cuisine', 'meanrating', 'bio', 'profilepic','working', 'user']
        extra_kwargs = {'user': {'write_only': True}}

    def update(self, instance, validated_data):
        validated_data.pop('user', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class ItemSerializer(serializers.ModelSerializer):
    class Meta():
        model = models.Item
        fields = ['id', 'name', 'price', 'description', 'available', 'chef']
    
    def update(self, instance, validated_data):
        validated_data.pop('chef', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance