# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from django.http import Http404, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db import *
from django.shortcuts import *
from models import *
from django.shortcuts import redirect
import linecache
import sys
import json


TAMANHO_MINIMO_SENHA = 6

def is_admin(user):
    return user.is_admin or user.is_staff

def is_cliente(user):
    return user.is_cliente

def is_medico(user):
    return user.is_medico

def is_admin_or_medico(user):
    return (user.is_medico or user.is_admin or user.is_staff)

def is_admin_or_cliente(user):
    return (user.is_cliente or user.is_admin or user.is_staff)

def is_medico_or_cliente(user):
    return (user.is_medico or user.is_cliente)

def api_monta_json(obj_json):
    '''
    Função que retorna um objeto JSON
    '''
    return HttpResponse(json.dumps(obj_json, indent=4), content_type="application/json")

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


# Create your views here.

def index(request):
    '''
    Função responsável por retornar a página inicial.
    '''
    context = RequestContext(request)

    if request.method == 'GET':
        return render_to_response('main/index.html', context)
    else:
        return HttpResponse('Método Não Permitido',status=405)

def registrar_cliente(request):
    '''
    Esta função é responsável por registrar um novo cliente.
    
    Esta função aceita pedidos GET e POST

    GET:
        Retorna a página de cadastro

    POST:
        Realiza o cadastro de um novo cliente

    '''
    context = RequestContext(request)

    if request.method == 'GET':
        #Retorna a página de cadastro de cliente
        return render_to_response('main/cliente/cadastro.html', context)

    elif request.method == 'POST':
        #obtem dados do POST
        try:
            nome = request.POST['nome']
            sobrenome = request.POST['sobrenome']
            senha =  request.POST['senha']
            confirmar_senha =  request.POST['confirmar_senha']
            email = request.POST['email']
            telefone = request.POST['telefone']
            endereco = request.POST['endereco']
            cpf = request.POST['cpf']
            rg = request.POST['rg']
        except:
            return HttpResponseBadRequest('<h1>Requisição inválida</h1>')


        erro = False

        if nome is None or nome =='':
            messages.error(request, "Nome é obrigatório!")
            erro = True
        
        if sobrenome is None or sobrenome =='':
            messages.error(request, "Sobrenome é obrigatório!")
        
        if senha is None or senha == '':
            # Define erro
            messages.error(request, 'Senha é obrigatória.')
            erro = True

        elif confirmar_senha is None or confirmar_senha == '':
            # Define erro
            messages.error(request, 'Confirmar Senha é obrigatório.')
            erro = True

        elif senha != confirmar_senha:
            # Define erro
            messages.error(request, 'Senhas diferentes.')
            erro = True

        elif len(senha) < TAMANHO_MINIMO_SENHA:
            # Define erro
            messages.error(request, 'A senha deve ter no mínimo 6 caracteres.')
            erro = True

        if email is None or email =='':
            messages.error(request, "Email é obrigatório!")
            erro = True

        if rg is None or rg =='':
            messages.error(request, "RG é obrigatório!")
            erro = True

        if cpf is None or cpf =='':
            messages.error(request, "CPF é obrigatório!")
            erro = True

        if not erro:
            #Tenta salvar o novo cliente no banco
            try:
                #A operacao deve ser atomica
                with transaction.atomic():
                    #Cria usuario
                    cliente = Cliente.objects.create_user(username=email, first_name=nome, last_name=sobrenome, password=senha)
                  
                    #Insere os campos obrigatorios
                    cliente.rg = rg
                    cliente.cpf = cpf
                    cliente.is_cliente = True

                    #Caso existentes, insere os campos nao obrigatorios
                    if telefone and telefone != '':
                        cliente.telefone = telefone

                    if endereco and endereco != '':
                        cliente.endereco = endereco
   
                    #Da um commit no bd
                    cliente.save()

                messages.info(request, "Cadastro realizado com sucesso!")
            except Exception, e:
                #Para qualquer problema, retorna um erro interno                
                PrintException()
                if 'username' in e.message:
                    messages.error(request, 'Email já cadastrado. Escolha outro email.')
                else:
                    messages.error(request, 'Erro desconhecido ao salvar a especialização.')


        return render_to_response('main/cliente/cadastro.html', context)

    else:

        return HttpResponse('Método Não Permitido',status=405)


