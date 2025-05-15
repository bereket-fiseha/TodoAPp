from django.urls import path
from . import views

app_name="todoapp"
urlpatterns = [
    path('',views.todo_list ,name="todo_list"),
    path('ai/chat',views.llm_chat ,name="llm_chat"),
    path('ai/get_response',views.get_ai_response ,name="get_ai_response"),
    
    path('todo/create',views.todo_create ,name="todo_create"),
    
    path('todo/update',views.todo_update ,name="todo_update"),
    path('todo/delete',views.todo_delete ,name="todo_delete"),
    path('todo/complete',views.todo_complete ,name="todo_complete"),

]