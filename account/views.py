from django.shortcuts import render, redirect

from django.views.generic import View
from django.contrib import messages
from validate_email import validate_email
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
# Create your views here.

class RegisterView(View):
	def get(self, request):
		return render(request, 'auth/register.html')

	def post(self, request):
		data = request.POST
		context = {"data":data, "has_error":False}

		email = request.POST.get('email')
		username = request.POST.get('username')
		firstName = request.POST.get('first_name')
		lastName = request.POST.get('last_name')
		password = request.POST.get('password')
		password2 = request.POST.get('password2')

		if not validate_email(email):
			messages.add_message(request, messages.ERROR, 'Please give Valid email')
			context['has_error']=True
		if len(password)<6:
			messages.add_message(request, messages.ERROR, 'Password should be al least 6 characters')
			context['has_error']=True

		if password != password2:
			messages.add_message(request, messages.ERROR, "Password doesn\'t match")
			context['has_error']=True


		if User.objects.filter(email=email).exists():
			messages.add_message(request, messages.ERROR, "Email already taken!")
			context['has_error']=True


		if User.objects.filter(username=username).exists():
			messages.add_message(request, messages.ERROR, "Username already taken!")
			context['has_error']=True

		if context['has_error']:
			return render(request, 'auth/register.html', context)

		user = User.objects.create_user(username=username,email=email)
		user.set_password(password)
		user.first_name=lastName
		user.last_name=lastName
		user.is_active = False

		user.save()

		current_site=get_current_site(request)
		email_subject='Activate your Account'
		message=render_to_string('auth/activate.html',
			{
			'user':user,
			'domain':current_site.domain,
			'uid':urlsafe_base64_encode(force_bytes(user.pk)),
			'token':generate_token.make_token(user)
			}
		)
		email_message = EmailMessage(
		    email_subject,
		    message,
		    settings.EMAIL_HOST_USER,
		    [email]
		)
		email_message.send()
			
		messages.add_message(request, messages.SUCCESS, "Account has been created")

		return redirect('login')




class LoginView(View):
	def get(self, request):
		return render(request, 'auth/login.html')

	def post(self, request):
		context={
			'data':request.POST,
			'has_error':False
		}
		username = request.POST.get('username')
		password = request.POST.get('password')

		if username=='':
			messages.add_message(request, messages.ERROR,'Username mustn\'t be empty')
			context['has_error']=True

		if password=='':
			messages.add_message(request, messages.ERROR,'Password is required.')
			context['has_error']=True

		user=authenticate(request,username=username,password=password)

		if not user and not context['has_error']:
			messages.add_message(request, messages.ERROR,'Invalid login!!')
			context['has_error']=True

		if context['has_error']:
			return render(request, 'auth/login.html', status=401, context=context)

		login(request,user)
		return redirect('home')


class LogoutView(View):
	def post(self, request):
		logout(request)
		messages.add_message(request, messages.SUCCESS,'Logout successfully.')
		return redirect('login')


class ActivateView(View):
	def get(self,request, uidb64, token):
		try:
			uid=force_text(urlsafe_base64_decode(uidb64))
			user=User.objects.get(pk=uid)
		except Exception as e:
			user=None
		

		if user is not None and generate_token.check_token(user,token):
			user.is_active=True
			user.save()
			messages.add_message(request,message.INFO,'Account activate successfully.')
			return redirect('login')
		return render(request,'auth/activate_faield.html',status=401)