@login_required        
def conta(request):
    '''
    Esta função é responsável por gerenciar as informacoes de conta.
    
    Esta função aceita pedidos GET e POST

    GET:
        Retorna a página com informacoes da conta do usuario autenticado.

    POST:
        Salva as alteracoes na conta.

    '''
    # TODO !!!

    return HttpResponse('Não Implementado',status=501)

@login_required        
@user_passes_test(is_admin)
def medicos(request):
    '''
    Esta função é responsável retornar uma lista com todos os medicos registrados.
    
    Esta função aceita apenas pedidos GET 

    '''
    context = RequestContext(request)

    if request.method == 'GET':
        #Obtem todos os medicos do bd
        medicos = [m for m in Medico.objects.all()]

        #Retorna a página de todos os medicos
        return render_to_response('main/medico/todos.html', { 'medicos' : medicos }, context)
    else:

        return HttpResponse('Método Não Permitido',status=405)

@login_required
@user_passes_test(is_admin)
def remover_medico(request, crm):
    '''
    Esta função é responsável por remover as informacoes de conta.
    
    Esta função aceita pedidos  POST

    POST:
        Remove as alteracoes na conta.

    '''    

    context = RequestContext(request)
    print crm

    erro = False
    if request.method == 'POST':
        if crm is None or crm == '':
            messages.error(request, 'Erro na remocao')
            erro = True

        if not erro:
            try:
                with transaction.atomic():
                    Medico.objects.filter(crm=crm).delete()
                    #Retorna a página de todos os medicos
                    messages.info(request, 'Medico removido com sucesso')
                    #return render_to_response('main/medico/remover.html', { 'medicos' : medicos }, context)
                return redirect('/medicos')
            except Exception, e:
                #Para qualquer problema, retorna um erro interno                
                PrintException()
        return HttpResponse('Método Não Permitido',status=405)

@login_required
@user_passes_test(is_admin_or_medico)
def alterar_medico(request, id):

    if request.user.is_medico and (request.user.id != int(id)):
        return HttpResponse('<h1>Proibido</h1>',status=403)

    medico = Medico.objects.get(id=id)

    parametros = {}

    parametros['nome'] = medico.first_name
    parametros['sobrenome'] = medico.last_name
    parametros['email'] = medico.username
    parametros['telefone'] = medico.telefone
    parametros['cpf'] = medico.cpf
    parametros['crm'] = medico.crm
    parametros['rg'] = medico.rg
    parametros['duracao_consulta'] = medico.duracao_consulta       
    parametros['especializacao'] = medico.especializacao.nome
    parametros['id'] = medico.id
    
    # Pegando seu pedido
    context = RequestContext(request)
    if request.method == 'GET':
        return render_to_response('main/medico/editar.html', parametros, context)
    elif request.method == 'POST':
        #obtem dados do POST
        try:
            nome = request.POST['nome']
            sobrenome = request.POST['sobrenome']
            email = request.POST['email']
            telefone = request.POST['telefone']
            endereco = request.POST['endereco']
            rg = request.POST['rg']
            duracao_consulta = request.POST['duracao_consulta']
        except:
            return HttpResponseBadRequest('<h1>Requisição inválida</h1>')

        erro = False

        if nome is None or nome =='':
            messages.error(request, "Nome é obrigatrio!")
            erro = True
        
        if sobrenome is None or sobrenome =='':
            messages.error(request, "Sobrenome é obrigatório!")
        
        if email is None or email =='':
            messages.error(request, "Email é obrigatório!")
            erro = True

        if rg is None or rg =='':
            messages.error(request, "RG é obrigatório!")
            erro = True

        if duracao_consulta is None or duracao_consulta == '':
            messages.error(request, "Duração da Consulta é obrigatório!")
            erro = True

        if not erro:
            #Tenta salvar o novo cliente no banco
            try:
                #A operacao deve ser atomica
                with transaction.atomic():                  
                    medico.first_name = nome
                    medico.last_name = sobrenome
                    medico.username = email
                    medico.duracao_consulta = duracao_consulta

                    #Insere os campos obrigatorios
                    medico.rg = rg

                    #Caso existentes, insere os campos nao obrigatorios
                    if telefone and telefone != '':
                        medico.telefone = telefone

                    if endereco and endereco != '':
                        medico.endereco = endereco
   
                    #Da um commit no bd
                    medico.save()

                messages.info(request, "Atualização realizado com sucesso!")
            except Exception, e:
                #Para qualquer problema, retorna um erro interno                
                PrintException()
                if 'username' in e.message:
                    messages.error(request, 'Email já cadastrado. Escolha outro email.')
                else:
                    messages.error(request, 'Erro desconhecido ao salvar o medico.')

        return render_to_response('main/medico/editar.html', parametros, context)

