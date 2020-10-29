__author__ = 'mohamed'
from django import forms
from . import models
from deployment.models import Server, SSHKey
import os
import autoDeploy.settings as settings

repo_type = [('git', 'git')]
update_style = [('commit', "commits"), ("tag", "tags")]
cfile_choices = [('','Select'),('file', "File"), ("branch", "Branch")]


def saveFile(file, project_name):
    if file == '':
        print("No File to save.")
        return ''
    if not os.path.exists(settings.MEDIA_ROOT+"/"+project_name):
        os.makedirs(settings.MEDIA_ROOT+"/"+project_name)
    fpath = settings.MEDIA_ROOT+"/"+project_name+"/"+file.name
    with open(fpath, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return fpath

class CIProjectsForm(forms.ModelForm):
    working_dir = forms.CharField(label="Working Directory", widget=forms.TextInput(attrs={'class': 'form-control', 'size': 30}))
    repo_type = forms.ChoiceField(choices=repo_type, label="Repo Type", widget=forms.Select(attrs={"class": "form-control"}))
    update_style = forms.ChoiceField(choices=update_style,label="Update Style",widget=forms.Select(attrs={"class":"form-control"}))
    cfile = forms.ChoiceField(choices=cfile_choices,label="Config File From",widget=forms.Select(attrs={"class":"form-control","onchange":"cfile_handler(this)"}))
    name = forms.CharField(label='Project Name',widget=forms.TextInput(attrs={'class':'form-control','size':30}))
    slackch = forms.CharField(label='Slack Channel', widget=forms.TextInput(attrs={'class': 'form-control', 'size': 30}))
    repo_link = forms.CharField(label='Repo Link',widget=forms.TextInput(attrs={'class':'form-control','size':30}))
    repo = forms.CharField(label='Repo',widget=forms.TextInput(attrs={'class':'form-control','size':30}))
    # integration_link = forms.CharField(label='Integration Link',widget=forms.TextInput(attrs={'class':'form-control','size':30}))
    emailUsers = forms.CharField(required=False,label='Users emails',help_text="comma seprated list of emails of users to notify when new version integrated",widget=forms.TextInput(attrs={'class':'form-control','size':30}))
    default_server = forms.ModelChoiceField(queryset=Server.objects.all(),empty_label="Select",widget=forms.Select(attrs={"class":"form-control"}),label="Default Server")
    sshKey = forms.ModelChoiceField(queryset=SSHKey.objects.all(), empty_label="Select",label="SSH Key",widget=forms.Select(attrs={"class": "form-control"}))
    default_branch = forms.CharField(label='Default Branch', widget=forms.TextInput(attrs={'class': 'form-control', 'size': 30}))

    def __init__(self, *args, **kwargs):
        super(CIProjectsForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['name'].widget.attrs['readonly'] = True

    def save(self, files, name):
        P = models.CIProject()
        P.name = self.cleaned_data["name"]
        # P.integration_link = self.cleaned_data["integration_link"]
        P.repo = self.cleaned_data["repo"]
        P.repo_link = self.cleaned_data["repo_link"]
        P.repo_type = self.cleaned_data["repo_type"]
        P.working_dir = self.cleaned_data["working_dir"]
        P.sshKey = self.cleaned_data["sshKey"]
        P.default_server = self.cleaned_data["default_server"]
        P.update_style = self.cleaned_data["update_style"]
        P.emailUsers = self.cleaned_data["emailUsers"]
        P.default_branch = self.cleaned_data["default_branch"]
        P.slackchannel = self.cleaned_data["slackch"]

        print("Files is ", files)
        f = files.get('cfile2', '')
        if f != "":
            P.configFile = saveFile(files.get('cfile2', ''), name)
        P.save()

    class Meta:
        model = models.CIProject
        fields = ("name", "repo", "repo_link", "working_dir", "update_style", "default_branch", "default_server", "repo_type", "sshKey", "cfile", "slackch", "emailUsers")


class CloneForm(forms.Form):
    server = forms.ModelChoiceField(queryset=Server.objects.all(), label="Server", required=True, widget=forms.Select(attrs={"class": "form-control"}))


