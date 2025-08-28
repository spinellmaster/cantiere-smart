from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils import timezone

from .models import (
    Project, WorkItem,
    TimeSession, TimeSessionAllocation,
    CostDocument,
    Vehicle, VehicleSession,
    UserFolder, UserFile
)
from .forms import (
    WorkItemForm, TimeStartForm, AllocationForm,
    VehicleCheckoutForm, VehicleCheckinForm,
    CostForm
)

def redirect_home(request):
    return redirect('dashboard')

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        user_or_email = request.POST.get('email','').strip()
        password = request.POST.get('password','').strip()
        username = user_or_email
        if '@' in user_or_email:
            User = get_user_model()
            try:
                u = User.objects.get(email__iexact=user_or_email)
                username = u.get_username()
            except User.DoesNotExist:
                pass
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Credenziali non valide')
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    kpi_projects = Project.objects.count()
    last_7 = timezone.now() - timezone.timedelta(days=7)
    total_minutes = 0
    for ts in TimeSession.objects.filter(user=request.user, completed=True, end_time__gte=last_7):
        total_minutes += ts.duration_minutes
    kpi_hours_week = round(total_minutes / 60, 1)
    recent_projects = Project.objects.all()[:5]
    bars = [4,6,3,7,5,8,6]
    return render(request, 'core/dashboard.html', {
        'kpi_projects': kpi_projects,
        'kpi_hours_week': kpi_hours_week,
        'recent_projects': recent_projects,
        'bars': bars
    })

@login_required
def projects_list(request):
    items = Project.objects.all()
    return render(request, 'core/projects_list.html', {'items': items})

# ===== Lavorazioni =====
def _build_tree(items):
    by_parent = {}
    for it in items:
        by_parent.setdefault(it.parent_id, []).append(it)
    for k in by_parent:
        by_parent[k].sort(key=lambda x: (x.sort_order, x.id))
    def walk(pid):
        nodes = []
        for n in by_parent.get(pid, []):
            nodes.append({'node': n, 'children': walk(n.id)})
        return nodes
    return walk(None)

@login_required
def project_detail(request, pk):
    p = get_object_or_404(Project, pk=pk)
    items = list(WorkItem.objects.filter(project=p).select_related('parent'))
    tree = _build_tree(items)
    return render(request, 'core/project_detail.html', {'p': p, 'tree': tree})

@login_required
def workitem_create(request, project_id):
    p = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = WorkItemForm(request.POST)
        form.fields['parent'].queryset = WorkItem.objects.filter(project=p)
        if form.is_valid():
            wi = form.save(commit=False)
            wi.project = p
            wi.save()
            messages.success(request, "Lavorazione creata.")
            return redirect('project_detail', pk=p.id)
    else:
        form = WorkItemForm()
        form.fields['parent'].queryset = WorkItem.objects.filter(project=p)
    return render(request, 'core/work_item_form.html', {'form': form, 'project': p, 'title': 'Nuova lavorazione'})

@login_required
def workitem_edit(request, pk):
    wi = get_object_or_404(WorkItem, pk=pk)
    p = wi.project
    if request.method == 'POST':
        form = WorkItemForm(request.POST, instance=wi)
        form.fields['parent'].queryset = WorkItem.objects.filter(project=p).exclude(pk=wi.pk)
        if form.is_valid():
            form.save()
            messages.success(request, "Lavorazione aggiornata.")
            return redirect('project_detail', pk=p.id)
    else:
        form = WorkItemForm(instance=wi)
        form.fields['parent'].queryset = WorkItem.objects.filter(project=p).exclude(pk=wi.pk)
    return render(request, 'core/work_item_form.html', {'form': form, 'project': p, 'title': 'Modifica lavorazione'})