@login_required
@user_passes_test(is_admin_or_cliente)
def alterar_cliente(request, id):

    if request.user.is_cliente and request.user.id != int(id):
        return HttpResponse('<h1>Proibido</h1>',status=403)

    cliente = Cliente.objects.get(id=id)

    parametros = {}

    parametros['nome'] = cliente.first_name
    parametros['sobrenome'] = cliente.last_name
    parametros['email'] = cliente.username
    parametros['telefone'] = cliente.telefone
    parametros['endereco'] = cliente.endereco
    parametros['rg'] = cliente.rg
    parametros['cpf'] = cliente.cpf
    
    # Pegando seu pedido
    context = RequestContext(request)
    if request.method == 'GET':
        return render_to_response('main/cliente/editar.html', parametros, context)
    elif request.method == 'POST':
        #obtem dados do POST
        try:
            nome = request.POST['nome']
            sobrenome = request.POST['sobrenome']
            email = request.POST['email']
            telefone = request.POST['telefone']
            endereco = request.POST['endereco']
            rg = request.POST['rg']
        except:
            return HttpResponseBadRequest('<h1>Requisição inválida</h1>')


        erro = False

        if nome is None or nome =='':
            messages.error(request, "Nome é obrigatrio!")
            erro = True
        
        if sobrenome is None or sobrenome =='':
            messages.error(request, "Sobrenome é obrigatório!")
        
        if email is None or email =='':
            messages.error(request, "Email é obrigatório!")
            erro = True

        if rg is None or rg =='':
            messages.error(request, "RG é obrigatório!")
            erro = True

        if not erro:
            #Tenta salvar o novo cliente no banco
            try:
                #A operacao deve ser atomica
                with transaction.atomic():                  
                    cliente.first_name = nome
                    cliente.last_name = sobrenome
                    cliente.username = email

                    #Insere os campos obrigatorios
                    cliente.rg = rg

                    #Caso existentes, insere os campos nao obrigatorios
                    if telefone and telefone != '':
                        cliente.telefone = telefone

                    if endereco and endereco != '':
                        cliente.endereco = endereco
   
                    #Da um commit no bd
                    cliente.save()

                messages.info(request, "Atualização realizada com sucesso!")
            except Exception, e:
                #Para qualquer problema, retorna um erro interno                
                PrintException()
                if 'username' in e.message:
                    messages.error(request, 'Email já cadastrado. Escolha outro email.')
                else:
                    messages.error(request, 'Erro desconhecido ao salvar o cliente.')

        return render_to_response('main/cliente/editar.html', parametros, context)


