from django.urls import path
from . import views

urlpatterns = [
    path('step1/', views.document_wizard_step1, name='document_step1'),
    path('step2/', views.document_wizard_step2, name='document_step2'),
    path('step3/', views.document_wizard_step3, name='document_step3'),
    path('status/<int:doc_id>/', views.document_status, name='document_status'),
    path('preview/<int:doc_id>/', views.document_preview, name='document_preview'),
    path('list/', views.document_list, name='document_list'),
    path('search/', views.search_documents, name='document_search'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('download/pdf/<int:doc_id>/', views.download_pdf, name='download_pdf'),
    path('download/docx/<int:doc_id>/', views.download_docx, name='download_docx'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('download-sample-excel/', views.download_sample_excel, name='download_sample_excel'),
    path('regenerate/<int:doc_id>/', views.regenerate_document, name='regenerate_document'),
    path('bulk-action/', views.bulk_action, name='bulk_action'),
    path('verify/', views.verify_form, name='verify_form'),  # form to enter number
    path('verify/<path:document_number>/', views.verify_document, name='verify'), 
]