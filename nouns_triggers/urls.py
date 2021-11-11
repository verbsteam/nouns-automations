from django.urls import path

from nouns_triggers import views

urlpatterns = [
    path('auctions/', views.get_auctions),
    path('noun<int:noun_id>.png', views.get_png_for_noun_id, name='noun-img'),
    path('proposals/', views.get_proposals),
    path('proposals-time-updates/', views.get_proposals_time_updates),
    path('webhooks/before-auction/zapier/', views.WebhookRegistrationView.as_view()),
    path('webhooks/before-auction/integromat/', views.WebhookRegistrationView.as_view()),
    path('current-auction/', views.before_auction_example),
    path('auth/zapier/', views.ZapierAuthView.as_view()),
]
