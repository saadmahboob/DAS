# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django_extensions.db.fields import UUIDField

#Nosso usuario base
class Usuario(AbstractUser):    
    #Tipo do usuario
    is_admin = models.BooleanField(default=False)
    is_medico = models.BooleanField(default=False)
    is_cliente = models.BooleanField(default=False)
    is_secretaria = models.BooleanField(default=False)

    #Informacoes comuns
    rg = models.CharField(max_length=15)
    cpf = models.CharField(max_length=15, unique=True)

    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=120)

    def __unicode__(self):
        return self.username + ' - ' + self.email
    
    def get_full_name(self):
        return self.first_name+" "+self.last_name

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class Cliente(Usuario):
    #usuario = models.OneToOneField(Usuario, null=True)
    convenio = models.ForeignKey('Convenio')
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __unicode__(self):
        return self.first_name+' '+self.last_name
class Secretaria(Usuario):
    #usuario = models.OneToOneField(Usuario, null=True)
    
    class Meta:
        verbose_name = "Secretaria"
        verbose_name_plural = "Secretarias"

class Medico(Usuario):
    #usuario = models.OneToOneField(Usuario, null=True)
    crm = models.CharField(max_length=16, unique=True)
    duracao_consulta = models.PositiveSmallIntegerField(max_length=15)
    especializacao = models.ForeignKey('Especializacao')

    def json(self):
        medico = {}
        medico['id'] = self.id
        medico['nome'] = self.first_name
        medico['sobrenome'] = self.last_name
        medico['email'] = self.username
        medico['crm'] = self.crm
        medico['duracao_consulta'] = self.duracao_consulta
        #espec = Especializacao.objects.get(id=self.especializacao)
        medico['especializacao'] = self.especializacao.json()
        return medico

    class Meta:
        verbose_name = "Medico"
        verbose_name_plural = "Medicos"

    def __unicode__(self):
        return self.first_name


class Especializacao(models.Model):
    nome = models.CharField(max_length=60, unique=True)

    def __unicode__(self):
        return self.nome

    def json(self):
        e = {}
        e['id'] = self.id
        e['nome'] = self.nome
        return e 

class Horario(models.Model):
    medico = models.ForeignKey('Medico')

    dia = models.PositiveSmallIntegerField(blank=False)
    hora_inicio = models.TimeField(blank=False)
    hora_final = models.TimeField(blank=False)

    def __unicode__(self):
        return self.dia + ': ' + hora_inicio + ' - ' + hora_final


class Convenio(models.Model):
    """docstring for Convenio"""
    cnpj = models.CharField(max_length=16, unique=True)
    razao_social = models.CharField(max_length=80)

    def __unicode__(self):
        return self.razao_social

    def json(self):
        convenio = {}
        convenio['cnpj'] = self.cnpj
        convenio['razao_social'] = self.razao_social
        return convenio

class Consulta(models.Model):
    """docstring for Convenio"""
    id = UUIDField(primary_key=True, auto=True)

    cliente = models.ForeignKey('Cliente')
    medico = models.ForeignKey('Medico')
    data_hora = models.DateTimeField(blank=False)
    checkin = models.BooleanField(default=False)

    def json(self):
        consulta = {}
        consulta['id'] = self.id
        consulta['cliente']   = self.cliente.first_name+' '+self.cliente.last_name
        consulta['medico']    = self.medico.first_name+' '+self.medico.last_name
        consulta['data_hora'] = self.data_hora.strftime('%d/%m/%Y  -  %H:%M')
        consulta['especializacao'] = self.medico.especializacao.nome
        consulta['checkin'] = self.checkin
        return consulta

    def __unicode__(self):
        return self.id