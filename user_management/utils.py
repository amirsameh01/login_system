from django.core.cache import cache


def increase_failed_attempts_count(identifier, identifier_type):
    """
    increase the number of failed attempts cache records. 

    args:
        identifier: IP address or phone number
        identifier_type: type of identifier ('ip_address' or 'phone_number')

    returns:
        number of failed attempts
    """
    cache_key = f'{identifier_type}_failed_attempts_{identifier}'
    failed_count = cache.get(cache_key, 0) + 1 # the fresh one

    cache.set(cache_key, failed_count, timeout=24*60*60)
    if failed_count >= 3:
        apply_block(identifier, identifier_type)
    
    return failed_count

def apply_block(identifier, identifier_type):
    """
    Block an IP or phone number for 1 hour after 3 failed attempts.

    args:
        identifier: IP address or phone number
        identifier_type: type of identifier ('ip_address' or 'phone_number')
    """
    blocked_key = f"blocked_{identifier_type}_{identifier}"

    cache.set(blocked_key, True, timeout=60*60)
    cache.delete(f"{identifier_type}_failed_attempts_{identifier}")
    return

def reset_failed_attempts_count(identifier, identifier_type):
    """
    Reset failed attempt counter after successful authentication
    
    args:
        identifier: IP address or phone number
        identifier_type: type of identifier ('ip_address' or 'phone_number')
    """
    cache_key = f"{identifier_type}_failed_attempts_{identifier}"
    cache.delete(cache_key)

    return


def validate_phone_number(phone_number):
    """
    Validate phone number format.
    
    1.must be either 10 or 11 digits
    2. if 10 digits, automatically add leading '0'
    3. if 11 digits, must start with '0'
    
    returns:
    - validated and normalized 11-digit phone number
    - none if invalid
    """

    if not phone_number:
        return None
    phone_number = str(phone_number).replace(' ', '')
    
    if not phone_number.isdigit():
        return None
    
    if len(phone_number) == 10:
        return f'0{phone_number}'
    elif len(phone_number) == 11:
        if not phone_number.startswith('0'):
            return None
        return phone_number
    
    return None