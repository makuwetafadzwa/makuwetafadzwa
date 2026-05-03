from .models import CompanyProfile


def company_profile(request):
    try:
        profile = CompanyProfile.get_solo()
    except Exception:
        profile = None
    return {"company": profile}
