from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task
from .forms import TaskForm
from .ai_utils import prioritize_task, suggest_related_tasks
import json
from django.db.models import Count
from django.utils import timezone

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    category = request.GET.get('category')
    priority = request.GET.get('priority')
    status = request.GET.get('status')
    if category:
        tasks = tasks.filter(category=category)
    if priority:
        tasks = tasks.filter(priority=priority)
    if status:
        tasks = tasks.filter(status=status)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            # Set AI-driven priority
            task.priority = prioritize_task(task)
            task.save()
            # Suggest related tasks
            suggestions = suggest_related_tasks(task.description)
            if suggestions:
                for suggestion in suggestions:
                    Task.objects.create(
                        user=request.user,
                        title=suggestion,
                        description='Suggested task',
                        due_date=task.due_date,
                        priority='LOW',
                        category=task.category,
                        status='PENDING'
                    )
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.status = 'COMPLETED'
    task.save()
    return redirect('task_list')

@login_required
def analytics(request):
    tasks = Task.objects.filter(user=request.user)

    # Priority data as an array
    priority_data = [
        tasks.filter(priority='LOW').count(),
        tasks.filter(priority='MEDIUM').count(),
        tasks.filter(priority='HIGH').count()
    ]

    # Category data as an array
    category_data = [
        tasks.filter(category='WORK').count(),
        tasks.filter(category='PERSONAL').count(),
        tasks.filter(category='OTHER').count()
    ]

    # Status data as an array
    status_data = [
        tasks.filter(status='PENDING').count(),
        tasks.filter(status='COMPLETED').count()
    ]

    # Average completion time for completed tasks
    completion_times = [
        (t.updated_at - t.created_at).total_seconds() / 3600
        for t in tasks.filter(status='COMPLETED')
    ]
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

    return render(request, 'tasks/analytics.html', {
        'priority_data': json.dumps(priority_data),
        'category_data': json.dumps(category_data),
        'status_data': json.dumps(status_data),
        'avg_completion_time': avg_completion_time,
    })

