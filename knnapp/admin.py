from django.contrib import admin
from . import models
from django.http import HttpResponse
import csv
import json
import os
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from datetime import datetime


def update_names_decrypted(queryset, namedecrypt):
    for student, decrypted_names in zip(queryset, namedecrypt):
        student.namefather = decrypted_names.get('namefather', student.namefather)
        student.telfather = decrypted_names.get('telfather', student.telfather)
        student.namemother = decrypted_names.get('namemother', student.namemother)
        student.telmother = decrypted_names.get('telmother', student.telmother)

        student.save()

def decrypt_names(modeladmin, request, queryset):
    namedecrypt = []

    with open('ZVFITUJ1VWVfQnd2NW16blo5T.txt', 'r') as file:
        criptografados = json.load(file)

        for student in queryset:
            for criptografado in criptografados:
                if student.namefather in criptografado:
                    target = criptografado[student.namefather]
                    namedecrypt.append({'namefather': target})

                elif student.telfather in criptografado:
                    target = criptografado[student.telfather]
                    namedecrypt.append({'telfather': target})

                if student.namemother in criptografado:
                    target = criptografado[student.namemother]
                    namedecrypt.append({'namemother': target})

                elif student.telmother in criptografado:
                    target = criptografado[student.telmother]
                    namedecrypt.append({'telmother': target})

    update_names_decrypted(queryset, namedecrypt)
    return HttpResponseRedirect(request.get_full_path())

def update_names_crypted(queryset, namecrypt):
    for student, crypted_name in zip(queryset, namecrypt):
        student.namefather = crypted_name.get('namefather', student.namefather)
        student.telfather = crypted_name.get('telfather', student.telfather)
        student.namemother = crypted_name.get('namemother', student.namemother)
        student.telmother = crypted_name.get('telmother', student.telmother)

        student.save()

def crypt_names(modeladmin, request, queryset):
    namecrypt = []

    with open('ZVFITUJ1VWVfQnd2NW16blo5T.txt', 'r') as file:
        criptografados = json.load(file)

        for student in queryset:
            for criptografado in criptografados:
                for chave, valor in criptografado.items():
                    if valor == student.namefather:
                        namecrypt.append({'namefather': chave})
                    if valor == student.telfather:
                        namecrypt.append({'telfather': chave})
                    if valor == student.namemother:
                        namecrypt.append({'namemother': chave})
                    if valor == student.telmother:
                        namecrypt.append({'telmother': chave})                                              
    print(namecrypt)
    update_names_crypted(queryset, namecrypt)
    return HttpResponseRedirect(request.get_full_path())

def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(['Matrícula do aluno', 'Nome do aluno', 'Gênero', 'Data de nascimento', 'Curso', 'KNN', 'Naive Bayes', 'Árvore de decisão', 'MLP'])

    for student in queryset:
        writer.writerow([student.registration, student.name, student.genre, student.birth_date, student.career, student.risk_knn, student.risk_skl, student.risk_tree, student.risk_mlp])
        export_to_csv.short_description = "Exportar selecionados para CSV" 

    return response

