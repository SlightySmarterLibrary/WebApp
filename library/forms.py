from django import forms


class AccountVerificationForm(forms.Form):
    """Verifies a user to create their account"""
    username = forms.CharField()
    confirmation_code = forms.CharField(
        required=True, max_length=6, label="Verification Code")

    def clean(self):
        user = super(AccountVerificationForm, self).clean()
        self.user = user

        return user


class RegisterForm(forms.Form):
    """"Specifies required information for user sign up"""

    first_name = forms.CharField(max_length=200, required=True)
    last_name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    verify_password = forms.CharField(
        widget=forms.PasswordInput(), required=True)

    def clean(self):
        user = super(RegisterForm, self).clean()
        self.user = user

        if user.get('password') != user.get('verify_password'):
            self.errors['verify_password'] = \
                self.error_class(['Passwords do not match'])
            del self.user['password']

        del self.user['verify_password']

        return user
