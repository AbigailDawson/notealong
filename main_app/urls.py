from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('collections/', views.collections_index, name='index'),
    path('collections/<int:collection_id>/', views.collections_detail, name='detail'),
    path('collections/create/', views.CollectionCreate.as_view(), name='collections_create'),
    path('collections/<int:pk>/update/', views.CollectionUpdate.as_view(), name='collections_update'),
    path('collections/<int:pk>/delete/', views.CollectionDelete.as_view(), name='collections_delete'),
    path('collections/<int:collection_id>/assoc_ref/', views.assoc_ref, name='assoc_ref'),
    path('collections/<int:collection_id>/unassoc_ref/<int:reference_id>', views.unassoc_ref, name='unassoc_ref'),
    path('collections/<int:collection_id>/notes/create/', views.NoteCreate.as_view(), name='notes_create'),
    path('collections/<int:collection_id>/notes/<int:pk>/update/', views.NoteUpdate.as_view(), name='notes_update'),
    path('collections/<int:collection_id>/notes/<int:pk>/delete/', views.NoteDelete.as_view(), name='notes_delete'),
    path('references/', views.ReferenceIndex.as_view(), name='references_index'),
    path('references/create/', views.ReferenceCreate.as_view(), name='references_create'),
    path('references/<int:pk>/update/',views.ReferencePageUpdate.as_view(),name='references_page_update'),
    path('references/<int:pk>/delete/',views.ReferencePageDelete.as_view(),name='references_page_delete'),
    path('collections/<int:collection_id>/references/create/', views.ReferenceCreate.as_view(), name='references_create'),
    path('collections/<int:collection_id>/references/<int:pk>/update/', views.ReferenceUpdate.as_view(), name='references_update'),
    path('collections/<int:collection_id>/references/<int:pk>/delete/',views.ReferenceDelete.as_view(), name='references_delete'),
    path('shared-collections/', views.shared_collections_index, name='shared_collections'),
    path('shared-collections/<int:collection_id>/', views.shared_collections_detail, name='shared_collections_detail'),
    path('search/', views.SearchResults.as_view(), name='search_results'),
    path('search/<int:collection_id>/', views.search_results_detail, name="search_results_detail"),
    path('saved-collections/', views.saved_collections_index, name='saved_collections_index'),
    path('saved-collections/<int:collection_id>/', views.saved_collections_detail, name='saved_collections_detail'),
    path('saved-collections/<int:collection_id>/add', views.saved_collections_add, name='saved_collections_add'),
    path('saved-collections/<int:collection_id>/remove', views.saved_collections_remove, name='saved_collections_remove')
]