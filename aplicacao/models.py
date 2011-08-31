#coding: utf-8

from django.db import models
from django.forms import ModelForm, ChoiceField, RadioSelect
from django import forms
from django.db import connection, transaction


class AgendarVisita(models.Model):
    nome_da_escola = models.CharField(max_length=50)
    telefone_de_contato = models.CharField(max_length=50)
    email = models.EmailField()
    quantidade_de_visitantes = models.IntegerField()
    responsavel_escola = models.CharField(max_length=50)
    data = models.CharField(max_length=50)
    horario = models.CharField(max_length=50)
    horario1 = models.CharField(max_length=50, blank=True)
    responsavel1 = models.CharField(max_length=50) 
    responsavel2 = models.CharField(max_length=50, null=True, blank=True) 
    responsavel3 = models.CharField(max_length=50, null=True, blank=True) 
    responsavel4 = models.CharField(max_length=50, null=True, blank=True) 
    responsavel5 = models.CharField(max_length=50, null=True, blank=True) 
    responsavel6 = models.CharField(max_length=50, null=True, blank=True)    


class AgendarVisitaModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AgendarVisitaModelForm, self).__init__(*args, **kwargs)

        nome = ['nome_da_escola']
        for n in nome:
            self.fields[n].widget=forms.TextInput(attrs={'size':'40', 'onkeyup':'maiuscula(this.value);', 'maxlength':'30'})

        responsavel_escola = ['responsavel_escola']
        for r in responsavel_escola:
            self.fields[r].widget=forms.TextInput(attrs={'size':'40', 'onkeyup':'maiuscula(this.value);', 'maxlength':'29'})

        responsavel = ['responsavel1']
        for r in responsavel:
            self.fields[r].widget=forms.TextInput(attrs={'size':'40', 'onkeyup':'maiuscula(this.value);', 'maxlength':'29'})
            
        responsavel = ['responsavel2']
        for r in responsavel:
            self.fields[r].widget=forms.TextInput(attrs={'size':'40', 'onkeyup':'maiuscula(this.value);', 'maxlength':'29'})
            
        responsavel = ['responsavel3']
        for r in responsavel:
            self.fields[r].widget=forms.TextInput(attrs={'size':'40', 'onkeyup':'maiuscula(this.value);', 'maxlength':'29'})
            
        responsavel = ['responsavel4']
        for r in responsavel:
            self.fields[r].widget=forms.TextInput(attrs={'size':'40', 'onkeyup':'maiuscula(this.value);', 'maxlength':'29'})
            
        responsavel = ['responsavel5']
        for r in responsavel:
            self.fields[r].widget=forms.TextInput(attrs={'size':'40', 'onkeyup':'maiuscula(this.value);', 'maxlength':'29'})
            
        responsavel = ['responsavel6']
        for r in responsavel:
            self.fields[r].widget=forms.TextInput(attrs={'size':'40', 'onkeyup':'maiuscula(this.value);', 'maxlength':'29'})

        telefone = ['telefone_de_contato']
        for tel in telefone:
            self.fields[tel].widget=forms.TextInput(attrs={'size':'40'})

        email = ['email']
        for e in email:
            self.fields[e].widget=forms.TextInput(attrs={'size':'40', 'onkeyup':'minuscula(this.value);', 'maxlength':'30'})

        visitantes = ['quantidade_de_visitantes']
        for v in visitantes:
            self.fields[v].widget=forms.TextInput(attrs={'size':'40', 'onkeyup':'num(this);', 'maxlength':'3'})

        lista_data = ['data']
        for dia in lista_data:
            self.fields[dia].widget = forms.HiddenInput()

        lista_horario1 = ['horario1']
        for hora1 in lista_horario1:
            data = '08/09/2011'
            self.fields[hora1].widget = forms.RadioSelect(attrs={'onclick':'data.value = "08/09/2011"; this.name = "horario", document.getElementByName(horario).checked = false;'}, choices=
(('14:00', '14:00 - Disponível '+str(160 - self.conta_horario('14:00', data)) + ' vaga(s)'), ('15:00', '15:00 - Disponível '+str(160 - self.conta_horario('15:00', data)) +  ' vaga(s)'), ('16:00', '16:00 - Disponível ' +str(160 - self.conta_horario('16:00', data)) + ' vaga(s)'), ('17:00', '17:00 - Disponível '+str(160 - self.conta_horario('17:00', data)) +  ' vaga(s)'), ('18:00', '18:00 - Disponível '+str(160 - self.conta_horario('18:00', data)) + ' vaga(s)'), ('19:00', '19:00 - Disponível '+str(160 - self.conta_horario('19:00', data)) + ' vaga(s)')))
        lista_horario = ['horario']
        for hora in lista_horario:
            data = '09/09/2011'
            self.fields[hora].widget = forms.RadioSelect(attrs={'onclick':'data.value = "09/09/2011"'}, choices=
(('14:00', '14:00 - Disponível '+str(160 - self.conta_horario('14:00', data)) + ' vaga(s)'), ('15:00', '15:00 - Disponível '+str(160 - self.conta_horario('15:00', data)) +  ' vaga(s)'), ('16:00', '16:00 - Disponível ' +str(160 - self.conta_horario('16:00', data)) + ' vaga(s)'), ('17:00', '17:00 - Disponível '+str(160 - self.conta_horario('17:00', data)) +  ' vaga(s)'), ('18:00', '18:00 - Disponível '+str(160 - self.conta_horario('18:00', data)) + ' vaga(s)'), ('19:00', '19:00 - Disponível '+str(160 - self.conta_horario('19:00', data)) + ' vaga(s)')))
        
    def conta_horario(self, horario, data):
        cursor = connection.cursor()
        cursor.execute("SELECT sum(quantidade_de_visitantes) from aplicacao_agendarvisita where horario = %s and data = %s;", [horario, data])
        row = cursor.fetchone()
        row = str(row)
        if row == '(None,)':
            return 0
        else:            
            row = row.split("(")[1]
            row = row.split("L,)")[0]
            return int(row) 

    class Meta:
        model = AgendarVisita	
       
