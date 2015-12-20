# django-rest-accounts

Django rest accounts provides a set of endpoints for user registration, authentication, and modification

rest-accounts was inspired by django-rest-auth (https://github.com/Tivix/django-rest-auth), and was created in an attempt to
both understand account creation/modificaion in django and to modify/add a couple features I wanted.

## Endpoints

### /token/ (POST/DELETE)
* username
* password

### /register/ (POST)
* Username
* Password
* email
* first_name (optional)
* last_name (optional)

### /activate/activation_token/ (GET)

### /user/ (requires authentication via token or username/password)
* GET - retreives information about authenticated user
* PUT - allows user information other than username or password to be updated

### /password/change/ (PUT) (requires authentication via token or username/password)
* old_password
* new_password

### /password/reset (POST)
* username OR email

### /password/reset/confirm/recovery_token/ (GET)
