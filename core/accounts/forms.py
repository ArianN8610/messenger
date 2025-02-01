from django import forms

from .models import Profile


class ProfileCompleteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs['class'] = 'file-input file-input-bordered w-full'
        self.fields['first_name'].widget.attrs['class'] = 'input input-bordered w-full'
        self.fields['last_name'].widget.attrs['class'] = 'input input-bordered w-full'
        self.fields['bio'].widget.attrs['class'] = 'textarea textarea-bordered'
        self.fields['bio'].widget.attrs['placeholder'] = 'Type something about yourself here'

    class Meta:
        model = Profile
        exclude = ('user',)
