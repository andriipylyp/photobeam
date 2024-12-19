import base64
import json
import time
import uuid
import zipfile
from datetime import datetime
from io import BytesIO
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
import qrcode
import stripe
from io import BytesIO
from PIL import Image

from .forms import RegistrationForm
from .models import Album, ApplicationSettings, UserProfile, UploadedImage

stripe.api_key = settings.STRIPE_SECRET_KEY
UPLOAD_LINK = "http://localhost:8000/upload/?album_id={0}"

def get_data(request):
    settings = ApplicationSettings.objects.first()
    name = "None"
    if request.user.is_authenticated:
        name = UserProfile.objects.get(user=request.user).user.username
    user_data = {
        "auth": request.user.is_authenticated,
        "name": name
    }
    return settings, user_data

def index(request):
    settings, user_data = get_data(request)
    return render(request, 'index.html', {'settings': settings, 'user_data': user_data})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile') 
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def take_picture(request):
    album_id = request.GET.get("album_id")
    album = get_object_or_404(Album, unique_id=album_id)
    current_datetime = now()
    
    if request.method == "GET":
        allowed = album.event_date_start <= current_datetime <= album.event_date_end
        return render(request, "take_picture.html", {"album_id": album_id, "allowed": allowed})
    elif request.method == "POST":
        image = request.FILES.get("image")
        if image:
            start_time = time.time()
            # Open the uploaded image
            img = Image.open(image)

            # Get the current width and height of the image
            original_width, original_height = img.size

            # Calculate new dimensions while preserving aspect ratio
            full_hd_width = 1920
            scaling_factor = full_hd_width / original_width

            # Apply scaling factor to maintain aspect ratio
            new_width = int(original_width * scaling_factor)
            new_height = int(original_height * scaling_factor)

            # Resize the image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create a unique filename for the image
            file_name = f"{album.unique_id}_{str(uuid.uuid4())}_{image.name}"
            file_path = os.path.join(settings.MEDIA_ROOT, "uploaded_images", file_name)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save the resized image
            img.save(file_path)
            end_time = time.time()
            # Save the reference to the UploadedImage model
            uploaded_image = UploadedImage.objects.create(album=album, image=f"uploaded_images/{file_name}", processing_speed=int((end_time-start_time) * 1000))
            uploaded_image.save()

            return render(request, "upload_success.html", {"redirect_url": UPLOAD_LINK.format(album.unique_id)})
        return HttpResponse("No image uploaded.", status=400)

    
@login_required
def profile(request):
    # Ensure UserProfile exists
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Generate QR codes for each album
    albums = user_profile.albums.all()
    album_data = []
    for album in albums:
        qr_url = UPLOAD_LINK.format(album.unique_id)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        image_count = album.images.count()

        album_data.append({
            "unique_id": album.unique_id,
            "name": album.name,
            "created_at": album.created_at,
            "event_date_start": album.event_date_start,
            "event_date_end": album.event_date_end,
            "qr_code": img_base64,
            "qr_url": qr_url,
            "image_count": image_count,
        })
    settings, user_data = get_data(request)
    return render(request, "profile.html", {"user_profile": user_profile, "albums": album_data, "settings": settings, "user_data": user_data})

def user_album(request):
    album_id = request.GET.get('album_id')
    album = get_object_or_404(Album, unique_id=album_id)
    images = album.images.all()  # Access related images
    if not request.user.is_authenticated or UserProfile.objects.get(user=request.user) != album.user_profile:
        admin = False
    else:
        admin = True
    settings, user_data = get_data(request)
    return render(request, "album.html", {"album": album, "images": images, "admin": admin, "settings": settings, "user_data": user_data})

@login_required
def delete_album(request, album_id):
    if request.method == "POST":
        # Get the album by its unique ID
        album = get_object_or_404(Album, unique_id=album_id)

        # Ensure the user owns the album
        if album.user_profile.user != request.user:
            return HttpResponseForbidden("You do not have permission to delete this album.")

        # Delete the album and all associated images
        album.delete()

        # Redirect back to the profile page
        return redirect("profile")
    else:
        return HttpResponseForbidden("Invalid request method.")

