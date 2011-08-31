# coding: utf-8 

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from visitas.aplicacao.models import AgendarVisita, AgendarVisitaModelForm
from django.core.urlresolvers import reverse
from django.core.mail import send_mail, get_connection, EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from django.core.urlresolvers import reverse
from cStringIO import StringIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction

#pagina principal
def index(request):
	return render_to_response('index.html', {'user':request.user})

#agendamento de visita
@login_required
def agendar_visita(request):
    i = []
    f = AgendarVisitaModelForm()
    
    #validação do formulario com a quantidade de visitantes
    if request.GET:
    
        #se quantidade de visitantes for igual a em branco, quantidade recebe zero, senão recebe o valor passado pelo usuário
        if str(request.GET['quantidade_de_visitantes']) == '':
            quantidade = 0
        else:
            quantidade = int(request.GET['quantidade_de_visitantes'])
            
        #se a quantidade for maior que zero e menor ou igual a 160, o contador i é implementado para gerar o os campos de responsáveia pela visita, onde a cada 30 visitantes, é necessário um responsavel.
        if quantidade > 0 and quantidade <= 160:
            i = quantidade/30
            if (i < 1) and (i >= 0):
                i = 1
            elif (i >= 1) and (quantidade % 30 != 0):
                i += 1
                
            #retorna o template com o restante do formulário, com as informações do usuario logado 'user', o contador 'i', para a geração dos campos de responsáveis
            return render_to_response('agendar_visita.html', {'form': f, 'user': request.user, 'i': i, 'visitantes': request.GET['quantidade_de_visitantes']})
            
        #retorna o formulario com a mensagem de erro
        else:        
            erro = True
            if quantidade == 0:
                if str(request.GET['quantidade_de_visitantes']) == '':
                    texto_erro = 'Campo Obrigatório.'
                elif str(request.GET['quantidade_de_visitantes']) == '0':
                    texto_erro = 'Quantidade de visitantes não pode ser zero.'
            elif quantidade > 160:
                texto_erro = 'Quantidade de visitantes não pode ser superior a 160 participantes.'
            return render_to_response('agendar.html', {'form':f, 'user':request.user, 'erro':erro, 'texto_erro':texto_erro})
    #validação do formulario de agendamento
    elif request.POST:
        
        #geração do contador de responsaveis, que será chamado, caso as informações não sejam válidas (erro)
        if str(request.POST['quantidade_de_visitantes']) == '':
            quantidade = 0
        else:
            quantidade = int(request.POST['quantidade_de_visitantes'])
        if quantidade > 0 and quantidade <= 160:
            i = quantidade/30
            if (i < 1) and (i >= 0):
                i = 1
            elif (i >= 1) and (quantidade % 30 != 0):
                i += 1
         
        #f recebe o valor de todos os campos do formulario
        f = AgendarVisitaModelForm(request.POST)
        
        #valida o campo quantidade de visitantes e passa o valor 0 se campo estiver em branco; se o campo estiver preenchido corretamente passa o valor informado pelo usuário 
        if request.POST['quantidade_de_visitantes'] == '':
            quantidade_visitantes = 0
        else:
            quantidade_visitantes = int(request.POST['quantidade_de_visitantes'])
        
        #se todos os campos obrigatórios foram preenchidos
        if f.is_valid():
        
            #verifica se existe a quantidade de vagas solicitadas pelo usuário
            visitantes = f.conta_horario(request.POST['horario'], request.POST['data'])+ quantidade_visitantes
            
            #se o total de visitantes for menor ou igual a 160, salva os dados no banco de dados, envia e-mail para o solicitante e para o responsavel pelo evento e retorna a página de confirmação para usuário imprimir os dados referente ao agendamento da visita
            if visitantes <= 160:
            
                #salva o formulario
                f.save()
                
                #dados do email: titulo (subject) e mensagem
                subject = "Confirmação: Visitas de Escolas - Semana do Saber Fazer Saber"
                mensagem = ('Olá ' + str(request.POST['responsavel_escola']) + ', a visita da ' + str(request.POST['nome_da_escola']) + ' na Semana do Saber Fazer Saber foi agendada para o dia ' + str(request.POST['data']) + ' às ' + str(request.POST['horario']) + ', no Auditório Miguel Ramalho.')
                
                #remetente da mensagem
                from_email = '' #colocar o email
                
                #login e senha do remetente da mensagem, neste caso foi configurado os serviços do gmail; caso queira trocar o serviço de e-mail, deve trocar a conexão no arquivo "settings.py" do projeto
                connection = get_connection(username = '', password ='') #colocar o e-mail e a senha
                
                #e-mail do responsavel pelo evento
                email_gerencia = '' #colocar e-mail do responsavel
                
                #agrupa as informações do e-mail
                send_email = EmailMessage(subject, mensagem , from_email, [request.POST['email'], email_gerencia], connection = connection)
                send_email.content_subtype = "html"
                
                #envia o e-mail para o solicitante da visita "request.POST['email']", com cópia para o responsavel pelo evento
                send_email.send()
                
                #retorna o template de confirmação
                return HttpResponseRedirect(reverse('visitas.aplicacao.views.sucesso'))
                
            #se o total de visitantes for superior a 160, retorna o template de formulario, informando a impossibilidade de agendamento da visita para a data e hora escolhida
            elif visitantes > 160:
                erro_vagas = True
                texto_erro = "Não há " + str(request.POST['quantidade_de_visitantes']) + " vagas disponíveis para o dia " + str(request.POST['data']) + " às " + str(request.POST['horario']) + ". Por favor, escolha outra data e horário."
                return render_to_response('agendar_visita.html',{'form':f, 'erro_vagas':erro_vagas, 'texto_erro':texto_erro, 'user':request.user, 'i':i, 'visitantes': request.POST['quantidade_de_visitantes'] })
                
        #se algum campo obrigatório não foi informado, retorna o template do formulario, informando e erro
        else:
            erro=True
            return render_to_response('agendar_visita.html',{'form':f, 'erro':erro, 'user':request.user, 'i':i, 'visitantes': request.POST['quantidade_de_visitantes'] })
            
    #se o metodo não for GET (não foi submetido o formulario com a quantidade de visitantes), nem POST (não foi submetido o formulario de agendamento de visitas, retorna o formulario para preenchimento da quantidade de visitantes, começando o agendamento da visita)
    else:
        f = AgendarVisitaModelForm()
        return render_to_response('agendar.html', {'form':f, 'user': request.user})

