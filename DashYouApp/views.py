#views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render, get_object_or_404
from .models import Project, Pipeline
from .models import Admin3s
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import requests
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from jenkinsapi.jenkins import Jenkins


@csrf_exempt
@require_POST
def trigger_jenkins_build(request, pipeline_id):
    try:
        pipeline = Pipeline.objects.get(id=pipeline_id)
        jenkins_job_url = f'http://localhost:8080/job/{pipeline.name}/build'
        
        # Trigger the Jenkins job using a POST request
        response = requests.post(jenkins_job_url, auth=('your-jenkins-username', 'your-jenkins-api-token'))
        
        if response.status_code == 201:
            return JsonResponse({'status': 'success', 'message': 'Build triggered successfully!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to trigger build.'})
    except Pipeline.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Pipeline not found.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})



@login_required
def update_profile(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        role = request.POST.get('role')
        
        user = request.user
        user.email = email
        user.username = username
        user.role = role
        user.save()
        
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('developper')
    
    return render(request, 'developper.html')

from django.contrib.auth import authenticate

@login_required
def update_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')
        
        user = authenticate(username=request.user.username, password=current_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('developper')
        else:
            messages.error(request, 'Current password is incorrect.')
    
    return render(request, 'developper.html')



from django.contrib.auth import authenticate

@login_required
def update_passwordpip(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')
        
        user = authenticate(username=request.user.username, password=current_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('pipeline_page')
        else:
            messages.error(request, 'Current password is incorrect.')
    
    return render(request, 'pipeline_page.html')


@login_required
def update_profilepip(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        role = request.POST.get('role')
        
        user = request.user
        user.email = email
        user.username = username
        user.role = role
        user.save()
        
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('pipeline_page')
    
    return render(request, 'pipeline_page.html')

def authentication(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'signup':
            username = request.POST.get('signup_username')
            password = request.POST.get('signup_password')
            email = request.POST.get('signup_email')
            role = request.POST.get('signup_role')
            
            user = Admin3s.objects.create_user(username=username, email=email, password=password, role=role)
            login(request, user)
            return redirect('developper')  # Redirect after signup

        elif action == 'login':
            username = request.POST.get('login_username')
            password = request.POST.get('login_password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Redirect based on user role
                if user.role == 'developer':
                    return redirect('developper')
                elif user.role == 'devops':
                    return redirect('pipeline_page')
                else:
                    return HttpResponse('Unauthorized', status=401)  # Handle unauthorized roles if needed
            else:
                return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')

def list_users(request):
    users = Admin3s.objects.all()
    return render(request, 'list_users.html', {'users': users})


@login_required
def developper(request):
    if request.method == 'POST':
        if 'add_project' in request.POST:
            name = request.POST.get('name')
            description = request.POST.get('description')
            github_url = request.POST.get('github_url')
            languages = request.POST.get('languages')
            status = request.POST.get('status')

            Project.objects.create(
                name=name,
                description=description,
                github_url=github_url,
                languages=languages,
                status=status,
                user=request.user
            )
            return redirect('base')  # Redirection vers la page d'accueil

        elif 'update_project' in request.POST:
            project_id = request.POST.get('project_id')
            project = get_object_or_404(Project, id=project_id)
            project.name = request.POST.get('name')
            project.description = request.POST.get('description')
            project.github_url = request.POST.get('github_url')
            project.languages = request.POST.get('languages')
            project.status = request.POST.get('status')
            project.save()

            return redirect('base')  # Redirection vers la page d'accueil

        elif 'delete_project' in request.POST:
            project_id = request.POST.get('project_id')
            project = get_object_or_404(Project, id=project_id)
            if project.user == request.user or request.user.is_superuser:
                project.delete()

            return redirect('base')  # Redirection vers la page d'accueil

    projects = Project.objects.all()
    return render(request, 'developper.html', {'projects': projects})


# Jenkins configuration
JENKINS_URL = 'http://your-jenkins-url'  # Replace with your Jenkins URL
JENKINS_USER = 'your-username'           # Replace with your Jenkins username
JENKINS_TOKEN = 'your-api-token'         # Replace with your Jenkins API token

def get_jenkins_server():
    return Jenkins(JENKINS_URL, username=JENKINS_USER, password=JENKINS_TOKEN)

@csrf_exempt
def pipeline_page(request):
    if request.method == "POST":
        if 'name' in request.POST and 'jenkins_file' in request.POST:
            if 'update_pipeline' in request.POST:
                pipeline_id = request.POST.get('pipeline_id')
                name = request.POST.get('name')
                jenkins_file = request.POST.get('jenkins_file')

                if pipeline_id and name and jenkins_file:
                    try:
                        pipeline = Pipeline.objects.get(id=pipeline_id)
                        pipeline.name = name
                        pipeline.jenkins_file = jenkins_file
                        pipeline.save()
                        # Update Jenkins job if necessary
                        jenkins_server = get_jenkins_server()
                        jenkins_server.reconfig_job(name, jenkins_file)
                    except Pipeline.DoesNotExist:
                        return render(request, 'pipeline_page.html', {'error': 'Pipeline not found.'})
            else:
                # Ajouter un pipeline
                name = request.POST.get('name')
                jenkins_file = request.POST.get('jenkins_file')

                if name and jenkins_file:
                    Pipeline.objects.create(name=name, jenkins_file=jenkins_file)
                    # Add the pipeline to Jenkins
                    try:
                        jenkins_server = get_jenkins_server()
                        jenkins_server.create_job(name, jenkins_file)
                    except Exception as e:
                        return render(request, 'pipeline_page.html', {'error': f'Error adding pipeline to Jenkins: {e}'})
                else:
                    return render(request, 'pipeline_page.html', {'error': 'All fields are required.'})
        elif 'delete_pipeline' in request.POST:
            # Supprimer un pipeline
            pipeline_id = request.POST.get('pipeline_id')

            if pipeline_id:
                try:
                    pipeline = Pipeline.objects.get(id=pipeline_id)
                    pipeline.delete()
                    # Remove the pipeline from Jenkins
                    jenkins_server = get_jenkins_server()
                    jenkins_server.delete_job(pipeline.name)
                except Pipeline.DoesNotExist:
                    return render(request, 'pipeline_page.html', {'error': 'Pipeline not found.'})

        return redirect('pipeline_page')

    # GET request - Afficher la liste des pipelines
    pipelines = Pipeline.objects.all()
    projects = Project.objects.all()

    return render(request, 'pipeline_page.html', {'pipelines': pipelines, 'projects': projects})



#pipelineold
"""
@csrf_exempt
def pipeline_page(request):
    if request.method == "POST":
        if 'name' in request.POST and 'jenkins_file' in request.POST:
            # Identifier l'action à réaliser
            if 'update_pipeline' in request.POST:
                # Mettre à jour un pipeline
                pipeline_id = request.POST.get('pipeline_id')
                name = request.POST.get('name')
                jenkins_file = request.POST.get('jenkins_file')

                if pipeline_id and name and jenkins_file:
                    try:
                        pipeline = Pipeline.objects.get(id=pipeline_id)
                        pipeline.name = name
                        pipeline.jenkins_file = jenkins_file
                        pipeline.save()
                    except Pipeline.DoesNotExist:
                        return render(request, 'pipeline_page.html', {'error': 'Pipeline not found.'})
            else:
                # Ajouter un pipeline
                name = request.POST.get('name')
                jenkins_file = request.POST.get('jenkins_file')

                if name and jenkins_file:
                    Pipeline.objects.create(name=name, jenkins_file=jenkins_file)
                else:
                    return render(request, 'pipeline_page.html', {'error': 'All fields are required.'})
        elif 'delete_pipeline' in request.POST:
            # Supprimer un pipeline
            pipeline_id = request.POST.get('pipeline_id')

            if pipeline_id:
                try:
                    pipeline = Pipeline.objects.get(id=pipeline_id)
                    pipeline.delete()
                except Pipeline.DoesNotExist:
                    return render(request, 'pipeline_page.html', {'error': 'Pipeline not found.'})

        return redirect('pipeline_page')

    # GET request - Afficher la liste des pipelines
    pipelines = Pipeline.objects.all()
    projects = Project.objects.all()

    return render(request, 'pipeline_page.html', {'pipelines': pipelines, 'projects': projects})
    """