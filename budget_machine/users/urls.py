from django.urls import path
from . import views,auth,record
#each url start after members
urlpatterns = [
    path('', views.home, name='home'),
    path('user_manual/', views.user_manual, name='user_manual'),
    path('about_us/', views.about_us, name='about_us'),
    path('sign_in/', auth.Auth.sign_in, name='sign_in'),
    path('sign_up/', auth.Auth.sign_up, name='sign_up'),
    path('sign_out/', auth.Auth.sign_out, name='sign_out'),
    path('delete_user/', auth.Auth.delete_user, name='delete_user'),
    path('update_profile/', auth.Auth.update_profile , name='update_profile'),
    path('welcome/', record.Record.welcome, name="welcome"),
    path('view_all_records/', record.Record.view_all_records , name='view_all_records'),
    path('add_budget/', record.Record.add_budget , name='add_budget'),
    path('withdraw_amount/', record.Record.withdraw_amount , name='withdraw_amount'),
    path('transaction/', record.Record.transaction , name='transaction'),
    path('view_transaction_chart/', record.Record.view_transaction_chart , name='view_transaction_chart'),
]
