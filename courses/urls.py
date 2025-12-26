from django.urls import path
from . import views

urlpatterns = [
    # Студенческие URLs
    path('', views.CourseListView.as_view(), name='course_list'),
    path('my/', views.MyCoursesView.as_view(), name='my_courses'),
    path('lesson/<int:lesson_id>/', views.LessonView.as_view(), name='lesson_view'),
    path('lesson/<int:lesson_id>/complete/', views.LessonCompleteView.as_view(), name='lesson_complete'),
    
    # Преподавательские URLs
    path('instructor/', views.InstructorCoursesView.as_view(), name='instructor_courses'),
    path('instructor/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('instructor/<slug:slug>/', views.InstructorCourseDetailView.as_view(), name='instructor_course_detail'),
    path('instructor/<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('instructor/<slug:slug>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('instructor/<slug:slug>/publish/', views.CoursePublishView.as_view(), name='course_publish'),
    path('instructor/<slug:slug>/unpublish/', views.CourseUnpublishView.as_view(), name='course_unpublish'),
    
    # Разделы
    path('instructor/<slug:course_slug>/section/create/', views.SectionCreateView.as_view(), name='section_create'),
    path('instructor/section/<int:section_id>/edit/', views.SectionUpdateView.as_view(), name='section_update'),
    path('instructor/section/<int:section_id>/delete/', views.SectionDeleteView.as_view(), name='section_delete'),
    
    # Уроки
    path('instructor/section/<int:section_id>/lesson/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('instructor/lesson/<int:lesson_id>/edit/', views.LessonUpdateView.as_view(), name='lesson_update'),
    path('instructor/lesson/<int:lesson_id>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),
    
    # Детальная страница курса (должна быть в конце)
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<slug:slug>/enroll/', views.CourseEnrollView.as_view(), name='course_enroll'),
]
