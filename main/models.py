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

    #Informacoes comuns
    rg = models.CharField(max_length=15)
    cpf = models.CharField(max_length=15)

    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=120)

    def __unicode__(self):
        return self.username + ' - ' + self.email

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class Cliente(Usuario):
    #usuario = models.OneToOneField(Usuario, null=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

class Medico(Usuario):
    #usuario = models.OneToOneField(Usuario, null=True)
    crm = models.CharField(max_length=16)
    duracao_consulta = models.PositiveSmallIntegerField(max_length=15)

    class Meta:
        verbose_name = "Medico"
        verbose_name_plural = "Medicos"

class Especializacao(models.Model):
    nome = models.CharField(max_length=60, unique=True)

    def __unicode__(self):
        return self.nome

class Horario(models.Model):
    medico = models.ForeignKey('Medico')

    dia = models.PositiveSmallIntegerField(blank=False)
    hora_inicio = models.TimeField(blank=False)
    hora_final = models.TimeField(blank=False)

    def __unicode__(self):
        return self.dia + ': ' + hora_inicio + ' - ' + hora_final

class Convenio(models.Model):
    """docstring for Convenio"""
    cnpj = models.CharField(max_length=16, primary_key=True)
    razao_social = models.CharField(max_length=80)

    def __unicode__(self):
        return self.razao_social

class Consulta(models.Model):
    """docstring for Convenio"""
    id = UUIDField(primary_key=True, auto=True)

    cliente = models.ForeignKey('Cliente')
    medico = models.ForeignKey('Medico')
    data_hora = models.DateTimeField(blank=False)
    checkin = models.BooleanField(default=False)

    def __unicode__(self):
        return self.cliente + ' ' + self.medico 
