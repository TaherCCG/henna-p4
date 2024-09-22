from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# @login_required
def profile(request):
    """ Display user profile """
    template = 'profiles/profile.html'
    profile = request.user.userprofile
    context = {'profile': profile}
    
    return render(request, template, context)
