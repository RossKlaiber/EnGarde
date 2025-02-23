from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from profiles.models import AthleteProfile


User = get_user_model()

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def get_success_url(self):
        # This method is called after successful login.
        user = self.request.user
        if user.user_type == 'ATHLETE':
            return reverse_lazy('athlete_home')
        elif user.user_type == 'RECRUITER':
            return reverse_lazy('recruiter_home')
        return reverse_lazy('login')

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from accounts.models import CustomUser
from profiles.models import AthleteProfile

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from accounts.models import CustomUser
from profiles.models import AthleteProfile
from profiles.views import extract_fencer_data  # ✅ Import the scraper function

def signup(request):
    """Handles user signup, creating either an Athlete or Recruiter with optional FIE scraping."""
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        user_type = request.POST.get("user_type")  # Should be 'athlete' or 'recruiter'
        fie_link = request.POST.get("fie_link")  # FIE Link (only if athlete)

        if not username or not password or user_type not in ['athlete', 'recruiter']:
            return render(request, 'accounts/signup.html', {'error': 'Invalid input'})

        # ✅ Create and save the user
        user = CustomUser.objects.create_user(username=username, password=password, email=email, user_type=user_type)
        user.save()

        # ✅ If the user is an athlete, scrape their data and create an AthleteProfile
        if user.user_type == 'athlete':
            athlete_profile = AthleteProfile.objects.create(user=user, FIE_page=fie_link)

            if fie_link:  # ✅ If FIE Link is provided, attempt to scrape data
                scraped_data = extract_fencer_data(fie_link)
                
                # ✅ Populate athlete profile with scraped data
                athlete_profile.FIE_id = scraped_data.get('FIE_id')
                athlete_profile.name = scraped_data.get('name')
                athlete_profile.flag = scraped_data.get('flag')
                athlete_profile.handedness = scraped_data.get('handedness')
                athlete_profile.age = scraped_data.get('age')
                athlete_profile.weapon = scraped_data.get('weapon')
                athlete_profile.rank = scraped_data.get('rank')
                athlete_profile.residence = scraped_data.get('residence')
                athlete_profile.points = scraped_data.get('points')
                athlete_profile.image = scraped_data.get('image')
                athlete_profile.save()

        # ✅ Log in the new user
        login(request, user)

        # ✅ Redirect to the appropriate home page
        return redirect('athlete_home' if user.user_type == 'athlete' else 'recruiter_home')

    return render(request, 'accounts/signup.html')



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from profiles.models import AthleteProfile


@login_required
def athlete_home(request):
    """
    View for the athlete home page. Fetches the logged-in user's athlete profile 
    and ensures that competition data is passed correctly.
    """
    profile = AthleteProfile.objects.filter(user=request.user).first()

    if profile:
        competitions_data = profile.competitions_data if profile.competitions_data else []
        yearly_summary_data = profile.yearly_summary_data if profile.yearly_summary_data else []
    else:
        competitions_data = []
        yearly_summary_data = []

    return render(request, 'athlete/athlete_home.html', {
        'profile': profile,
        'competitions_data': competitions_data,
        'yearly_summary_data': yearly_summary_data
    })



def recruiter_home(request):
    return render(request, 'recruiter/recruiter_home.html')
