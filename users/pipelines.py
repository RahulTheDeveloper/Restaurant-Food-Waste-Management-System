# pipelines.py

def save_client_details(backend, user, response, *args, **kwargs):
    """
    Save additional client details like phone_number, email, and image.
    """
    if backend.name == 'google-oauth2':  # Add checks for other backends if needed
        user.email = response.get('email', user.email)
        user.phone_number = response.get('phone_number', user.phone_number)  # Assuming phone_number is in the response
        user.name = response.get('name', user.name)

        # Save profile image if provided
        picture_url = response.get('picture')
        if picture_url:
            from urllib.request import urlopen
            from django.core.files.base import ContentFile

            avatar_response = urlopen(picture_url)
            user.image.save(f"{user.id}_avatar.jpg", ContentFile(avatar_response.read()), save=True)

        user.save()
