from django.urls import path
from . import views

urlpatterns = [
    path('', views.redirect_home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Progetti
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),

    # Lavorazioni
    path('projects/<int:project_id>/work-items/new/', views.workitem_create, name='workitem_create'),
    path('work-items/<int:pk>/edit/', views.workitem_edit, name='workitem_edit'),
    path('work-items/<int:pk>/delete/', views.workitem_delete, name='workitem_delete'),
    path('work-items/<int:pk>/status/<str:new_status>/', views.workitem_set_status, name='workitem_set_status'),
    path('work-items/<int:pk>/progress/<int:value>/', views.workitem_set_progress, name='workitem_set_progress'),

    # Timbrature
    path('times/', views.times_list, name='times_list'),
    path('times/start/', views.times_start, name='times_start'),
    path('times/active/', views.times_active, name='times_active'),
    path('times/<int:pk>/', views.times_detail, name='times_detail'),
    path('times/<int:pk>/stop/', views.times_stop, name='times_stop'),
    path('times/<int:pk>/alloc/add/', views.times_alloc_add, name='times_alloc_add'),
    path('times/alloc/<int:pk>/delete/', views.times_alloc_delete, name='times_alloc_delete'),

    # Spese
    path('costs/', views.costs_list, name='costs_list'),
    path('costs/new/', views.costs_new, name='costs_new'),
    path('costs/<int:pk>/', views.costs_detail, name='costs_detail'),
    path('costs/<int:pk>/approve/', views.costs_approve, name='costs_approve'),
    path('costs/<int:pk>/reject/', views.costs_reject, name='costs_reject'),
    path('costs/<int:pk>/delete/', views.costs_delete, name='costs_delete'),

    # Flotta
    path('fleet/', views.fleet_list, name='fleet_list'),
    path('fleet/<int:pk>/', views.fleet_detail, name='fleet_detail'),
    path('fleet/<int:vehicle_id>/checkout/', views.fleet_checkout, name='fleet_checkout'),
    path('fleet/session/<int:pk>/checkin/', views.fleet_checkin, name='fleet_checkin'),

    # Documenti HR
    path('documents/', views.docs_home, name='docs_home'),
    path('documents/folder/<int:pk>/', views.docs_folder, name='docs_folder'),
    path('documents/file/<int:pk>/', views.docs_file, name='docs_file'),
]


