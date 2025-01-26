import os
import uuid

import requests
from allauth.account.signals import user_signed_up

from .models import Profile
from django.dispatch import receiver
from django.core.files.base import ContentFile


@receiver(user_signed_up)
def populate_user_profile(request, user, **kwargs):
    social_account = kwargs.get('sociallogin').account
    profile = Profile.objects.create(user=user)

    # Get image address from Google
    avatar_url = social_account.extra_data.get('picture')
    if avatar_url:
        try:
            # Download image
            response = requests.get(avatar_url)
            response.raise_for_status()  # Check the success of the request

            # Create unique name for avatar
            ext = os.path.splitext(avatar_url)[1]  # Get file extension
            avatar_name = f"{user.email}_avatar_{uuid.uuid4()}{ext}"  # Use UUID for unique name

            # Save image file
            profile.avatar.save(avatar_name, ContentFile(response.content), save=False)
        except Exception as e:
            print(f"Downloading image error: {e}")

    profile.first_name = social_account.extra_data.get('given_name', '')
    profile.last_name = social_account.extra_data.get('family_name', '')
    profile.save()
