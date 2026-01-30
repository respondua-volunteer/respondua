import os
import yaml
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def openapi_schema(request):
    """
    Custom view to serve our OpenAPI schema from YAML file
    """
    schema_path = os.path.join(settings.BASE_DIR, 'schema.yml')
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as file:
            schema_data = yaml.safe_load(file)
        return Response(schema_data)
    except FileNotFoundError:
        return JsonResponse({'error': 'Schema file not found'}, status=404)
    except yaml.YAMLError as e:
        return JsonResponse({'error': f'Invalid YAML: {str(e)}'}, status=400)