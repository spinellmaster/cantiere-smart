from django.db import models
from django.utils import timezone
from django.conf import settings

# ===== PROGETTI =====
class Project(models.Model):
    STATUS_CHOICES = [('active','Attivo'),('paused','Pausa'),('closed','Chiuso')]
    name = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    budget_eur = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cover_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-id']
    def __str__(self): return self.name

# ===== LAVORAZIONI =====
class WorkItem(models.Model):
    STATUS_CHOICES = [('open','Aperta'),('in_progress','In corso'),('paused','In pausa'),('done','Completata')]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='work_items')
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='open')
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['sort_order','id']
        indexes = [models.Index(fields=['project']), models.Index(fields=['parent'])]
    def __str__(self): return f"[{self.project_id}] {self.name}"

# ===== TIMBRATURE =====
class TimeSession(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='time_sessions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='time_sessions')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)
    hourly_rate_eur_snapshot = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-id']
        indexes = [models.Index(fields=['user']), models.Index(fields=['project'])]
    def __str__(self): return f"TS#{self.id} - {getattr(self.user,'username',self.user_id)} - {self.project.name}"
    @property
    def is_active(self): return self.end_time is None and not self.completed
    @property
    def duration_minutes(self):
        end = self.end_time or timezone.now()
        return int((end - self.start_time).total_seconds() // 60)

class TimeSessionAllocation(models.Model):
    time_session = models.ForeignKey(TimeSession, on_delete=models.CASCADE, related_name='allocations')
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name='allocations')
    minutes_allocated = models.IntegerField(blank=True, null=True)
    percent_allocated = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    class Meta:
        indexes = [models.Index(fields=['time_session']), models.Index(fields=['work_item'])]
    def __str__(self): return f"Alloc TS#{self.time_session_id} -> WI#{self.work_item_id}"

class WorkPhoto(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='work_photos')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_photos')
    time_session = models.ForeignKey(TimeSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    work_item = models.ForeignKey(WorkItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    url = models.URLField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-id']
    def __str__(self): return f"Photo#{self.id} - {self.project.name}"

# ===== SPESE =====
class CostDocument(models.Model):
    DOC_TYPES = [('fattura','Fattura'),('scontrino','Scontrino'),('ddt','DDT'),('altro','Altro')]
    STATUS = [('pending','In attesa'),('approved','Approvato'),('rejected','Respinto')]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='cost_documents')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cost_documents')
    work_item = models.ForeignKey(WorkItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cost_documents')
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES, default='fattura')
    amount_eur = models.DecimalField(max_digits=12, decimal_places=2)
    with_vat = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    doc_url = models.URLField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_cost_documents')
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-id']
        indexes = [models.Index(fields=['project']), models.Index(fields=['status'])]
    def __str__(self): return f"Cost#{self.id} - {self.project.name} - €{self.amount_eur}"

# ===== FLOTTA MEZZI =====
class Vehicle(models.Model):
    TYPES = [('van','Furgone'),('truck','Camion'),('car','Auto'),('pickup','Pickup'),('other','Altro')]
    STATUS = [('available','Disponibile'),('in_use','In uso'),('maintenance','Manutenzione'),('unavailable','Non disponibile')]
    plate = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=TYPES, default='van')
    status = models.CharField(max_length=20, choices=STATUS, default='available')
    odometer_km = models.IntegerField(default=0)
    fuel_level_percent = models.IntegerField(default=100)
    photo_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['plate']
    def __str__(self): return f"{self.plate} - {self.name}"

class VehicleSession(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='sessions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicle_sessions')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicle_sessions')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)
    start_odometer_km = models.IntegerField()
    end_odometer_km = models.IntegerField(blank=True, null=True)
    start_fuel_percent = models.IntegerField()
    end_fuel_percent = models.IntegerField(blank=True, null=True)
    notes_out = models.TextField(blank=True, null=True)
    notes_in = models.TextField(blank=True, null=True)
    damages_report = models.TextField(blank=True, null=True)
    photos_urls = models.TextField(blank=True, null=True)  # URL uno per riga
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-id']
    def __str__(self): return f"VS#{self.id} - {self.vehicle.plate} - {getattr(self.user,'username', self.user_id)}"
    @property
    def is_active(self): return self.end_time is None

# ===== DOCUMENTI HR =====
class UserFolder(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hr_folders')
    name = models.CharField(max_length=120)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['name']
        unique_together = [('owner','parent','name')]
    def __str__(self): return f"{self.owner_id}/{self.name}"

class UserFile(models.Model):
    CATEGORY = [('payslip','Busta paga'),('contract','Contratto'),('circular','Circolare'),('other','Altro')]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hr_files')
    folder = models.ForeignKey(UserFolder, on_delete=models.CASCADE, related_name='files')
    title = models.CharField(max_length=200)
    file_url = models.URLField()
    category = models.CharField(max_length=30, choices=CATEGORY, default='other')
    requires_ack = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    ack_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-id']
    def __str__(self): return f"UF#{self.id} - {self.title}"

class BroadcastDoc(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='broadcast_docs')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-id']
    def __str__(self): return self.title
