from django.db import models

career_choices = (
    ('TAGRO', 'TAGRO'),
    ('TMSI', 'TMSI'),
)

genre_choices = (
    ('', 'Não informado'),
    ('M', 'MASCULINO'),
    ('F', 'FEMININO'),
    ('O', 'OUTRO'),
)

measures_choices = (
    ('L', 'Leve'),
    ('M', 'Média'),
    ('G', 'Grave'),
)

warnings_choices = (
    ('Advertência', 'Advertência'),
    ('Advertência Escrita', 'Advertência Escrita'),
    ('Horas Orientadas', 'Horas Orientadas'),
    ('Suspensão', 'Suspensão'),
    ('Perda Residência', 'Perda Residência'),
    ('Expulsão', 'Expulsão'),
)



class Students(models.Model):
    registration = models.CharField(max_length=20, verbose_name='Matrícula do aluno')
    name = models.CharField(max_length=100, verbose_name='Nome do aluno')
    namefather = models.CharField(max_length=100,null=True, verbose_name='Nome do Pai')
    telfather = models.CharField(max_length=100,null=True, verbose_name='Telefone do Pai')
    namemother = models.CharField(max_length=100,null=True, verbose_name='Nome da Mãe')
    telmother = models.CharField(max_length=100,null=True, verbose_name='Telefone da Mãe')
    email = models.CharField(max_length=100,null=True, verbose_name='Email Responsável')
    genre = models.CharField(max_length=50, choices=genre_choices, null=True, verbose_name="Gênero")
    birth_date = models.DateField(null=True, verbose_name='Data de nascimento')
    career = models.CharField(max_length=20, choices=career_choices, null=True, verbose_name='Curso')
    risk_knn = models.DecimalField(decimal_places=2, max_digits=10, default=0.0, verbose_name='KNN - K-Nearest Neighbour')
    risk_skl = models.DecimalField(decimal_places=2, max_digits=10, default=0.0, verbose_name='SKL - Naive Bayes')
    risk_tree = models.DecimalField(decimal_places=2, max_digits=10, default=0.0, verbose_name='Árvore de decisão')
    risk_mlp = models.DecimalField(decimal_places=2, max_digits=10, default=0.0, verbose_name='MLP - Multi Layer Perceptron')


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Estudante'
        verbose_name_plural = 'Estudantes'

class Regulations(models.Model):
    regulation = models.CharField(max_length=50, blank=True, verbose_name='Regulamentação')
    description = models.CharField(max_length=255, blank=True, verbose_name='Descrição da regra')
    psychologist = models.CharField(max_length=100, blank=True, verbose_name='Psicóloga')
    pedagogue = models.CharField(max_length=100, blank=True, verbose_name='Pedagogo')
    coordinatordae = models.CharField(max_length=100, blank=True, verbose_name='Coordenador DAE')
    coordinatorres = models.CharField(max_length=100, blank=True, verbose_name='Coordenador Residencia')
    director = models.CharField(max_length=100, blank=True, verbose_name='Diretor')


    def __str__(self):
        return self.description

    class Meta:
        verbose_name = 'Regulamento'
        verbose_name_plural = 'Regulamento'


class Measures(models.Model):
    name = models.CharField(max_length=100, choices=warnings_choices, verbose_name='Descrição')
    classification = models.CharField(max_length=1, choices=measures_choices, verbose_name='Classificação')
    regulation = models.ForeignKey(Regulations, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Regulamento')
    ata = models.CharField(max_length=50, blank=True, verbose_name='Registro Ata')
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Medida Disciplinar'
        verbose_name_plural = 'Medidas Disciplinares'


class Violations(models.Model):
    student = models.ForeignKey(Students, null=True, default=None, on_delete=models.PROTECT, verbose_name='Estudante')
    regulation = models.ForeignKey(Regulations, on_delete=models.PROTECT, verbose_name='Infração')
    description = models.TextField(max_length=500, verbose_name='Descrição da ocorrência')
    measure = models.ForeignKey(Measures, null=True, on_delete=models.PROTECT, verbose_name='Medida disciplinar')
    complement = models.CharField(max_length=255, null=True, verbose_name='Complemento da medida disciplinar')
    date_event = models.DateField(verbose_name='Data do evento')

    def __str__(self):
        return str(self.student)

    class Meta:
        verbose_name = 'Violação'
        verbose_name_plural = 'Violações'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.measure and self.measure.name == 'Advertência' or self.measure.name == 'Advertência Escrita' or self.measure.name == 'Horas Orientadas' or self.measure.name == 'Suspensão' or self.measure.name == 'Perda Residência' or self.measure.name == 'Expulsão':
            if not Recommendations.objects.filter(student=self.student, measure=self.measure).exists():
                Recommendations.objects.create(student=self.student, measure=self.measure)


class Recommendations(models.Model):
    student = models.ForeignKey(Students, null=True, default=None, on_delete=models.PROTECT, verbose_name='Estudante')
    measure = models.ForeignKey(Measures, null=True, on_delete=models.PROTECT, verbose_name='Medida disciplinar')
    regulations = models.ForeignKey(Regulations, null=True, on_delete=models.PROTECT, verbose_name='Regulamentos')
    
    def __str__(self):
        return str(self.student)

    class Meta:
        verbose_name = 'Recomendação'
        verbose_name_plural = 'Recomendações'