@login_required        
@user_passes_test(is_admin)
def registrar_medico(request):
    '''
    Esta função é responsável por registrar um novo médico.
    
    Esta função aceita pedidos GET e POST

    GET:
        Retorna a página de cadastro

    POST:
        Realiza o cadastro de um novo médico

    '''
    context = RequestContext(request)

    #Obtem as especializacoes
    parametros = {'especializacoes' : Especializacao.objects.all()}

    if request.method == 'GET':
        #Retorna a página de cadastro de cliente
        return render_to_response('main/medico/cadastro.html',parametros, context)

    elif request.method == 'POST':

        try:
            #obtem dados do POST
            nome = request.POST['nome']
            sobrenome = request.POST['sobrenome']
            senha =  request.POST['senha']
            confirmar_senha =  request.POST['confirmar_senha']
            email = request.POST['email']
            telefone = request.POST['telefone']
            endereco = request.POST['endereco']
            cpf = request.POST['cpf']
            rg = request.POST['rg']
            crm = request.POST['crm']
            duracao_consulta = request.POST['duracao_consulta']
            especializacao = request.POST['especializacao']
        except:
            return HttpResponseBadRequest('<h1>Requisição inválida</h1>')

        parametros['nome'] = nome
        parametros['sobrenome'] = sobrenome
        parametros['email'] = email
        parametros['telefone'] = telefone
        parametros['cpf'] = cpf
        parametros['crm'] = crm
        parametros['rg'] = rg
        parametros['duracao_consulta'] = duracao_consulta     
        parametros['especializacao'] = especializacao

        erro = False

        if nome is None or nome =='':
            messages.error(request, "Nome é obrigatrio!")
            erro = True
        
        if sobrenome is None or sobrenome =='':
            messages.error(request, "Sobrenome é obrigatório!")
        
        if senha is None or senha == '':
            # Define erro
            messages.error(request, 'Senha é obrigatória.')
            erro = True

        elif confirmar_senha is None or confirmar_senha == '':
            # Define erro
            messages.error(request, 'Confirmar Senha é obrigatório.')
            erro = True

        elif senha != confirmar_senha:
            # Define erro
            messages.error(request, 'Senhas diferentes.')
            erro = True

        elif len(senha) < TAMANHO_MINIMO_SENHA:
            # Define erro
            messages.error(request, 'A senha deve ter no mínimo 6 caracteres.')
            erro = True

        if email is None or email =='':
            messages.error(request, "Email é obrigatório!")
            erro = True

        if rg is None or rg =='':
            messages.error(request, "RG é obrigatório!")
            erro = True

        if cpf is None or cpf =='':
            messages.error(request, "CPF é obrigatório!")
            erro = True

        if crm is None or crm =='':
            messages.error(request, "CRM é obrigatório!")
            erro = True

        if duracao_consulta is None or duracao_consulta == '':
            messages.error(request, "Duração da Consulta é obrigatório!")
            erro = True

        if especializacao is None or especializacao == '':
            messages.error(request, "Especialização é obrigatório!")
            erro = True
        else:
            #Tenta obter a especializacao
            try:
                espec = Especializacao.objects.get(id=especializacao)
            except:
                messages.error(request, "Especialização invalida!")
                erro = True

        if not erro:
            #Tenta salvar o novo cliente no banco
            try:
                #A operacao deve ser atomica
                with transaction.atomic():
                    #Cria usuario
                    medico = Medico.objects.create_user(username=email, first_name=nome, last_name=sobrenome, password=senha, duracao_consulta=duracao_consulta, especializacao=espec)
                  
                    #Insere os campos obrigatorios
                    medico.rg = rg
                    medico.cpf = cpf
                    medico.crm = crm
                    medico.is_medico = True

                    #Caso existentes, insere os campos nao obrigatorios
                    if telefone and telefone != '':
                        medico.telefone = telefone

                    if endereco and endereco != '':
                        medico.endereco = endereco
   
                    #Da um commit no bd
                    medico.save()

                messages.info(request, "Cadastro realizado com sucesso!")
            except Exception, e:
                #Para qualquer problema, retorna um erro interno                
                PrintException()
                if 'username' in e.message:
                    messages.error(request, 'Email já cadastrado. Escolha outro email.')
                else:
                    messages.error(request, 'Erro desconhecido ao salvar o medico.')


        return render_to_response('main/medico/cadastro.html',parametros, context)

    else:

        return HttpResponse('Método Não Permitido',status=405)

@login_required        
@user_passes_test(is_admin)
def especializacoes(request):
    '''
    Esta função é responsável mostrar todas as especializacoes.
    
    Esta função aceita apenas pedidos GET

    '''

    context = RequestContext(request)

    if request.method == 'GET':
        #Obtem todas as especialozacoes
        especializacoes =  [e for e in Especializacao.objects.all()]
        #Retorna a página de tdas as espocializacoes
        return render_to_response('main/especializacao/todas.html',{'especializacoes' : especializacoes}, context)
    else:
        return HttpResponse('Método Não Permitido',status=405)

