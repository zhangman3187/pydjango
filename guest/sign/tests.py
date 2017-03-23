#-*- coding:utf-8 -*-
from django.test import TestCase
from sign.models import Event,Guest
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from sign.views import index
from django.template.loader import render_to_string
from django.template import RequestContext
from django.test import Client
from django.contrib.auth.models import User
from datetime import datetime


# Create your tests here.

class ModelTest(TestCase):

	def setUp(self):
		Event.objects.create(id=1,name="oneplus 3 event",status=True,limit=2000,address="shenzhen",start_time="2016-08-31 02:18:22")
		Guest.objects.create(id=1,event_id=1,realname="alen",phone="13711001101",email="alen@mail.com",sign=False)

	def test_event_models(self):
		result = Event.objects.get(name="oneplus 3 event")
		self.assertEqual(result.address,"shenzhen")
		self.assertTrue(result.status)

	def test_guest_models(self):
		result = Guest.objects.get(phone="13711001101")
		self.assertEqual(result.realname,"alen")
		self.assertFalse(result.sign)

#Test index
class IndexPageTest(TestCase):

	''' 测试index登录首页'''
	def test_root_url_resolves_to_index_page(self):

		''' 测试根url是否解析到登录页'''
		found = resolve('/')
		self.assertEqual(found.func,index)

	def test_index_page_returns_correct_html(self):

		''' 测试调用index函数返回的页于模板加载的index.html是否相等'''
		request = HttpRequest()
		response = index(request)
		expected_html = render_to_string('index.html',context_instance=RequeseContext(request))
		self.assertMuiliLineEqual(expected_html,response.content.decode())

#Test Login action
class LoginActionTest(TestCase):
	''' 测试登录动作 '''

	def setUp(self):
		User.objects.create_user('admin','admin@mail.com','admin123456')

	def test_add_author_email(self):
		''' 测试添加用户'''
		user = User.objects.get(username = "admin")
		self.assertEqual(user.username,"admin")
		self.assertEqual(user.email,"admin@mail.com")

	def  test_login_action_username_password_null(self):
		''' 用户名密码为空 '''
		c = Client()
		response = c.post('/login_action/',{'username':'','password':''})
		self.assertEqual(response.status_code,200)
		self.assertIn("用户名或密码错误",response.content)

	def test_login_action_username_password_error(self):
		''' 用户名密码错误 '''
		c = Client()
		response = c.post('/login_action/',{'username':'abc','password':'123'})
		self.assertEqual(response.status_code,200)
		self.assertIn("用户名或密码错误",response.content)

	def test_login_action_success(self):
		'''登录成功 '''
		c = Client()
		response = c.post('login_action/',data={'username':'admin','password':'admin123456'})
		self.assertEqual(response.status_code,302)

#Test Event Manage

class EventManageTest(TestCase):
	''' 发布会管理 '''
	def setUp(self):
		Event.objects.create(id=2,name='xiaomi5',limit=2000,status=True,address='beijing',start_time=datetime(2016,8,10,14,0,0))

	def test_date(self):
		''' 测试添加的发布会'''
		event = Event.objects.get(name='xiaomi5')
		self.assertEqual(event.address,'beijing')

	def test_event_manage_succsee(self):
		''' 测试发布会:xiaomi5'''
		c = Client()
		response = c.post('/event_manage/')
		self.assertEqual(response.status_code,200)
		self.assertIn('xiaomi5',response.content)
		self.assertIn('beijing',response.content)

	def test_event_manage_search_success(self):
		''' 测试发布会搜索 '''
		c = Client()
		response = c.post('/search_name/',{'name':'xiaomi5'})
		self.assertEqual(response.status_code,200)
		self.assertIn('xiaomi5',response.content)
		self.assertIn('beijing',response.content)

#Test Guest Manage
class GuestManageTest(TestCase):
	''' 嘉宾管理'''

	def setUp(self):
		Event.objects.create(id=1,name="xiaomi5",limit=2000,address='beijing',status=1,start_time=datetime(2016,8,10,14,0,0))
		Guest.objects.create(realname='alen',phone='18611001100',email='alen@mail.com',sign=0,event_id=1)

	def test_data(self):
		''' 测试添加嘉宾'''
		guest = Guest.objects.get(realname='alen')
		self.assertEqual(guest.phone,'18611001100')
		self.assertEqual(guest.email,'alen@mail.com')
		self.assertFalse(guest.sign)

	def test_event_manage_success(self):
		''' 测试嘉宾信息：alen'''
		c = Client()
		response = c.post('/guest_manage/')
		self.assertEqual(response.status_code,200)
		self.assertIn('alen',response.content)
		self.assertIn('18611001100',response.content)

	def test_guest_manage_search_success():
		''' 测试嘉宾搜索'''
		c = Client()
		response = c.post('/search_phone/',{'phone':'18611001100'})
		self.assertEqual(response.status_code,200)
		self.assertIn('alen',response.content)
		self.assertIn('18611001100',response.content)

#Test User Sign
class SignIndexActionTest(TestCase):
	''' 发布会签到 '''

	def setUp(self):
		Event.objects.create(id=1,name='xiaomi5',limit=2000,address='beijing',status=1,start_time='2017-8-10 12:30:00')
		Event.objects.create(id=2,name='oneplus4',limit=2000,address='shenzhen',status=1,start_time='2017-6-10 12:30:00')
		Guest.objects.create(realname='alen',phone='18611001100',email='alen@mail.com',sign=0,event_id=1)
		Guest.objects.create(realname='una',phone='18611001101',email='una@mail.com',sign=1,event_id=2)

	def test_sign_index_action_phone_null(self):
		''' 手机号码为空 '''
		c = Client()
		response = c.post('/sign_index_action/1/',{'phone':''})
		self.assertEqual(response.status_code,200)
		self.assertIn('手机号为空或不存在',response.content)

	def test_sign_index_action_phone_or_event_is_error(self):
		''' 手机号码或者发布会id错误 '''
		c = Client()
		response = c.post('/sign_index_action/2/',{'phone':'18611001100'})
		self.assertEqual(response.status_code,200)
		self.assertIn('该用户未参加此次发布会',response.content)

	def test_sign_index_action_user_sign_has(self):
		''' 用户已签到 '''
		c = Client()
		response = c.post('/sign_index_action/2/',{'phone':'18611001101'})
		self.assertEqual(response.status_code,200)
		self.assertIn('已签到',response.content)

	def test_sign_index_action_sign_success(self):
		'''签到成功 '''
		c = Client()
		response = c.post('/sign_index_action/1/',{'phone':'18611001100'})
		self.assertEqual(response.status_code,200)
		self.assertIn('签到成功',response.content)
















