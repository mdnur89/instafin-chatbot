from django.urls import path
from . import views

app_name = 'intelligence'

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),

    # NLU Model URLs
    path('models/', views.NLUModelListView.as_view(), name='nlu_model_list'),
    path('models/create/', views.NLUModelCreateView.as_view(), name='nlu_model_create'),
    path('models/<int:pk>/', views.NLUModelDetailView.as_view(), name='nlu_model_detail'),
    path('models/<int:pk>/update/', views.NLUModelUpdateView.as_view(), name='nlu_model_update'),
    path('models/<int:model_id>/train/', views.start_training, name='start_training'),
    path('training/<int:session_id>/status/', views.get_training_status, name='training_status'),

    # FAQ URLs
    path('faqs/', views.FAQListView.as_view(), name='faq_list'),
    path('faqs/create/', views.FAQCreateView.as_view(), name='faq_create'),
    path('faqs/<int:pk>/update/', views.FAQUpdateView.as_view(), name='faq_update'),
]