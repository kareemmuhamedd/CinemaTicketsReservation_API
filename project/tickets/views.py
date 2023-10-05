from django.shortcuts import render
from django.http.response import JsonResponse
from .models import Movie, Guest, Reservation
from rest_framework.decorators import api_view
from .serializers import GuestSerializer, MovieSerializer, ReservationSerializer
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from rest_framework import generics, mixins, viewsets


from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.

# 1 without REST and no model query


def no_rest_no_model(request):
    guests = [
        {
            'id': 1,
            'Name': 'kareem',
            'mobile': 1234546542,
        },
        {
            'id': 2,
            'Name': 'muhamed',
            'mobile': 165656652,
        }
    ]
    return JsonResponse(guests, safe=False)

# 2 model data default django without rest


def no_rest_from_model(requist):
    # in this line i call all data about the guest
    data = Guest.objects.all()
    # in the response i will get a map
    # in the key 'guests' i will generate list and add the name and mobile only, that i have returned from the data
    # look if you type data.values() without any data in the () it will return all values
    response = {

        'guests': list(data.values('name', 'mobile'))
    }
    return JsonResponse(response)

# 3 function base views
# 3.1 GET POST


@api_view(['GET', 'POST'])
# FBV function base view
def FBV_List(request):
    # GET
    if request.method == 'GET':
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data)
    # POST
    elif request.method == 'POST':
        # in this the 'GuestSerializer' will take the data you send in the post
        # and save it in the model in the table
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # the next return like if i send data with null values and it required
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

# 3.2 GET PUT DELETE


@api_view(['GET', 'PUT', 'DELETE'])
def FBV_pk(request, pk):
    try:
        guest = Guest.objects.get(pk=pk)
    except Guest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # GET
    if request.method == 'GET':
        serializer = GuestSerializer(guest)
        return Response(serializer.data)
    # PUT
    elif request.method == 'PUT':
        # we will send the guest we need to update
        serializer = GuestSerializer(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # the next return like if i send data with null values and it required
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # DELETE
    if request.method == 'DELETE':
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CBV class base views

# 4.1 List and Create == GET and POST

class CBV_List(APIView):
    def get(self, request):
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serialiser = GuestSerializer(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED,)
        return Response(serialiser.data, status=status.HTTP_400_BAD_REQUEST,)

 # 4.2 GET PUT DELETE class based views -- pk


class CBV_pk(APIView):
    def get_object(self, pk):
        try:
            return Guest.objects.get(pk=pk)
        except Guest.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest)
        return Response(serializer.data)

    def put(self, request, pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        guest = self.get_object(pk)
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# 5 Mixins
# 5.1 mixins list get post


class mixins_list(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def get(self, request):
        return self.list(request)

    def post(self, request):
        return self.create(request)

# 5.2 mixins get put delete


class mixins_pk(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def get(self, request, pk):
        return self.retrieve(request)

    def put(self, request, pk):
        return self.update(request)

    def delete(self, request, pk):
        return self.destroy(request)


# 6 Generics

# 6.1 get and post
# i will use the security in thes two end points

class generics_list(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    #! the second to line of codes fo the authenticate the end point using normal authenticate
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    #! the following code for auth token 
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]





# 6.2 get put delete

class generics_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    #! the second to line of codes fo the authenticate the end point using normal authenticate
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    #! the following code for auth token 
    authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]


# 7 viewsets
class viewsets_guest(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class viewsets_movie(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    # the next 2 line of code is using for searching about a movie
    filter_backends = [filters.SearchFilter]
    search_fields = ['movie']


class viewsets_reservation(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


# ----- we will create some features using function based view -----#

# 8 Find movie
@api_view(["GET"])
def find_movie(request):
    try:
        movies = Movie.objects.filter(
            hall=request.data["hall"],
            movie=request.data["movie"],
        )
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)
    except Movie.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


# 9 create new reservation
@api_view(['POST'])
def new_reservation(request):
    try:
        guest = Guest()
        guest.name = request.data["name"]
        guest.mobile = request.data["mobile"]
        print(guest.name)
        print(guest.mobile)
        guest.save()
        movie = Movie.objects.get(
            hall=request.data["hall"],
            movie=request.data["movie"],
        )
        reservation = Reservation()
        reservation.guest = guest
        reservation.movie = movie
        reservation.save()
        serializer = ReservationSerializer(reservation)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
    except Guest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