@login_required
@user_passes_test(is_admin)
def remover_especializacao(request, id):
    '''
    Esta função é responsável mostrar todas as especializacoes.
    
    Esta função aceita apenas pedidos POST

    '''
    
    context = RequestContext(request)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                Especializacao.objects.filter(id=id).delete()
        except Exception, e:
            messages.error(request, 'Erro ao remover especializacao')
            #Para qualquer problema, retorna um erro interno                
            PrintException()

        messages.info(request, 'Especializacao removida com sucesso')
        return redirect('/especializacoes')
    else:
        return HttpResponse('Metodo nao permitido', status=405)

@login_required
@user_passes_test(is_admin)
def alterar_especializacao(request, id):
    '''
    Esta função é responsável mostrar todas as especializacoes.
    
    Esta função aceita apenas pedidos GET e POST

    '''
    
    context = RequestContext(request)
    try:
        especializacao = Especializacao.objects.get(id=id)
    except:
        return HttpResponseNotFound('<h1>Page not found</h1>')

    parametros = {}
    parametros['id'] = especializacao.id
    parametros['nome'] = especializacao.nome

    if request.method == 'GET':
        return render_to_response('main/especializacao/alterar.html', parametros, context)
    elif request.method == 'POST':
        
        error = False
        if especializacao.id is None or especializacao.id == '':
            messages.error(request, 'Erro ID')
            error = True

        if especializacao.nome is None or especializacao.nome == '':
            messages.error(request, 'Nome digitado invalido')
            error = True

        novo_nome = request.POST['nome']

        if novo_nome is None or novo_nome =='':
            messages.error(request, 'Novo nome invalido')
            error = True

        if not error:   
            try:
                with transaction.atomic():
                    especializacao.nome = novo_nome
                    especializacao.save()
                    messages.info(request, 'Especializacao alterada com sucesso')
            except Exception, e:
                messages.error(request, 'Erro ao alterar especializacao')
                #Para qualquer problema, retorna um erro interno                
                PrintException()
        return redirect('/especializacoes')
    else:
        return HttpResponse('Metodo nao permitido', status=405)
@login_required        
@user_passes_test(is_admin)
def registrar_especializacao(request):
    '''
    Esta função é responsável por registrar uma nova especialização.
    
    Esta função aceita pedidos GET e POST

    GET:
        Retorna a página de cadastro

    POST:
        Realiza o cadastro de uma nova especialização

    '''

    context = RequestContext(request)

    if request.method == 'GET':
        #Retorna a página de cadastro de cliente
        return render_to_response('main/especializacao/cadastro.html', context)

    elif request.method == 'POST':

        #Obtem o parametro do POST
        espec_nome = request.POST['especializacao']
        erro = False

        if espec_nome is None or espec_nome == '':
            # Define erro
            messages.error(request, 'Nome da especialização inválido.')
            erro = True

        if not erro:
            #Tenta salvar a especializacao no banco
            try:
                #A operacao deve ser atomica
                with transaction.atomic():
                    espec = Especializacao(nome=espec_nome)
                    espec.save()

                messages.info(request, "Cadastro da especialização '{}' realizado com sucesso!".format(espec_nome))
            except Exception, e:
                #Para qualquer problema, retorna um erro interno                
                PrintException()
                if 'unique' in e.message:
                    messages.error(request, 'Especialização já existente.')
                else:
                    messages.error(request, 'Erro desconhecido ao salvar a especialização.')

        return render_to_response('main/especializacao/cadastro.html', context)
    else:
        return HttpResponse('Método Não Permitido',status=405)


@login_required        
@user_passes_test(is_admin)
def convenios(request):
    '''
    Esta função é responsável mostrar todos os convenios.
    
    Esta função aceita apenas pedidos GET

    '''

    context = RequestContext(request)

    if request.method == 'GET':
        #Obtem todas as especialozacoes
        convenios =  [c.json() for c in Convenio.objects.all()]
        #Retorna a página de tdas as espocializacoes
        return render_to_response('main/convenio/todos.html',{'convenios' : convenios}, context)
    else:
        return HttpResponse('Método Não Permitido',status=405)

