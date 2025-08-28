from django.contrib import admin
from .models import (
    Project, WorkItem,
    TimeSession, TimeSessionAllocation, WorkPhoto,
    CostDocument,
    Vehicle, VehicleSession,
    UserFolder, UserFile, BroadcastDoc
)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id','name','client_name','status','budget_eur','start_date','end_date')
    list_filter = ('status',)
    search_fields = ('name','client_name')

@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ('id','project','name','parent','status','progress','weight','sort_order')
    list_filter = ('status','project')
    search_fields = ('name',)
    autocomplete_fields = ('project','parent')

class TimeSessionAllocationInline(admin.TabularInline):
    model = TimeSessionAllocation
    extra = 0

@admin.register(TimeSession)
class TimeSessionAdmin(admin.ModelAdmin):
    list_display = ('id','project','user','start_time','end_time','completed')
    list_filter = ('completed','project','user')
    autocomplete_fields = ('project','user')
    inlines = [TimeSessionAllocationInline]
    search_fields = ('id','project__name','user__username','user__email','note')

@admin.register(WorkPhoto)
class WorkPhotoAdmin(admin.ModelAdmin):
    list_display = ('id','project','user','time_session','work_item','url','created_at')
    list_filter = ('project','user')
    autocomplete_fields = ('project','user','time_session','work_item')
    search_fields = ('url','description','project__name','user__username','work_item__name')

@admin.register(CostDocument)
class CostDocumentAdmin(admin.ModelAdmin):
    list_display = ('id','project','user','work_item','doc_type','amount_eur','with_vat','status','created_at')
    list_filter = ('status','doc_type','project')
    search_fields = ('project__name','user__username','user__email','work_item__name')
    autocomplete_fields = ('project','user','work_item','approved_by')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id','plate','name','vehicle_type','status','odometer_km','fuel_level_percent')
    list_filter = ('status','vehicle_type')
    search_fields = ('plate','name')

@admin.register(VehicleSession)
class VehicleSessionAdmin(admin.ModelAdmin):
    list_display = ('id','vehicle','user','project','start_time','end_time','start_odometer_km','end_odometer_km')
    list_filter = ('vehicle','user','project')
    autocomplete_fields = ('vehicle','user','project')
    search_fields = ('id','vehicle__plate','vehicle__name','user__username','user__email','project__name','notes_out','notes_in','damages_report')

@admin.register(UserFolder)
class UserFolderAdmin(admin.ModelAdmin):
    list_display = ('id','owner','name','parent','created_at')
    list_filter = ('owner',)
    search_fields = ('name','owner__username','owner__email')
    autocomplete_fields = ('owner','parent')

@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):
    list_display = ('id','owner','folder','title','category','requires_ack','read_at','ack_at','created_at')
    list_filter = ('category','requires_ack','owner')
    search_fields = ('title','owner__username','owner__email','folder__name')
    autocomplete_fields = ('owner','folder')

@admin.register(BroadcastDoc)
class BroadcastDocAdmin(admin.ModelAdmin):
    list_display = ('id','title','created_by','created_at')
    search_fields = ('title','created_by__username','created_by__email')
    autocomplete_fields = ('created_by',)
