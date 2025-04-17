from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response

#NOTE: should i move this to utils? since it has been used both in views and here, or maybe rename this file to utils? discauss ai.
    # this way (renaming it to utils) we can move the cache helper functions to the new utils file as well.
def get_client_ip(request):
    """ helper function to fetch client ip. """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_block_status(view_func):
    """ params, return"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        ip_address = get_client_ip(request)
        
        ip_block_key = f"blocked_ip_address_{ip_address}"
        if cache.get(ip_block_key):
            return Response({
                'message': 'IP address has been temporarily blocked. Please try again later.',
                'state': 'IP_BLOCKED'
            }, status=403)
        
        if phone_number:
            phone_block_key = f"blocked_phone_number_{phone_number}"
            if cache.get(phone_block_key):
                return Response({
                    'message': 'This phone number has been temporarily blocked. Please try again later.',
                    'state': 'PHONE_BLOCKED'
                }, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper