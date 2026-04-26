import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils import get_pdf_text, extract_skills
from .services import fetch_custom_opportunities

def home(request):
    return render(request, 'analyzer/home.html')

def analyze(request):
    if request.method == 'POST':
        # --- WIRETAP: SEE WHAT THE HTML IS ACTUALLY SENDING ---
        print("\n" + "="*40)
        print("🚨 DEBUG: INCOMING DATA FROM BROWSER 🚨")
        print(f"User Choice: {request.POST.get('user_choice')}")
        print(f"Manual Skills typed: '{request.POST.get('manual_skills')}'")
        print(f"Files attached: {request.FILES}")
        print("="*40 + "\n")
        # -----------------------------------------------------

        user_choice = request.POST.get('user_choice', 'internship').strip()
        state = request.POST.get('state', '').strip()
        district = request.POST.get('location', '').strip() 
        want_stipend = request.POST.get('want_stipend', 'no').strip()
        branch = request.POST.get('branch', 'Engineering').strip()

        full_loc = "Remote" if state.lower() == "remote" else f"{district}, {state}" if district else state or "India"

        skills_list = []
        fallback = request.POST.get('fallback_domain', '').strip()
        manual = request.POST.get('manual_skills', '').strip()

        # Route Logic
        if fallback:
            skills_list = [fallback.capitalize()]
        elif 'resume' in request.FILES and request.FILES['resume'].name:
            file = request.FILES['resume']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            path = fs.path(filename)
            try:
                skills_list = extract_skills(get_pdf_text(path))
            finally:
                if os.path.exists(path):
                    os.remove(path)
        elif manual:
            skills_list = extract_skills(manual)
            if not skills_list:
                skills_list = [manual.replace(',', ' ').split()[0].capitalize()]

        # Gatekeeper
        if not skills_list:
            print("🚨 ERROR: Skills list is empty! Redirecting to ask_domain.")
            return render(request, 'analyzer/ask_domain.html', {
                'user_choice': user_choice, 'state': state,
                'location': district, 'want_stipend': want_stipend, 'branch': branch
            })

        print(f"✅ SUCCESS: Searching for skills: {skills_list}")
        
        # Search
        stipend_min = 1 if want_stipend == 'yes' else 0
        jobs = fetch_custom_opportunities(user_choice, {'location': full_loc, 'stipend_min': stipend_min}, skills_list)

        return render(request, 'analyzer/success.html', {
            'jobs': jobs, 'skills': skills_list, 'location': full_loc,
            'user_choice': user_choice.capitalize(), 'branch': branch
        })

    return render(request, 'analyzer/home.html')