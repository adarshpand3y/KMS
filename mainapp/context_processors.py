from KMS import settings

def branding_details(request):
    return {
        'brand_name_full': settings.BRAND_FULL_NAME,
        'brand_name_short': settings.BRAND_SHORT_NAME,
    }