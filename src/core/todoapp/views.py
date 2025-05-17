import random
import sqlite3
import time
import json
from django.core.serializers import serialize

import pandas as pd
from groq import Groq
from django.shortcuts import render
from django.http import HttpResponse
from .models import Todo
import os
from dotenv import load_dotenv
import datetime
from django.views.generic import ListView

load_dotenv()
groq_key=os.environ.get("Groq_API_KEY")

# Create your views here.
class TodoListView(ListView):
    model=Todo
    template="todoapp/todo_list.html"
    context_object_name="list_of_todo"

def todo_list(request):
  date_filter=request.GET.get("date")
  if not date_filter:
       date_filter=datetime.date.today()
       
  is_compeleted=request.GET.get("is_completed")
  if not is_compeleted:
       #is_compeleted=False
       pass
  list_of_todo=Todo.objects.filter(Date=date_filter)
  return render(request,"todoapp/todo_list.html",context={"list_of_todo":list_of_todo,"date_filter":date_filter,"is_completed":is_compeleted})          


def llm_chat(request):
    return render(request,"todoapp/llmchat.html")    

#generic llm 
def llm_generic_response(system_prompt,user_prompt,model,stream=False,max_token=200):
     res_content="Select description from todoapp_todo where is_completed=true "
     if "groq" in model:
          model=model.split("@")[0]
          #the prompt for diagnosis ,but we will add for plan as well
          client = Groq( api_key=groq_key)
          completion = client.chat.completions.create(
                model=model,
                messages=[
        {
            "role": "system",
            "content": system_prompt
              },
        {
            "role": "user", 
            "content": user_prompt
        }
                 ],
              max_completion_tokens=max_token,
               stream=stream,
    
                  )
          res_content= completion.choices[0].message.content
     return res_content     

def todo_create(request):
     try:
      title=request.POST.get("title")
      description=request.POST.get("description")
      step_by_step_execution=request.POST.get("step_by_step_execution")
      todo=Todo(title=title,description=description,step_by_step_execution=step_by_step_execution)
      todo.save()
      return HttpResponse("success",status=201)
     except Exception as e:
          print("exeption is",e)
          return HttpResponse(status=500)


def todo_get(request,id:int):
    try:
     todo=Todo.objects.get(pk=id)
    except:
        return HttpResponse(status=500)
    todo_json = serialize('json', [todo,])
    return HttpResponse(todo_json, content_type='application/json',status=200)
    
    

def todo_update(request):
     id=request.POST.get("id")
     title=request.POST.get("title")
     description=request.POST.get("description")
     step_by_step_execution=request.POST.get("step_by_step_execution")
     todo=Todo.objects.get(id=id)
     todo.title=title
     todo.description=description
     todo.step_by_step_execution=step_by_step_execution
     todo.save()
     return HttpResponse(status=204)
def todo_delete(request):
     id=request.POST.get("id")
     todo=Todo.objects.get(id=id)
     todo.delete()
    
     return HttpResponse("success",status=204)
def  todo_complete(request):
      try:
       id=request.POST.get("id")
       todo=Todo.objects.get(id=id)
       todo.is_completed=True
       print(todo)
       print(todo.is_completed)
       todo.save()
    
       return HttpResponse("success",status=200)
      except Exception as ex:
           return HttpResponse(f"error,{ex}",status=500) 

# def text_to_sql_response(model,user_prompt):
 
#     sql_response=text_to_sql(model,user_prompt)
#     llm_response=sql_to_text(model,sql_response)
#     return llm_response
def db_data_manipulate(model,user_prompt):
     #text to sql
     sql_command=text_to_sql(model,user_prompt)
     print(sql_command)
     #execute sql command
     raw_sql=execute_db_command(sql_command,"db.sqlite3","read")
     #sql to text
     formatted_response=sql_to_text(model,user_prompt=raw_sql)
     print(formatted_response)
     return formatted_response
#convert user input to sql query/command
def text_to_sql(model,user_prompt):
     system_prompt="""
     You are an expert in converting English questions to SQL query!
     All tables start with todoapp_, hence if the table name is student ,add prefix to it and call it todoapp_student.
The SQL database has table called Todo and has the following columns -Title ,Description,Date, StepByStepExecution,is_completed  \n\n For example,\n 
only select  with the first  three columns. Gien student table with name,class,age,gender,address columns lets see the following examples.
 Example 1- get all students ,the sql command will be something like Select (name,class,age) from student.


Example 2- How many entries of records are present the SQL command will be something like this SELECT COUNT(*) FROM STUDENT;
\\nExample 3-  Fetch all todos with status completed
the SQL command will be something like this SELECT (title,description ,date) FROM todo where is_completed="True";
also the sql code should not have '''in the beginning or end and sql word in the command

"""
     llm_response=llm_generic_response(system_prompt=system_prompt,model=model,user_prompt=user_prompt)
     return llm_response

#convert  sql output to text
def sql_to_text(model,user_prompt):
     model="mistral-saba-24b@groq"
     system_prompt="""

           "You are a formatting assistant.format and structure this in a nice structured  format!
            trim also any column value of the table with length greater than 25 characters and add ...
            For example: if column value  is "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" make it 
            "aaaaaaaaaaaaaaaaaaaaaaaaa..."
     
           only responde the table format ,dont add any comments or text
           give enough space between the columns
            """
     llm_response=llm_generic_response(system_prompt=system_prompt,model=model,user_prompt=user_prompt)
     return llm_response
 

def speech_recognition(model,audio):
      pass
def generate_image():
      pass
def text_generation(model,user_prompt):
      system_prompt="you are helpfull assistant"
      llm_response=llm_generic_response(system_prompt=system_prompt,model=model,user_prompt=user_prompt)
      return llm_response
      

def get_ai_response(request):
    llm_task=request.POST.get("llm_task")
    model=request.POST.get("model")
    user_prompt=request.POST.get("user_prompt")
    audio='audio'
    llm_response=""
    print(llm_task)
    if llm_task=="db_manipulation":
         llm_response= db_data_manipulate(model,user_prompt)
    elif llm_task=="speech recognition":
        llm_response=speech_recognition(model,audio)     
    elif llm_task=="image generation":
          generate_image()
    else:
        llm_response= text_generation(model,user_prompt)      

    return HttpResponse(llm_response)

def execute_db_command(sql_command,db,command_type):
     res=""
     try:
      if command_type=="read":
        conn=sqlite3.connect(db)
        df=pd.read_sql_query(sql_command,conn)
    
        curr=conn.cursor()
        data=curr.execute(sql_command)
        names = [description[0] for description in data.description]
        print(names)
        rows=curr.fetchall()
        col_names=f"column name list:{names}"
        raw_sql="raw sql data:"
        conn.commit()
        conn.close()
        for row in rows:
             raw_sql+=str(row)+"\n"
             print(raw_sql)

        res=  col_names+""+raw_sql   
        return res
     except Exception as ex:
         res=f"exceptio of {ex} occured"
         return res 
     

     