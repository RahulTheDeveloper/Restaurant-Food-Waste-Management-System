from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RawMaterial, RestaurantMenu, Donation, Transaction
from .serializers import RawMaterialSerializer, MenuSerializer,NewMenuSerializer, ListRawMaterialSerializer, DonateRestaurantMenuSerializer, DonateRawMaterialSerializer, DonationSerializer, SellRestaurantMenuByClientSerializer, RestaurantTransactionHistorySerializer, AppUserTransactionHistorySerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
import pandas as pd
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from users.models import Client



class MenuApiView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        request.data['client'] = request.user.id
        serializer = NewMenuSerializer(data=request.data)
        if serializer.is_valid():
            menu_instance = serializer.save()  # Save the object
            response_serializer = NewMenuSerializer(menu_instance)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED) # Return the ID from the saved instance
        else:
            return Response("Error in saving Data",status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, pk,*args, **kwargs):
        object = RestaurantMenu.objects.get(id=pk)

        serializer = NewMenuSerializer(object, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Data Updated'},status=status.HTTP_200_OK)
        else:
            return Response("Error in saving Data",status=status.HTTP_400_BAD_REQUEST)
        
        
class ListMenuView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        queryset = RestaurantMenu.objects.filter(client=user)

        page_size = int(request.query_params.get("page_size", 10))
        page_number = int(request.query_params.get("page", 1))
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)

        serializer = MenuSerializer(page.object_list, many=True)
        return Response({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "results": serializer.data,
        })
        
class ListAppUserMenuView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        queryset = RestaurantMenu.objects.all()

        page_size = int(request.query_params.get("page_size", 10))
        page_number = int(request.query_params.get("page", 1))
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)

        serializer = MenuSerializer(page.object_list, many=True)
        return Response({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "results": serializer.data,
        })
        
class MenuDetails(APIView):
    
    def get(self, request, pk):

        try:
            object = RestaurantMenu.objects.get(id=pk)
        except RestaurantMenu.DoesNotExist:
            return Response({"error": "Campaign result not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MenuSerializer(object)
        return Response(serializer.data)
    
    
    
## Toggle donate in Restaurant Menu

# class ToggleDonateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, menu_id):
#         # Retrieve the object
#         menu_item = get_object_or_404(RestaurantMenu, id=menu_id, client=request.user)

#         # Toggle the donate field
#         menu_item.donate = not menu_item.donate
#         menu_item.save()

#         return Response(
#             {"message": "Toggled successfully", "donate": menu_item.donate},
#             status=status.HTTP_200_OK
#         )


class DonateRestaurantMenuView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DonateRestaurantMenuSerializer(data=request.data)
        if serializer.is_valid():
            menu_id = serializer.validated_data['menu_id']
            quantity = serializer.validated_data['quantity']
            
            try:
                menu = RestaurantMenu.objects.get(id=menu_id)
                client = request.user
                
                message = menu.donate(client, quantity)
                return Response({"message": message}, status=status.HTTP_200_OK)
            
            except RestaurantMenu.DoesNotExist:
                return Response({"error": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DonateRawMaterialView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DonateRawMaterialSerializer(data=request.data)
        if serializer.is_valid():
            rawMaterial_id = serializer.validated_data['rawMaterial_id']
            quantity = serializer.validated_data['quantity']
            
            try:
                rawMaterial = RawMaterial.objects.get(id=rawMaterial_id)
                client = request.user
                
                message = rawMaterial_id.donate(client, quantity)
                return Response({"message": message}, status=status.HTTP_200_OK)
            
            except RestaurantMenu.DoesNotExist:
                return Response({"error": "Raw Material item not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class RawMaterialUploadView(APIView):
    permission_classes = [IsAuthenticated]
    

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        excel_file = request.FILES['file']

        # Check file extension
        if not excel_file.name.endswith('.xlsx'):
            return Response({'error': 'File is not a valid Excel file'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read the Excel file using pandas
            df = pd.read_excel(excel_file)

            # Validate the required columns
            required_columns = ['name', 'temperature', 'humidity', 'pH', 'microbial_count', 'weight']
            for column in required_columns:
                if column not in df.columns:
                    return Response({'error': f'Missing required column: {column}'}, status=status.HTTP_400_BAD_REQUEST)

            # Iterate over each row and save to the database
            raw_materials = []
            for _, row in df.iterrows():
                raw_material = RawMaterial(
                    name=row.get('name'),
                    temperature=row.get('temperature'),
                    humidity=row.get('humidity'),
                    pH=row.get('pH'),
                    microbial_count=row.get('microbial_count'),
                    weight=row.get('weight'),
                    client = request.user
                )
                raw_materials.append(raw_material)

            # Bulk create raw materials
            RawMaterial.objects.bulk_create(raw_materials)

            return Response({'message': f'{raw_materials} raw materials uploaded successfully!'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        
        try:
            object = RawMaterial.objects.get(id=pk)
            serializer = RawMaterialSerializer(object, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({'msg': 'Data Updated'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class ListRawMaterialView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Ensure the user is a `Client` and fetch their raw materials
        if not isinstance(user, Client):
            return Response({"error": "Invalid user type."}, status=403)

        # Filter raw materials by the authenticated user
        queryset = RawMaterial.objects.filter(client=user)
        
        # Pagination
        page_size = int(request.query_params.get("page_size", 10))
        page_number = int(request.query_params.get("page", 1))
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)
        
        # Serialize and return paginated results
        serializer = ListRawMaterialSerializer(page.object_list, many=True)
        return Response({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "results": serializer.data,
        })

        
class RawMaterialDetails(APIView):
    
    def get(self, request,pk, *args, **kwargs):
        try:
            object = RestaurantMenu.objects.get(id=pk)
        except RestaurantMenu.DoesNotExist:
            return Response({"error": "Campaign result not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MenuSerializer(object)
        return Response(serializer.data)    
        


class ListDonationItems(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        
        page_size = int(request.query_params.get("page_size", 10))
        page_number = int(request.query_params.get("page", 1))
        
        user = request.user
        donated_items = Donation.objects.filter(client=user)
        
        paginator = Paginator(donated_items, page_size)
        page = paginator.get_page(page_number)
        
        
        serializer = DonationSerializer(page.object_list, many=True)
        return Response({
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "results": serializer.data,
            })
        
        

class SellRestaurantMenuByClientView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, *args, **kwargs):
        id = request.data['id']
        object = RestaurantMenu.objects.get(id=id)
        serializer = SellRestaurantMenuByClientSerializer(object, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            return Response({"msg": serializer.data}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RestaurantTransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Transaction.objects.filter(seller=user)
        
        page_size = int(request.query_params.get("page_size", 10))
        page_number = int(request.query_params.get("page", 1))
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)
        serializer = RestaurantTransactionHistorySerializer(page.object_list, many=True)
        
        return Response({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "results": serializer.data,
        })
        
class AppUserTransactionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Transaction.objects.filter(buyer=user)
        
        page_size = int(request.query_params.get("page_size", 10))
        page_number = int(request.query_params.get("page", 1))
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)
        serializer = AppUserTransactionHistorySerializer(page.object_list, many=True)
        
        return Response({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "results": serializer.data,
        })
   
   
class WasteAnalytics(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Transaction.objects.filter(seller=user)
        ...