@login_required
def workitem_delete(request, pk):
    wi = get_object_or_404(WorkItem, pk=pk)
    pid = wi.project_id
    if wi.children.exists():
        messages.error(request, "Impossibile eliminare: esistono sotto-lavorazioni. Elimina prima i figli.")
        return redirect('project_detail', pk=pid)
    wi.delete()
    messages.success(request, "Lavorazione eliminata.")
    return redirect('project_detail', pk=pid)

@login_required
def workitem_set_status(request, pk, new_status):
    wi = get_object_or_404(WorkItem, pk=pk)
    valid = dict(WorkItem.STATUS_CHOICES).keys()
    if new_status not in valid:
        messages.error(request, "Stato non valido.")
    else:
        wi.status = new_status
        wi.save(update_fields=['status','updated_at'])
        messages.success(request, "Stato aggiornato.")
    return redirect('project_detail', pk=wi.project_id)

@login_required
def workitem_set_progress(request, pk, value):
    wi = get_object_or_404(WorkItem, pk=pk)
    v = max(0, min(int(value), 100))
    wi.progress = v
    wi.save(update_fields=['progress','updated_at'])
    messages.success(request, f"Progress impostato a {v}%.")
    return redirect('project_detail', pk=wi.project_id)

# ===== Timbrature =====
@login_required
def times_list(request):
    my_sessions = TimeSession.objects.filter(user=request.user).select_related('project')
    active = my_sessions.filter(end_time__isnull=True, completed=False).first()
    return render(request, 'core/times_list.html', {'items': my_sessions, 'active': active})

@login_required
def times_active(request):
    active = TimeSession.objects.filter(user=request.user, end_time__isnull=True, completed=False).select_related('project').first()
    return render(request, 'core/times_active.html', {'active': active})

@login_required
def times_start(request):
    already = TimeSession.objects.filter(user=request.user, end_time__isnull=True, completed=False).exists()
    if already:
        messages.error(request, "Hai già una timbratura attiva. Chiudila prima di avviarne un'altra.")
        return redirect('times_active')
    if request.method == 'POST':
        form = TimeStartForm(request.POST)
        if form.is_valid():
            p = form.cleaned_data['project']
            note = form.cleaned_data['note']
            ts = TimeSession.objects.create(project=p, user=request.user, note=note, hourly_rate_eur_snapshot=0)
            messages.success(request, "Timbratura avviata.")
            return redirect('times_detail', pk=ts.id)
    else:
        form = TimeStartForm()
    return render(request, 'core/times_start.html', {'form': form})

@login_required
def times_detail(request, pk):
    ts = get_object_or_404(TimeSession, pk=pk, user=request.user)
    wi_qs = WorkItem.objects.filter(project=ts.project)
    return render(request, 'core/times_detail.html', {'ts': ts, 'wi_qs': wi_qs})

@login_required
def times_stop(request, pk):
    ts = get_object_or_404(TimeSession, pk=pk, user=request.user)
    if not ts.end_time:
        ts.end_time = timezone.now()
        ts.completed = True
        ts.save(update_fields=['end_time','completed','updated_at'])
        messages.success(request, "Timbratura chiusa.")
    else:
        messages.info(request, "La timbratura è già chiusa.")
    return redirect('times_detail', pk=ts.id)

