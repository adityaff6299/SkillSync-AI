from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    # Links the resume to a specific user (Login/Register)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # This stores the actual PDF file
    resume_file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # These fields will be filled by our AI later
    extracted_text = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    match_score = models.FloatField(default=0.0)

    def __str__(self):
        return f"Resume of {self.user.username}"