@login_required
@user_passes_test(is_admin)
def remover_convenio(request, cnpj):
    '''
    Esta função e responsável remover um convenio

    Esta funcao aceita apenas pedidos POST

    '''
    try:
        context = RequestContext(request)

        print cnpj

        if request.method == 'POST':
            Convenio.objects.filter(cnpj=cnpj).delete()
            #Obtem todos os medicos do bd
            #medicos = [m.json() for m in Medico.objects.all()]

            #Retorna a página de todos os medicos
            messages.info(request, 'Convenio removido com sucesso')
            return redirect('/convenios')

            #return render_to_response('main/medico/remover.html', { 'medicos' : medicos }, context)
    except Exception, e:
        #Para qualquer problema, retorna um erro interno                
        PrintException()

    return HttpResponse('Método Não Permitido',status=405)

@login_required
@user_passes_test(is_admin)
def alterar_convenio(request, cnpj):
    '''
    Esta funcao e responsavel por editar um convenio

    Esta funcao aceita pedidos GET e POST
    '''

    context = RequestContext(request)

    print cnpj

    convenio = Convenio.objects.get(cnpj=cnpj)

    if request.method == 'GET':
        parametros = {}
        parametros['cnpj'] = convenio.cnpj
        parametros['razao_social'] = convenio.razao_social
        return render_to_response('main/convenio/alterar.html', parametros, context)
    elif request.method == 'POST': 
        novo_razao_social = request.POST['razao_social']

        error = False
        if novo_razao_social is None or novo_razao_social == '':
            messages.error(request, 'Nova razao social invalida')
            error = True

        if not error:
            try:
                with transaction.atomic():
                    convenio.razao_social = novo_razao_social
                    convenio.save()
                    messages.info(request, 'Convenio alterado com sucesso!')
            except Exception, e:
                messages.error(request, 'Erro ao alterar convenio')
                #Para qualquer problema, retorna um erro interno                
                PrintException()

        return redirect('/convenios')
    else:
        return HttpResponse('Método Não Permitido',status=405)


@login_required        
@user_passes_test(is_admin)
def registrar_convenio(request):
    '''
    Esta função é responsável por registrar uma nova especialização.
    
    Esta função aceita pedidos GET e POST

    GET:
        Retorna a página de cadastro

    POST:
        Realiza o cadastro de um novo convenio

    '''

    context = RequestContext(request)

    if request.method == 'GET':
        #Retorna a página de cadastro de cliente
        return render_to_response('main/convenio/cadastro.html', context)

    elif request.method == 'POST':

        #Obtem o parametro do POST
        cnpj = request.POST['cnpj']
        razao_social = request.POST['razao_social']

        erro = False

        if razao_social is None or razao_social == '':
            # Define erro
            messages.error(request, 'Razão social é obrigatório.')
            erro = True

        if cnpj is None or cnpj == '':
            # Define erro
            messages.error(request, 'CNPJ é obrigatório.')
            erro = True

        if not erro:
            #Tenta salvar a especializacao no banco
            try:
                #A operacao deve ser atomica
                with transaction.atomic():
                    convenio = Convenio(cnpj=cnpj, razao_social=razao_social)
                    convenio.save()

                messages.info(request, "Cadastro do convênio realizado com sucesso!")
            except Exception, e:
                #Para qualquer problema, retorna um erro interno                
                PrintException()
                if 'unique' in e.message:
                    messages.error(request, 'Convênio já existente.')
                else:
                    messages.error(request, 'Erro desconhecido ao salvar o convênio.')

        return render_to_response('main/convenio/cadastro.html', context)
    else:
        return HttpResponse('Método Não Permitido',status=405)

@login_required        
@user_passes_test(is_medico)
def horarios(request):
    '''
    Esta função é responsável mostrar todos os horarios do medico autenticado.
    
    Esta função aceita apenas pedidos GET

    '''
    context = RequestContext(request)
    medico = Medico.objects.get(id=request.user.id)


    if request.method == 'GET':
        #Obtem todas as especialozacoes
        horarios =  [h.json() for h in Horario.objects.filter(medico=medico)]
        #Retorna a página de tdas as espocializacoes
        return render_to_response('main/medico/horarios.html',{'horarios' : horarios}, context)
    else:
        return HttpResponse('Método Não Permitido',status=405)