#pagina de confirmação após submeter o formulario
@login_required
def sucesso(request):
	return render_to_response('sucesso.html', {'user':request.user})

#relatorio de visitas
@login_required
def relatorio(request):

    #restringe o acesso ao relatório aos usuários gerencia e admin
    if request.user.username == 'admin' or request.user.username == 'gerencia':
    
        #cria as propriedades do pdf
        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=visitas.pdf'
        doc = SimpleDocTemplate(response, pagesize = (1000.00, 800.00))
        elements = []
        
        #cria um paragrafo para adicionar a logo da instituição
        styles=getSampleStyleSheet()
        logo = '<img src="/home/dtic/visitas/aplicacao/media/images/logo.png"/> <br><br>'
        elements.append(Paragraph(logo, styles["Normal"]))
        #cria um paragrafo para adicionar o título do relatório
        ptext = '<font size=15> <b> Agendamento de Visitas - Semana do Saber Fazer Saber <b> </font> <br><br><br><br>'
        elements.append(Paragraph(ptext, styles["Normal"]))    
        
        # cria consulta a base de dados, ordenado por data e horário da visita
        data = []        
        visita = AgendarVisita.objects.order_by('data', 'horario')
        
        #cria e adiciona a tabela com os dados da consulta
        for v in visita:
            data.append([Paragraph("<b>ESCOLA</b>", styles["Normal"]), Paragraph("<b>QUANTIDADE DE VISITANTES</b>", styles["Normal"]), Paragraph("<b>DATA E HORÁRIO DA VISITA</b>", styles["Normal"])])
            data.append([v.nome_da_escola, v.quantidade_de_visitantes, str(v.data) + ' às ' + str(v.horario)])
            data.append([Paragraph("<b>RESPONSÁVEL PELA ESCOLA</b>", styles["Normal"]), Paragraph("<b>TELEFONE</b>", styles["Normal"]), Paragraph("<b>E-MAIL</b>", styles["Normal"])])
            data.append([v.responsavel_escola, v.telefone_de_contato, v.email])
            data.append([Paragraph("<b>RESPONSÁVEL PELA VISITA</b>", styles["Normal"])])
            data.append([Paragraph("<b>RESPONSÁVEL PELO GRUPO 1</b>", styles["Normal"]), Paragraph("<b>RESPONSÁVEL PELO GRUPO 2</b>", styles["Normal"]), Paragraph("<b>RESPONSÁVEL PELO GRUPO 3</b>", styles["Normal"])])
            data.append([v.responsavel1, v.responsavel2, v.responsavel3])
            data.append([Paragraph("<b>RESPONSÁVEL PELO GRUPO 4</b>", styles["Normal"]), Paragraph("<b>RESPONSÁVEL PELO GRUPO 5</b>", styles["Normal"]), Paragraph("<b>RESPONSÁVEL PELO GRUPO 6</b>", styles["Normal"])])
            data.append([v.responsavel4, v.responsavel5, v.responsavel6])
            t = Table(data)
            t.setStyle(TableStyle([('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 1.00, colors.black),
                       ]))
            elements.append(t)
            data = []
            elements.append(Paragraph("<br><br>", styles["Normal"]))
        cursor = connection.cursor()
        cursor.execute("SELECT sum(quantidade_de_visitantes) from aplicacao_agendarvisita")
        row = cursor.fetchone()
        row = str(row)
        if row == '(None,)':
            row = '0'
        else:
            row = row.split("(")[1]
            row = row.split("L,)")[0]
        elements.append(Paragraph("<b>Total de Visitantes: " + str(row) + "</b>", styles["Normal"]))
        
        #adiciona o titulo e a tabela ao pdf
        doc.build(elements)
        return response
    else:
    
        #se o usuario não tiver permissão, retorna mensagem de erro, como template permissao.html 
        return render_to_response('permissao.html', {'user':request.user})

@login_required
def consulta(request):

    #restringe o acesso aos usuários gerencia e admin
    if request.user.username == 'admin' or request.user.username == 'gerencia':
    
        #cria a consulta de acordo com o filtro e mostra no template visitas.html
        if request.POST:
            if request.POST['status'] == 'data':  
                titulo = "Consulta de Visitas - " + str(request.POST['data'])
                visita = AgendarVisita.objects.filter(data = request.POST['data']).order_by('horario')
                contador = visita.count()
            elif request.POST['status'] == 'escola':
                titulo = "Consulta de Visitas - '" + str(request.POST['escola']) + "'"
                visita = AgendarVisita.objects.filter(nome_da_escola__icontains = request.POST['escola'])
                contador = visita.count()
            elif request.POST['status'] == 'todos':
                titulo = "Consulta Geral de Visitas"
                visita = AgendarVisita.objects.order_by('data', 'horario')
                contador = visita.count()
            elif request.POST['status'] == '':
                titulo = "Consulta de Visitas - Filtro não Especificado"
                visita = []
                contador = 0        
            return render_to_response('visitas.html', {'visita':visita, 'user':request.user, 'titulo':titulo, 'contador':contador})
            
        #mostra a pagina de consulta
        else:
            return render_to_response('consulta.html', {'user':request.user})
            
    #se o usuario não tiver permissão, retorna mensagem de erro, como template permissao.html
    else:
        return render_to_response('permissao.html', {'user':request.user})