@login_required
def delete_image(request, image_id):
    if request.method == "POST":
        # Get the image by its ID
        image = get_object_or_404(UploadedImage, id=image_id)

        # Ensure the user owns the album the image belongs to
        if image.album.user_profile.user != request.user:
            return HttpResponseForbidden("You do not have permission to delete this image.")

        # Delete the image file from the file system
        if image.image and os.path.isfile(image.image.path):
            os.remove(image.image.path)

        # Delete the image record from the database
        image.delete()

        # Redirect back to the album page
        return redirect(f"/album/?album_id={image.album.unique_id}")
    else:
        return HttpResponseForbidden("Invalid request method.")
    
def about(request):
    settings, user_data = get_data(request)
    return render(request, "about.html", {"settings": settings, "user_data": user_data})

def contact(request):
    settings, user_data = get_data(request)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Process the form data (e.g., send an email, save to database, etc.)
        print(f"Name: {name}, Email: {email}, Message: {message}")
        
        return render(request, "thanks_contact.html", {"settings": settings, "user_data": user_data})

    elif request.method == 'GET':  
        return render(request, "contact.html", {"settings": settings, "user_data": user_data})

def services(request):
    settings, user_data = get_data(request)
    return render(request, "services.html", {"settings": settings, "user_data": user_data})

def faq(request):
    settings, user_data = get_data(request)
    return render(request, "faq.html", {"settings": settings, "user_data": user_data})

@login_required
def create_checkout_session(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        album_name = data.get("album_name", "").strip()
        album_date_start = data.get("album_date_start", "").strip()
        album_date_end = data.get("album_date_end", "").strip()

        if not album_name:
            return JsonResponse({"error": "Album name is required"}, status=400)
        if not album_date_start:
            return JsonResponse({"error": "Album album date start is required"}, status=400)
        if not album_date_start:
            return JsonResponse({"error": "Album album date end is required"}, status=400)
        # Create a Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": settings.STRIPE_PRICE_ID,
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=f"{request.scheme}://{request.get_host()}/create-album-success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.scheme}://{request.get_host()}/profile",
        )

        # Save session data for validation on success
        request.session["album_name"] = album_name
        request.session["album_date_start"] = album_date_start
        request.session["album_date_end"] = album_date_end
        request.session["checkout_session_id"] = checkout_session.id

        return JsonResponse({"checkout_url": checkout_session.url})
    except stripe.error.StripeError as e:
        return JsonResponse({"error": f"Stripe error: {e.user_message}"}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON input"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)


        
@login_required
def create_album_success(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return redirect("profile")

    try:
        # Retrieve session data
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        if checkout_session.payment_status != "paid":
            return HttpResponse("Payment not completed. Album creation aborted.", status=400)

        # Get album name from session
        album_name = request.session.pop("album_name", "Unnamed Album")
        album_date_start = request.session.pop("album_date_start", None)
        album_date_end = request.session.pop("album_date_end", None)
        if not album_date_start:
            return HttpResponse("Album start date missing. Album creation aborted.", status=400)
        if not album_date_end:
            return HttpResponse("Album end date missing. Album creation aborted.", status=400)
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

        # Create the album
        Album.objects.create(user_profile=user_profile, name=album_name, event_date_start=album_date_start, event_date_end=album_date_end)

        # Clean up session data
        request.session.pop("checkout_session_id", None)

        return redirect("profile")
    except stripe.error.StripeError as e:
        return HttpResponse(f"Error verifying payment: {e.user_message}", status=400)
    except KeyError:
        return redirect("profile")
    except Exception as e:
        return HttpResponse(f"Unexpected error: {str(e)}", status=500)
    
@login_required
def download_album(request, album_id):
    # Ensure the album exists and belongs to the logged-in user
    album = get_object_or_404(Album, unique_id=album_id, user_profile__user=request.user)
    images = album.images.all()  # Retrieve all images in the album

    # Create a ZIP file in memory
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zf:
        for image in images:
            # Add each image to the ZIP file
            image_path = image.image.path  # File system path of the image
            image_name = image.image.name.split('/')[-1]  # Extract the filename
            zf.write(image_path, image_name)

    buffer.seek(0)

    # Return the ZIP file as a response
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{album.name}.zip"'
    return response

def usage_policy(request):
    settings, user_data = get_data(request)
    return render(request, "usage_policy.html", {"settings": settings, "user_data": user_data})