@login_required        
@user_passes_test(is_medico)
def registrar_horario(request):
    '''
    Esta função é responsável por registrar um novo horario.
    
    Esta função aceita pedidos GET e POST

    GET:
        Retorna a página de cadastro

    POST:
        Realiza o cadastro de um novo horario.

    '''
    medico = Medico.objects.get(id=request.user.id)

    context = RequestContext(request)

    if request.method == 'GET':
        #Retorna a página de cadastro de horario
        return render_to_response('main/medico/adiciona_horario.html', context)

    elif request.method == 'POST':

        #Obtem o parametro do POST
        dia = request.POST['dia']
        hora_inicio = request.POST['hora_inicio']
        hora_final = request.POST['hora_final']

        erro = False

        if dia is None or dia == '':
            # Define erro
            messages.error(request, 'Dia é obrigatório.')
            erro = True

        if hora_inicio is None or hora_inicio == '':
            # Define erro
            messages.error(request, 'Horario de inicio é obrigatório.')
            erro = True

        if hora_final is None or hora_final == '':
            # Define erro
            messages.error(request, 'Horario de termino é obrigatório.')
            erro = True

        if not erro:
            #Tenta salvar a especializacao no banco
            try:
                #A operacao deve ser atomica
                with transaction.atomic():
                    horario = Horario(medico=medico, dia=dia, hora_inicio=hora_inicio, hora_final=hora_final)
                    horario.save()

                messages.info(request, "Cadastro de horario realizado com sucesso!")
            except Exception, e:
                #Para qualquer problema, retorna um erro interno                
                PrintException()
                messages.error(request, 'Erro desconhecido ao salvar o convênio.')

        return render_to_response('main/medico/adiciona_horario.html', context)
    else:
        return HttpResponse('Método Não Permitido',status=405)

    return HttpResponse('Não Implementado',status=501)

@login_required        
@user_passes_test(is_medico)
def alterar_horario(request):
    '''
    Esta função é responsável por alterar um horario.
    
    Esta função aceita pedidos GET e POST

    GET:
        Retorna a página de cadastro

    POST:
        Realiza a alteracao de um horario.

    '''
    # TODO !!!

    return HttpResponse('Não Implementado',status=501)

@login_required        
@user_passes_test(is_medico_or_cliente)
def consultas(request):
    '''
    Esta função é responsável mostrar todos as consultas do medico ou cliente autenticado.
    
    Esta função aceita apenas pedidos GET

    '''
    # TODO !!!

    return HttpResponse('Não Implementado',status=501)

@login_required        
#@user_passes_test(is_cliente)
def registrar_consulta(request):
    '''
    Esta função é responsável por registrar uma nova consulta.
    
    Esta função aceita pedidos GET e POST

    GET:
        Retorna a página de cadastro

    POST:
        Realiza o cadastro de uma nova consulta.

    '''
    # TODO !!!
    context = RequestContext(request)
    if request.method == 'GET':
        #Obter todos as especializações do bd
        especializacoes = [espec for espec in Especializacao.objects.all()]

        return render_to_response('main/consultas/cadastro.html',{'especializacoes':especializacoes}, context)

@login_required
@user_passes_test(is_admin)
def qrCodeScan(request):
    '''
    qrCode scanner
    '''
    context = RequestContext(request)
    return render_to_response('main/qrCodeScanner/index.html', context)

@login_required
@user_passes_test(is_admin)
def searchCode(request):
    context = RequestContext(request)

    if request.method == 'POST':
        entrada = request.POST['qrCode']
        try:

            #Testar entrada
            print(entrada)
            
            #Buscar no banco
            #u = Usuario.objects.get(nome=entrada)    
            return api_monta_json({'response':entrada})
          
        except Exception, e:
            return api_monta_json({'response':'Erro na leitura'})
    else:
        return api_monta_json({'response':'Método não permitido'})

@login_required
def listar_medico_espec(request):
    context = RequestContext(request)

    if request.method == 'POST':
        espec = request.POST['especId']
        especializacao = Especializacao.objects.get(id=espec)
        #print(especializacao.nome)
        medicos = [m.first_name for m in Medico.objects.filter(especializacao=especializacao)]
        return HttpResponse(json.dumps({'response': medicos}), content_type="application/json")
    else:        
        return api_monta_json({'response':'Método não permitido'})
