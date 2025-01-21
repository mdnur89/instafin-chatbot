from django.urls import path
from . import views

app_name = 'loan_management'

urlpatterns = [
    path('applications/', views.LoanApplicationListView.as_view(), name='application_list'),
    path('applications/create/', views.loan_application_create, name='application_create'),
    path('applications/<int:pk>/', views.loan_application_detail, name='application_detail'),
    path('applications/<int:application_pk>/upload/', views.document_upload, name='document_upload'),
    path('applications/<int:application_pk>/request-document/', 
         views.document_request_create, name='document_request_create'),
]