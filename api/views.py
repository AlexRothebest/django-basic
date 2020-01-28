from django.shortcuts import HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.template.context_processors import csrf
from django.core.mail import send_mail

from main.models import Client

import json, secrets, string


alphabet = string.ascii_letters + string.digits


def return_json_response(data, status_code = 200):
	response = HttpResponse(json.dumps(data), content_type = 'application/json')
	response.status_code = status_code
	return response


def login(request):
	if request.is_ajax() and request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = auth.authenticate(username = username, password = password)
		if user is not None:
			auth.login(request, user)
			result = {
				'status': 'accepted',
				'message': 'OK'
			}
		else:
			print(user)
			result = {
				'status': 'Not accepted',
				'message': 'Wrong username or password'
			}

		return return_json_response(result)
	else:
		result = {
			'status': 'Not accepted',
			'message': 'Wrong method'
		}
		return return_json_response(result, 400)


def logout(request):
	auth.logout(request)
	result = {
		'status': 'accepted',
		'message': 'Logout successful'
	}
	return redirect('/')


def add_user(request):
	if request.user.is_authenticated:
		if request.is_ajax() and request.method == 'POST':
			name = request.POST['name']
			surname = request.POST['surname']
			email = request.POST['email'].lower()
			status = request.POST['status']
			username = request.POST['username']
			password = request.POST['password']

			client = Client.objects.get(account = request.user)
			if client.status != 'a':
				status = 'user'

			if len(User.objects.filter(username = username)) != 0:
				result = {
					'status': 'Not accepted',
					'message': 'Existing username'
				}
				return return_json_response(result)
			elif len(Client.objects.filter(email = email)) != 0:
				result = {
					'status': 'Not accepted',
					'message': 'Existing email'
				}
				return return_json_response(result)
			else:
				html_message = f'Congratulations, {name}!<br><br>\
								 Somebody (probably you) registered you in our\
								 <a href = "https://127.0.0.1:8000/" style = "color: blue; text-decoration: none;">small developing site</a><br><br>\
								 Your username: {username}<br>\
								 Your password: {password}<br><br>\
								 Enjoy!'
				send_mail('Account verification', 'Lol', 'Kek', [email], html_message = html_message)

				new_user = User.objects.create_user(username = username,
													password = password)
				if status == 'admin':
					new_user.is_staff = True
				new_user.save()

				if not request.user.is_authenticated:
					auth.login(request, new_user)

				new_client = Client(
					name = name,
					surname = surname,
					email = email,
					status = status[0],
					account = new_user
					)
				new_client.save()
				print('\n\nNew client was created\n\n')

				result = {
					'status': 'accepted',
					'message': 'OK'
				}
				return return_json_response(result, 201)
		else:
			result = {
				'status': 'Not accepted',
				'message': 'Wrong method'
			}
			return return_json_response(result, 400)
	else:
		result = {
			'status': 'Not accepted',
			'message': 'Authentication required'
		}
		return return_json_response(result, 401)


def restore_password(request):
	global alphabet

	if request.is_ajax() and request.method == 'POST':
		try:
			username = request.POST['username']
			if len(User.objects.filter(username = username)) == 0:
				result = {
					'status': 'Not accepted',
					'message': 'Usename does not exist'
				}
				return return_json_response(result)
			else:
				print(User.objects.filter(username = username))
				print(Client.objects.filter(account = User.objects.get(username = username)))
				client = Client.objects.get(account = User.objects.get(username = username))
				email = client.email
				success = True
		except:
			email = request.POST['email'].lower()
			if len(Client.objects.filter(email = email)) == 0:
				result = {
					'status': 'Not accepted',
					'message': 'Email does not exist'
				}
				return return_json_response(result)

		client = Client.objects.filter(email = email)[0]
		name = client.name
		user = client.account
		new_password = ''.join(secrets.choice(alphabet) for i in range(12))
		user.set_password(new_password)
		user.save()

		send_mail('Restoring password', '', '', [email], html_message = 'Hello, ' + name + '!<br><br>Your new password: ' + new_password + '<br><br>Enjoy!')
		result = {
			'status': 'accepted',
			'message': ''
		}
		return return_json_response(result)
	else:
		result = {
			'status': 'Not accepted',
			'message': 'Wrong method'
		}
		return return_json_response(result, 400)