#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event,Guest
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

# Create your views here.
def index(request):
	return render(request,"index.html")

#发布会管理	
@login_required
def event_manage(request):
	#读取浏览器session
	event_list = Event.objects.all()
	username = request.session.get("user","")
	return render(request,"event_manage.html",{"user":username,'events':event_list})

@login_required
def search_name(request):
	username = request.session.get("user","")
	search_name = request.GET.get("name","")
	search_name_bytes = search_name.encode(encoding = "utf-8")
	event_list = Event.objects.filter(name__contains = search_name)
	return render(request,"event_manage.html",{"user":username,"events":event_list})

#嘉宾管理
@login_required
def guest_manage(request):
	username = request.session.get("user","")
	guest_list = Guest.objects.all()
	paginator = Paginator(guest_list,2)
	page = request.GET.get("page")
	try:
		contacts = paginator.page(page)
	except PageNotAnInteger:
		#If page is not an integer,deliver first page
		contacts = paginator.page(1)
	except EmptyPage:
		#If page is out of range,deliver last page of results.
		contacts = paginator.page(paginator.num_pages)
	return render(request,"guest_manage.html",{"user":username,"guests":contacts})

@login_required
def search_guest(request):
	username = request.session.get("user","")
	search_guest = request.GET.get("realname","")

	search_guest_bytes = search_guest.encode(encoding = "utf-8")
	guest_list = Guest.objects.filter(realname__contains = search_guest)
	print guest_list
	paginator = Paginator(guest_list,2)
	page = request.GET.get("page")
	try:
		contacts = paginator.page(page)
	except PageNotAnInteger:
		#If page is not an integer,deliver first page
		contacts = paginator.page(1)
	except EmptyPage:
		#If page is out of range,deliver last page of results.
		contacts = paginator.page(paginator.num_pages)

	print contacts
	return render(request,"guest_manage.html",{"user":username,"guests":contacts})



#登录
def login_action(request):
	if request.method == 'POST':
		username = request.POST.get('username','')
		password = request.POST.get('password','')
		user = auth.authenticate(username=username,password=password)
		if user is not None:
			auth.login(request,user)
			request.session['user'] = username
			response = HttpResponseRedirect('/event_manage/')
			return response
		else:
			return render(request,'index.html',{'error':'username or password error!'})
