from django.urls import path
from . import views

urlpatterns = [
    # path('dummydata/', views.dummydata),
    path('import_csv/', views.import_csv, name='import_csv'),
    path('risk_calculation/', views.risk_calculation),
    path('students/', views.students_list),
    path('students/<int:pk>/', views.student_detail),
    path('regulations/', views.regulations_list),
    path('regulations/<int:pk>/', views.regulations_detail),
    path('measures/', views.measures_list),
    path('measures/<int:pk>/', views.measures_detail),
    path('violations/', views.violations_list),
    path('violations/<int:pk>/', views.violations_detail),
    
]