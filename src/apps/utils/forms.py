# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from userena.forms import EditProfileForm
from userena.utils import get_profile_model


class EditProfileFormExtra(EditProfileForm):
    class Meta:
        model = get_profile_model()
        exclude = ['user', 'mugshot', 'privacy']

    def __init__(self, *args, **kwargs):
        super(EditProfileFormExtra, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'edit-profile-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.help_text_inline = True
        self.helper.add_input(Submit('submit', _('Save'), css_class='green'))
        self.helper.layout = Layout(
            Field('first_name', placeholder=_("First Name")),
            Field('last_name', placeholder=_("Last Name")),
            Field('language', css_class="chosen"),
            Field('timezone', css_class="chosen"),
        )