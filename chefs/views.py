from django.http import HttpResponse
from django.db.models import Value
from django.db.models.functions import Concat
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from . import serializers
from . import models
import jwt, datetime, os
from django.conf import settings
# Create your views here.

# Need a reset password (partial auth) and email validation when registering
# Rate limiting for logging in, register(email), item posting, item searching. Field validation on frontend
# Limit filesize of image uploads for profile pictures and items
# Get a certain number of items, sort items where available = true and chef working = true first, 
# get items by name, get items by chef name, get items by price range, get items by chef cuisine, 
# get item by id
# get item_images by itemid
# package app, delete dev lines, push to prod

# Later on a View to post a rating, rating model, also add images model.
# message: logged out, unauthenticated, expired token = redirect to login page

secret = 'FDSIEnfasdeipPOSDFKer'

def getPayload(request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Unauthenticated.")
        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Expired token.")
        return payload

def auth(user, pw):
    if pw is None:
        raise AuthenticationFailed('Provide password.')
    if not user.check_password(pw):
        raise AuthenticationFailed('Incorrect password.')

class RegisterView(APIView): # enforce required fields and lengths and email format on frontend
    def post(self, request):
        email = request.data.get('email')
        users = models.User.objects.filter(email=email)
        if(users.exists()):
            return Response({"message": "Email in use"}, status=status.HTTP_409_CONFLICT) # so frontend can see when email is in use
        serializer = serializers.UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = models.User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed("User not found")
        pw = request.data.get('password')
        auth(user, pw)        
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=40),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, secret, algorithm='HS256')

        response = Response({'jwt': token})
        response.set_cookie('jwt', token, httponly=True)
        return response

class LogoutView(APIView):
    def post(self, request):
        response = Response({'message': 'Logged Out'})
        response.delete_cookie('jwt')
        return response

class UserView(APIView):
    def get(self, request): # will this be used? this only gets the logged in user
        payload = getPayload(request)       
        user = models.User.objects.filter(id=payload['id']).first()
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request): #edit name, email, password... is this okay?
        payload = getPayload(request)       
        user = models.User.objects.filter(id=payload['id']).first()
        pw = request.data.get('oldpassword')
        auth(user, pw)
        email = request.data.get('email')
        users = models.User.objects.filter(email=email).exclude(id=payload['id'])
        if(users.exists()):
            return Response({"message": "Email in use"}, status=status.HTTP_409_CONFLICT)
        
        serializer = serializers.UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        payload = getPayload(request)       
        user = models.User.objects.filter(id=payload['id']).first()
        pw = request.data.get('password')
        auth(user, pw)
        user.delete()
        response = Response({'message': 'Logged out'})
        response.delete_cookie('jwt')
        return response

class ChefView(APIView):
     # make search by name? Or nah. Make a get chef from web token
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request):
        chefid = request.query_params.get('chefid')
        if chefid is None:
            payload = getPayload(request) # for a chef checking their own profile...
            chef = models.User.objects.filter(id=payload['id']).first().chef
        else:
            chef = models.Chef.objects.filter(id=chefid).first()
            if chef is None:
                return Response({"message": "Chef not found"}, status=status.HTTP_404_NOT_FOUND) 
        serializer = serializers.ChefSerializer(chef)
        jsondat = serializer.data
        jsondat['first_name'] = chef.user.first_name
        jsondat['last_name'] = chef.user.last_name
        return Response(jsondat)
    
    def put(self, request):
        payload = getPayload(request)
        chef = models.User.objects.filter(id=payload['id']).first().chef
        oldpath = None
        if chef.profilepic.url != '/media/profilepics/default.jpg':
            if request.data.get('profilepic') is not None:
                oldpath = chef.profilepic.path
        serializer = serializers.ChefSerializer(chef, data=request.data, partial=True)
        if(serializer.is_valid()):
            serializer.save()
            if oldpath is not None:
                os.remove(oldpath)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class ItemView(APIView):
    def get(self, request):
        name = request.query_params.get('name')
        chef_name = request.query_params.get('chefname')
        min_price = request.query_params.get('minprice')
        max_price = request.query_params.get('maxprice')
        cuisine = request.query_params.get('cuisine')
        itemid = request.query_params.get('id')
        chefid = request.query_params.get('chefid')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        items = models.Item.objects.all()

        if itemid:
            items = items.filter(id=itemid)
            if not items.exists():
                return Response({"message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializers.ItemSerializer(items.first()).data)
        if chefid:
            items = items.filter(chef__id=chefid)
            page = paginator.paginate_queryset(items, request)
            ser = serializers.ItemSerializer(page, many=True)
            return paginator.get_paginated_response(ser.data)
        if name:
            items = items.filter(name__icontains=name)
        if chef_name:
            items = items.annotate(chef_full_name=Concat('chef__user__first_name', Value(' '), 'chef__user__last_name'))
            items = items.filter(chef_full_name__icontains=chef_name)
        if min_price:
            items = items.filter(price__gte=float(min_price))
        if max_price:
            items = items.filter(price__lte=float(max_price))
        if cuisine:
            items = items.filter(chef__cuisine__icontains=cuisine)
        items = items.order_by('-available', '-chef__working')
        page = paginator.paginate_queryset(items, request)
        serializer = serializers.ItemSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        payload = getPayload(request)
        chef = models.User.objects.filter(id=payload['id']).first().chef
        dat = request.data.copy()
        dat['chef'] = chef.id
        serializer = serializers.ItemSerializer(data=dat)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):  # pass in item id
        payload = getPayload(request)
        chef = models.User.objects.filter(id=payload['id']).first().chef
        items = models.Item.objects.filter(id=request.data.get('id'))
        if not items.exists():
            return Response({"message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        item = items.first()
        if item.chef.id is not chef.id:
            raise AuthenticationFailed("Unauthenticated")
        serializer = serializers.ItemSerializer(item, data=request.data, partial=True)
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request): # pass in item id
        payload = getPayload(request)
        chef_id = models.User.objects.filter(id=payload['id']).first().chef.id
        items = models.Item.objects.filter(id=request.data.get('id'))
        if not items.exists():
            return Response({"message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        item = items.first()
        if item.chef.id is not chef_id:
            raise AuthenticationFailed("Unauthenticated")
        item.delete()
        return Response({'message': 'Deleted item'})

class ItemImageView:
    def get(self, request):
        pass
    def post(self, request):
        pass

def getMenus(request):
    return HttpResponse("Menus.")
