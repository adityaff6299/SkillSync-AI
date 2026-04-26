import requests

# Your Active Adzuna Credentials
APP_ID = "32dcbc07" 
APP_KEY = "9e7e7ee07e57d7eb52a8714a2336a8cf"

def fetch_custom_opportunities(user_choice, filters, user_skills):
    all_results = []
    # Ensure user_skills is a list and get the first element as a string
    main_skill = str(user_skills[0]) if (user_skills and len(user_skills) > 0) else "Software"

    # --- CATEGORY 1: NEWS SCOUT (Govt Notifications) ---
    if str(user_choice).lower() == 'internship':
        gov_news = scout_govt_news(main_skill)
        all_results.extend(gov_news)

    # --- CATEGORY 2: PREMIUM PRIVATE (Big Tech) ---
    premium_query = f"{main_skill} {user_choice} (Google OR Microsoft OR Amazon OR Adobe)"
    premium_jobs = fetch_adzuna_data(premium_query, filters, user_skills, boost=20)
    all_results.extend(premium_jobs)

    # --- CATEGORY 3: GENERAL MARKET ---
    general_query = f"{main_skill} {user_choice}"
    general_jobs = fetch_adzuna_data(general_query, filters, user_skills)
    all_results.extend(general_jobs)

    # --- CATEGORY 4: PERMANENT PORTAL FALLBACKS ---
    if str(user_choice).lower() == 'internship':
        all_results.append({
            'title': 'AICTE National Internship Portal',
            'company': 'Ministry of Education',
            'location': 'All India',
            'apply_url': 'https://internship.aicte-india.org/',
            'score': 100,
            'is_gov': True,
            'description': 'Centralized gateway for government and corporate internships.'
        })

    # Ranking: Govt first, then by score
    return sorted(all_results, key=lambda x: (not x.get('is_gov', False), -x['score']))[:15]

def scout_govt_news(skill):
    news_query = f"(ISRO OR DRDO OR AICTE OR BEL) (Notification OR Advertisement OR Notice OR 2026) {skill}"
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        'app_id': APP_ID, 'app_key': APP_KEY,
        'results_per_page': 5, 'what': news_query, 'content-type': 'application/json'
    }
    try:
        res = requests.get(url, params=params, timeout=10).json()
        news_results = []
        for item in res.get('results', []):
            news_results.append({
                'title': item.get('title').replace('<strong>', '').replace('</strong>', ''),
                'company': item.get('company', {}).get('display_name', 'Government Agency'),
                'location': 'Official Notification',
                'apply_url': item.get('redirect_url'),
                'score': 95, 'is_gov': True,
                'description': "Recent notification found via career news aggregation."
            })
        return news_results
    except: return []

def fetch_adzuna_data(query, filters, user_skills, boost=0):
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    
    # SAFETY FIX: Handle location if it is a dict or a string
    raw_loc = filters.get('location', '')
    if isinstance(raw_loc, dict):
        loc = str(raw_loc.get('display_name', '')).lower()
    else:
        loc = str(raw_loc).lower()

    params = {
        'app_id': APP_ID, 'app_key': APP_KEY,
        'results_per_page': 10, 'what': query, 'content-type': 'application/json'
    }
    
    if "remote" not in loc and loc.strip():
        params['where'] = loc.split(',')[0].strip()

    try:
        res = requests.get(url, params=params, timeout=10).json()
        processed = []
        for item in res.get('results', []):
            title = item.get('title', '').replace('<strong>', '').replace('</strong>', '')
            score = 70 + boost
            if user_skills and str(user_skills[0]).lower() in title.lower():
                score += 15
            processed.append({
                'title': title,
                'company': item.get('company', {}).get('display_name', 'Top Recruiter'),
                'location': item.get('location', {}).get('display_name', 'India'),
                'apply_url': item.get('redirect_url'),
                'score': min(score, 100),
                'is_gov': False,
                'description': item.get('description', '')[:100] + "..."
            })
        return processed
    except: return []