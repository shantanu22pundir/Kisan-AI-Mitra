from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SubmissionForm, CustomUserCreationForm
from .models import UserSubmission
from .utils import process_image, analyze_with_gemini
import markdown2
import re
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect


# ---------- Home Page ----------
def home(request):
    return render(request, "base.html")


# ---------- Dashboard (only logged-in users) ----------
@login_required(login_url='login')
def dashboard(request):
    submissions = UserSubmission.objects.order_by('-id')[:20]
    results = []
    
    for sub in submissions:
        try:
            width, height = process_image(sub.image.path) if sub.image else (None, None)
        except Exception:
            width, height = None, None

        try:
            ai_text = analyze_with_gemini(
                sub.image.path if sub.image else None
            )

            # Fix tables so markdown2 will render them
            ai_text = re.sub(
                r"(\|[^\n]+\|)\n(\|[^\n]+\|)",
                lambda m: f"{m.group(1)}\n" + "|---" * (m.group(1).count("|") - 1) + "|\n" + m.group(2),
                ai_text
            )

            # Convert Markdown to HTML (tables + code blocks supported)
            ai_output = markdown2.markdown(ai_text, extras=["tables", "fenced-code-blocks"])
            
        except Exception as e:
            ai_output = f"<p><strong>AI error:</strong> {e}</p>"

        results.append({
            "name": sub.name,
            "image_url": sub.image.url if sub.image else None,
            "image_size": f"{width}x{height}" if width else None,
            "ai_output": ai_output
        })
        
    return render(request, "dashboard.html", {"results": results})


# ---------- Upload Form (only logged-in users) ----------
@login_required(login_url='login')
def upload_form(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Image uploaded successfully!")
            return redirect('dashboard')
    else:
        form = SubmissionForm()
    return render(request, 'upload_form.html', {'form': form})


# ---------- User Registration ----------
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after registration
            messages.success(request, "Registration successful! Welcome aboard 🚀")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


# ---------- User Login ----------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # 👈 logs the user in
            messages.success(request, f"Welcome back, {user.username} 👋")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')


# ---------- User Logout ----------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
