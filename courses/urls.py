from django.urls import path
from . import views

urlpatterns = [
    # Студенческие URLs
    path('', views.CourseListView.as_view(), name='course_list'),
    path('my/', views.MyCoursesView.as_view(), name='my_courses'),
    path('lesson/<int:lesson_id>/', views.LessonView.as_view(), name='lesson_view'),
    path('lesson/<int:lesson_id>/complete/', views.LessonCompleteView.as_view(), name='lesson_complete'),
    
    # Комментарии к урокам
    path('lesson/<int:lesson_id>/comment/', views.LessonCommentCreateView.as_view(), name='lesson_comment_create'),
    path('comment/<int:comment_id>/edit/', views.LessonCommentUpdateView.as_view(), name='lesson_comment_update'),
    path('comment/<int:comment_id>/delete/', views.LessonCommentDeleteView.as_view(), name='lesson_comment_delete'),
    path('comment/<int:comment_id>/pin/', views.InstructorCommentPinView.as_view(), name='lesson_comment_pin'),
    
    # Сертификаты
    path('certificates/', views.MyCertificatesView.as_view(), name='my_certificates'),
    path('certificate/<str:certificate_number>/', views.CertificateDetailView.as_view(), name='certificate_detail'),
    path('certificate/<str:certificate_number>/print/', views.CertificatePrintView.as_view(), name='certificate_print'),
    path('verify/', views.CertificateVerifyView.as_view(), name='certificate_verify'),
    path('verify/<str:certificate_number>/', views.CertificateVerifyView.as_view(), name='certificate_verify_number'),
    
    # Платежи
    path('checkout/<slug:slug>/', views.CourseCheckoutView.as_view(), name='course_checkout'),
    path('payment/stripe/<int:purchase_id>/', views.StripePaymentView.as_view(), name='stripe_payment'),
    path('payment/paypal/<int:purchase_id>/', views.PayPalPaymentView.as_view(), name='paypal_payment'),
    path('payment/yookassa/<int:purchase_id>/', views.YookassaPaymentView.as_view(), name='yookassa_payment'),
    path('payment/success/<int:purchase_id>/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/failed/<int:purchase_id>/', views.PaymentFailedView.as_view(), name='payment_failed'),
    path('purchases/', views.PurchaseHistoryView.as_view(), name='purchase_history'),
    path('refund/<int:purchase_id>/', views.RefundRequestView.as_view(), name='refund_request'),
    
    # Тесты (Преподаватели)
    path('instructor/lesson/<int:lesson_id>/quiz/create/', views.InstructorQuizCreateView.as_view(), name='quiz_create'),
    path('instructor/quiz/<int:quiz_id>/', views.InstructorQuizDetailView.as_view(), name='instructor_quiz_detail'),
    path('instructor/quiz/<int:quiz_id>/question/create/', views.QuestionCreateView.as_view(), name='question_create'),
    
    # Домашние задания (Студенты)
    path('assignment/<int:assignment_id>/submit/', views.AssignmentSubmitView.as_view(), name='assignment_submit'),
    
    # Преподаватель - Курсы
    path('instructor/', views.InstructorCoursesView.as_view(), name='instructor_courses'),
    path('instructor/course/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('instructor/course/<slug:slug>/', views.InstructorCourseDetailView.as_view(), name='instructor_course_detail'),
    path('instructor/course/<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('instructor/course/<slug:slug>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('instructor/course/<slug:slug>/publish/', views.CoursePublishView.as_view(), name='course_publish'),
    path('instructor/course/<slug:slug>/unpublish/', views.CourseUnpublishView.as_view(), name='course_unpublish'),
    
    # Преподаватель - Разделы
    path('instructor/course/<slug:course_slug>/section/create/', views.SectionCreateView.as_view(), name='section_create'),
    path('instructor/section/<int:section_id>/edit/', views.SectionUpdateView.as_view(), name='section_update'),
    path('instructor/section/<int:section_id>/delete/', views.SectionDeleteView.as_view(), name='section_delete'),
    
    # Преподаватель - Уроки
    path('instructor/section/<int:section_id>/lesson/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('instructor/lesson/<int:lesson_id>/edit/', views.LessonUpdateView.as_view(), name='lesson_update'),
    path('instructor/lesson/<int:lesson_id>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),
    
    # Домашние задания (Преподаватели)
    path('instructor/lesson/<int:lesson_id>/assignment/create/', views.InstructorAssignmentCreateView.as_view(), name='assignment_create'),
    path('instructor/assignment/<int:assignment_id>/', views.InstructorAssignmentDetailView.as_view(), name='instructor_assignment_detail'),
    path('instructor/submission/<int:submission_id>/grade/', views.InstructorAssignmentGradeView.as_view(), name='assignment_grade'),
    
    # Отзывы и рейтинги
    path('<slug:slug>/reviews/', views.CourseReviewsView.as_view(), name='course_reviews'),
    path('<slug:slug>/review/create/', views.ReviewCreateView.as_view(), name='review_create'),
    path('<slug:slug>/review/edit/', views.ReviewUpdateView.as_view(), name='review_update'),
    path('<slug:slug>/review/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    
    # Детальная страница курса (должна быть в конце)
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<slug:slug>/enroll/', views.CourseEnrollView.as_view(), name='course_enroll'),
]