@login_required
def times_alloc_add(request, pk):
    ts = get_object_or_404(TimeSession, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AllocationForm(request.POST)
        form.fields['work_item'].queryset = WorkItem.objects.filter(project=ts.project)
        if form.is_valid():
            alloc = form.save(commit=False)
            alloc.time_session = ts
            if alloc.work_item.project_id != ts.project_id:
                messages.error(request, "La lavorazione selezionata non appartiene al progetto della timbratura.")
            else:
                alloc.save()
                messages.success(request, "Allocazione aggiunta.")
                return redirect('times_detail', pk=ts.id)
    else:
        form = AllocationForm()
        form.fields['work_item'].queryset = WorkItem.objects.filter(project=ts.project)
    return render(request, 'core/times_alloc_form.html', {'form': form, 'ts': ts})

@login_required
def times_alloc_delete(request, pk):
    alloc = get_object_or_404(TimeSessionAllocation, pk=pk)
    if alloc.time_session.user_id != request.user.id:
        messages.error(request, "Operazione non consentita.")
        return redirect('times_list')
    tsid = alloc.time_session_id
    alloc.delete()
    messages.success(request, "Allocazione eliminata.")
    return redirect('times_detail', pk=tsid)

# ===== Spese =====
@login_required
def costs_list(request):
    state = request.GET.get('state')
    qs = CostDocument.objects.select_related('project','user','work_item')
    if state in {'pending','approved','rejected'}:
        qs = qs.filter(status=state)
    return render(request, 'core/costs_list.html', {'items': qs, 'state': state})

@login_required
def costs_new(request):
    if request.method == 'POST':
        form = CostForm(request.POST)
        if form.is_valid():
            cost = form.save(commit=False)
            cost.user = request.user
            if cost.work_item and cost.work_item.project_id != cost.project_id:
                messages.error(request, "La lavorazione selezionata non appartiene al progetto scelto.")
            else:
                cost.save()
                messages.success(request, "Spesa inserita.")
                return redirect('costs_detail', pk=cost.id)
    else:
        form = CostForm()
    return render(request, 'core/costs_form.html', {'form': form, 'title': 'Nuova spesa'})

@login_required
def costs_detail(request, pk):
    doc = get_object_or_404(CostDocument.objects.select_related('project','user','work_item','approved_by'), pk=pk)
    return render(request, 'core/costs_detail.html', {'doc': doc})

def _is_staff(user): return user.is_staff or user.is_superuser

@user_passes_test(_is_staff)
@login_required
def costs_approve(request, pk):
    doc = get_object_or_404(CostDocument, pk=pk)
    if doc.status != 'approved':
        doc.status = 'approved'
        doc.approved_by = request.user
        doc.approved_at = timezone.now()
        doc.save(update_fields=['status','approved_by','approved_at'])
        messages.success(request, "Spesa approvata.")
    return redirect('costs_detail', pk=pk)

@user_passes_test(_is_staff)
@login_required
def costs_reject(request, pk):
    doc = get_object_or_404(CostDocument, pk=pk)
    if doc.status != 'rejected':
        doc.status = 'rejected'
        doc.approved_by = request.user
        doc.approved_at = timezone.now()
        doc.save(update_fields=['status','approved_by','approved_at'])
        messages.success(request, "Spesa respinta.")
    return redirect('costs_detail', pk=pk)

@login_required
def costs_delete(request, pk):
    doc = get_object_or_404(CostDocument, pk=pk)
    if (not request.user.is_staff) and (doc.user_id != request.user.id):
        messages.error(request, "Operazione non consentita.")
        return redirect('costs_list')
    doc.delete()
    messages.success(request, "Spesa eliminata.")
    return redirect('costs_list')

# ===== Flotta =====
@login_required
def fleet_list(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'core/fleet_list.html', {'items': vehicles})

@login_required
def fleet_detail(request, pk):
    v = get_object_or_404(Vehicle, pk=pk)
    active = VehicleSession.objects.filter(vehicle=v, end_time__isnull=True).select_related('user','project').first()
    history = VehicleSession.objects.filter(vehicle=v).select_related('user','project')
    return render(request, 'core/fleet_detail.html', {'v': v, 'active': active, 'history': history})

@login_required
def fleet_checkout(request, vehicle_id):
    v = get_object_or_404(Vehicle, pk=vehicle_id)
    if VehicleSession.objects.filter(vehicle=v, end_time__isnull=True).exists():
        messages.error(request, "Il mezzo è già in uso.")
        return redirect('fleet_detail', pk=v.id)
    if VehicleSession.objects.filter(user=request.user, end_time__isnull=True).exists():
        messages.error(request, "Hai già un mezzo in uso. Riconsegnalo prima di prenderne un altro.")
        return redirect('fleet_list')
    if request.method == 'POST':
        form = VehicleCheckoutForm(request.POST)
        if form.is_valid():
            vs = VehicleSession.objects.create(
                vehicle=v, user=request.user,
                project=form.cleaned_data['project'],
                start_odometer_km=form.cleaned_data['start_odometer_km'],
                start_fuel_percent=form.cleaned_data['start_fuel_percent'],
                notes_out=form.cleaned_data['notes_out'],
            )
            v.status = 'in_use'
            v.odometer_km = vs.start_odometer_km
            v.fuel_level_percent = vs.start_fuel_percent
            v.save(update_fields=['status','odometer_km','fuel_level_percent'])
            messages.success(request, "Ritiro effettuato.")
            return redirect('fleet_detail', pk=v.id)
    else:
        form = VehicleCheckoutForm(initial={'start_odometer_km': v.odometer_km,'start_fuel_percent': v.fuel_level_percent})
    return render(request, 'core/fleet_checkout.html', {'v': v, 'form': form})

@login_required
def fleet_checkin(request, pk):
    vs = get_object_or_404(VehicleSession.objects.select_related('vehicle'), pk=pk, user=request.user)
    if vs.end_time:
        messages.info(request, "Questa sessione è già chiusa.")
        return redirect('fleet_detail', pk=vs.vehicle_id)
    if request.method == 'POST':
        form = VehicleCheckinForm(request.POST)
        if form.is_valid():
            end_km = form.cleaned_data['end_odometer_km']
            end_fuel = form.cleaned_data['end_fuel_percent']
            if end_km < vs.start_odometer_km:
                messages.error(request, "I km finali non possono essere inferiori a quelli iniziali.")
                return render(request, 'core/fleet_checkin.html', {'vs': vs, 'form': form})
            vs.end_time = timezone.now()
            vs.end_odometer_km = end_km
            vs.end_fuel_percent = end_fuel
            vs.notes_in = form.cleaned_data['notes_in']
            vs.damages_report = form.cleaned_data['damages_report']
            vs.photos_urls = form.cleaned_data['photos_urls']
            vs.save()
            v = vs.vehicle
            v.status = 'available'
            v.odometer_km = end_km
            v.fuel_level_percent = end_fuel
            v.save(update_fields=['status','odometer_km','fuel_level_percent'])
            messages.success(request, "Riconsegna effettuata.")
            return redirect('fleet_detail', pk=v.id)
    else:
        form = VehicleCheckinForm(initial={'end_odometer_km': vs.start_odometer_km,'end_fuel_percent': vs.start_fuel_percent})
    return render(request, 'core/fleet_checkin.html', {'vs': vs, 'form': form})

# ===== Documenti HR =====
@login_required
def docs_home(request):
    roots = UserFolder.objects.filter(owner=request.user, parent__isnull=True).order_by('name')
    return render(request, 'core/docs_home.html', {'roots': roots})

@login_required
def docs_folder(request, pk):
    folder = get_object_or_404(UserFolder, pk=pk, owner=request.user)
    subfolders = folder.children.all().order_by('name')
    files = folder.files.all().order_by('-id')
    return render(request, 'core/docs_folder.html', {'folder': folder, 'subfolders': subfolders, 'files': files})

@login_required
def docs_file(request, pk):
    uf = get_object_or_404(UserFile.objects.select_related('folder'), pk=pk, owner=request.user)
    if uf.read_at is None:
        uf.read_at = timezone.now()
        uf.save(update_fields=['read_at'])
    if request.method == 'POST' and uf.requires_ack and uf.ack_at is None:
        uf.ack_at = timezone.now()
        uf.save(update_fields=['ack_at'])
        messages.success(request, "Presa visione confermata.")
        return redirect('docs_file', pk=uf.id)
    return render(request, 'core/docs_file.html', {'f': uf})