@admin.register(models.Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ['name', 'career','namefather','telfather','namemother','telmother','risk_knn','risk_skl','risk_tree','risk_mlp']
    list_filter = ("career",)
    search_fields = ("name", "career")
    ordering = ("name",)
    actions = [export_to_csv,decrypt_names,crypt_names]
    decrypt_names.short_description = "Descriptografar"
    crypt_names.short_description = "Criptografar"
    export_to_csv.short_description = "Exportar CSV"

    change_list_template = 'admin/students_change_list.html'

@admin.register(models.Regulations)
class RegulationsAdmin(admin.ModelAdmin):
    list_display = ['description', 'regulation']
    search_fields = ("description", "regulation",)
    ordering = ['description', ]


@admin.register(models.Measures)
class MeasuresAdmin(admin.ModelAdmin):
    list_display = ['name', 'classification']
    list_filter = ('classification', )


@admin.register(models.Violations)
class ViolationsAdmin(admin.ModelAdmin):
    list_display = ['student', 'date_event']
    list_filter = ('date_event', )
    ordering = ['student', ]


@admin.register(models.Recommendations)
class RecommendationsAdmin(admin.ModelAdmin):
    list_display = ['method_field','superior_field','student_name','student_registration','student_career','student_email','student_father_name','student_father_tel','student_mother_name','student_mother_tel','measure']
    list_filter = ('measure', )
    ordering = ['student', ]

    def student_name(self, obj):
        return obj.student.name

    student_name.short_description = 'Nome do Estudante'

    def student_registration(self, obj):
        return obj.student.registration

    student_registration.short_description = 'Matricula'

    def student_career(self, obj):
        return obj.student.career

    student_career.short_description = 'Curso'

    def student_email(self, obj):
        return obj.student.email
    
    student_email.short_description = 'Email Responsável'

    def student_father_name(self, obj):
        return obj.student.namefather

    student_father_name.short_description = 'Nome do Pai'

    def student_father_tel(self, obj):
        return obj.student.telfather

    student_father_tel.short_description = 'Telefone Pai'

    def student_mother_name(self, obj):
        return obj.student.namemother

    student_mother_name.short_description = 'Nome da Mãe'

    def student_mother_tel(self, obj):
        return obj.student.telmother

    student_mother_tel.short_description = 'Telefone Mãe'

    def method_field(self, obj):
        if obj.measure and obj.measure.name == 'Advertência':
            return 'Reunião com Pedagogo\Psicólogo (a)'
        elif obj.measure and obj.measure.name == 'Advertência Escrita':
            return 'Reunião com Pais\Pedagogo\Psicólogo\Coordenador DAE (a)'
        elif obj.measure and obj.measure.name == 'Horas Orientadas':
            return 'Reunião com Pais\Pedagogo\Psicólogo\Coordenador Residencia (a)'
        elif obj.measure and obj.measure.name == 'Suspensão':
            return 'Reunião com Pais\Conselho\Pedagogo\Psicólogo\Coordenador DAE\Coordenador Residencia (a) '
        elif obj.measure and obj.measure.name == 'Perda Residência':
            return 'Reunião com Pais\Conselho Disciplinar\Coordenador Residencia (a)'
        elif obj.measure and obj.measure.name == 'Expulsão':
            return 'Reunião com Pais\Coordenadores\Diretor (a)'
        
    method_field.short_description = 'Metódo'

    def superior_field(self, obj):
        regulation = models.Regulations.objects.first()  
        if obj.measure and obj.measure.name == 'Advertência':
            psychologist = regulation.psychologist if regulation else ''
            pedagogue = regulation.pedagogue if regulation else ''
            self.send_invitation_email_superiors([psychologist, pedagogue],['Psicólogo', 'Pedagogo'], obj)
            self.send_invitation_email_students([obj.student.email], obj)
            return f'Psicólogo(a): {psychologist}   /   Pedagogo(a): {pedagogue}' if psychologist or pedagogue else 'Sem Informacoes'
        elif obj.measure and obj.measure.name == 'Advertência Escrita':
            psychologist = regulation.psychologist if regulation else ''
            pedagogue = regulation.pedagogue if regulation else ''
            cordres = regulation.coordinatorres if regulation else ''
            self.send_invitation_email_superiors([psychologist, pedagogue, cordres],['Psicólogo', 'Pedagogo', 'Coordenador'], obj)
            self.send_invitation_email_students([obj.student.email], obj)
            return f'Psicólogo(a): {psychologist}   /   Pedagogo(a): {pedagogue}   /   Coordenador Residencia(a): {cordres}' if psychologist or pedagogue or cordres else 'Sem Informações'
        elif obj.measure and obj.measure.name == 'Horas Orientadas':
            psychologist = regulation.psychologist if regulation else ''
            pedagogue = regulation.pedagogue if regulation else ''
            corddae = regulation.coordinatordae if regulation else ''
            self.send_invitation_email_superiors([psychologist, pedagogue, corddae],['Psicólogo', 'Pedagogo', 'Coordenador'], obj)
            self.send_invitation_email_students([obj.student.email], obj)
            return f'Psicólogo(a): {psychologist}   /   Pedagogo(a): {pedagogue}   /   Coordenador Dae(a): {corddae}' if psychologist or pedagogue or corddae else 'Sem Informações'
        elif obj.measure and obj.measure.name == 'Suspensão':
            psychologist = regulation.psychologist if regulation else ''
            pedagogue = regulation.pedagogue if regulation else ''
            corddae = regulation.coordinatordae if regulation else ''
            cordres = regulation.coordinatorres if regulation else ''
            self.send_invitation_email_superiors([psychologist, pedagogue, corddae, cordres],['Psicólogo', 'Pedagogo', 'Coordenador', 'Coordenador'], obj)
            self.send_invitation_email_students([obj.student.email], obj)
            return f'Psicólogo(a): {psychologist}   /   Pedagogo(a): {pedagogue}   /   Coordenador Dae(a): {corddae}    /   Coordenador Residencia(a): {cordres}' if psychologist or pedagogue or cordres  or corddae else 'Sem Informações'
        elif obj.measure and obj.measure.name == 'Perda Residência':
            psychologist = regulation.psychologist if regulation else ''
            pedagogue = regulation.pedagogue if regulation else ''
            corddae = regulation.coordinatordae if regulation else ''
            cordres = regulation.coordinatorres if regulation else ''
            self.send_invitation_email_superiors([psychologist, pedagogue, corddae, cordres],['Psicólogo', 'Pedagogo', 'Coordenador', 'Coordenador'], obj)
            self.send_invitation_email_students([obj.student.email], obj)
            return f'Psicólogo(a): {psychologist}   /   Pedagogo(a): {pedagogue}   /   Coordenador Dae(a): {corddae}    /   Coordenador Residencia(a): {cordres}' if psychologist or pedagogue or cordres  or corddae else 'Sem Informações'
        elif obj.measure and obj.measure.name == 'Expulsão':
            corddae = regulation.coordinatordae if regulation else ''
            cordres = regulation.coordinatorres if regulation else ''
            diretor = regulation.director if regulation else ''
            self.send_invitation_email_superiors([corddae, cordres, diretor],['Coordenador', 'Coordenador', 'Diretor'], obj)
            self.send_invitation_email_students([obj.student.email], obj)
            return f'Diretor(a): {diretor}    /    Coordenador Dae(a): {corddae}   /   Coordenador Residencia(a): {cordres}' if diretor or cordres or corddae else 'Sem Informações'

    superior_field.short_description = 'Superiores'

    def send_email_with_check(self,email,student):
        email_log_file = "register_email.txt"
        if not os.path.exists(email_log_file):
            open(email_log_file, 'w').close()

        with open(email_log_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if email in line and student in line:
                    return True
        return False
                    

    def send_invitation_email_superiors(self, emails, ids, obj):
        email_log_file = "register_email.txt"
        subject = 'Convocação do Departamento de Assistência Estudantil (DAE)'
        message_template = \
        """
        Prezado {name} (a),

        A equipe do Departamento de Assistência Estudantil (DAE) convoca-o(a) a comparecer ao nosso setor para tratar de assuntos pertinentes à ocorrência {ocorrencia}, registrada na Ata n° {ata}.

        Destacamos a importância de sua presença, pois isso é crucial para a resolução de questões de seu interesse. Ressaltamos que é dever do estudante atender às convocações da instituição, em conformidade com as normas vigentes.

        Sua colaboração é fundamental. Contamos com sua presença e nos colocamos à disposição para eventuais esclarecimentos.

        Atenciosamente, Equipe do DAE
        """

        for email, id in zip(emails, ids):
            if not self.send_email_with_check(email,obj.student.name):
                if email:
                    message = message_template.format \
                    (
                        name=id,
                        ocorrencia=obj.measure.name,
                        ata=obj.measure.ata
                    )
                    send_mail(subject, message, 'SEU EMAIL', [email], fail_silently=False)  # ADICIONAR O MESMO EMAIL DO SETTINGS.PY AQUI
                    
                    with open(email_log_file, 'a') as file:
                        file.write(f"{datetime.now()} - 'Superior':{email} - 'Estudante':{obj.student.name}\n")
            else:
                pass
    
    
    def send_invitation_email_students(self, emails, obj):
        email_log_file = "register_email.txt"
        subject = 'Convocação do Departamento de Assistência Estudantil (DAE)'
        message_template = \
        """
        Prezado(a) {name},

        A equipe do Departamento de Assistência Estudantil (DAE) convoca-o(a) a comparecer ao nosso setor para tratar de assuntos pertinentes à ocorrência {ocorrencia}, registrada na Ata n° {ata}.

        Destacamos a importância de sua presença, pois isso é crucial para a resolução de questões de seu interesse. Ressaltamos que é dever do estudante atender às convocações da instituição, em conformidade com as normas vigentes.

        Sua colaboração é fundamental. Contamos com sua presença e nos colocamos à disposição para eventuais esclarecimentos.

        Atenciosamente, Equipe do DAE
        """
        for email in emails:
            if not self.send_email_with_check(email,obj.student.name):
                if email:
                    message = message_template.format(
                        name=f"{obj.student.namefather} e {obj.student.namemother}",
                        ocorrencia=obj.measure.name,
                        ata=obj.measure.ata
                    )
                    send_mail(subject, message, 'SEU EMAIL', [email], fail_silently=False) # ADICIONAR O MESMO EMAIL DO SETTINGS.PY AQUI
                    with open(email_log_file, 'a') as file:
                        file.write(f"{datetime.now()} - 'Responsavel':{email} - 'Estudante':{obj.student.name}\n")
            else:
                pass
