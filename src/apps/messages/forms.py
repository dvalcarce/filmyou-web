# -*- coding: utf-8 -*-

import autocomplete_light
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from userena.contrib.umessages.models import Message


class MessageForm(forms.Form):
    to = forms.ModelMultipleChoiceField(
        User.objects.all(),
        widget=autocomplete_light.MultipleChoiceWidget('UserAutocomplete'),
        label=_('To')
    )

    to.help_text = u''

    body = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea({'class': 'message'}),
        required=True
    )

    def save(self, sender):
        """
        Save the message and send it out into the wide world.

        :param sender:
        The :class:`User` that sends the message.

        :param parent_msg:
        The :class:`Message` that preceded this message in the thread.

        :return: The saved :class:`Message`.

        """
        um_to_user_list = self.cleaned_data['to']
        body = self.cleaned_data['body']
        msg = Message.objects.send_message(sender, um_to_user_list, body)

        return msg