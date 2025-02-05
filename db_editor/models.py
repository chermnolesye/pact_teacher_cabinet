from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        """Создание и сохранение обычного пользователя"""
        if not login:
            raise ValueError('The Login field must be set')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        """Создание и сохранение суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(login, password, **extra_fields)

class Rights(models.Model):
    idrights = models.AutoField(primary_key=True)
    rightsname = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'tblrights'

    def __str__(self):
        return self.rightsname
    
class User(AbstractBaseUser, PermissionsMixin):
    iduser = models.AutoField(primary_key=True)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    lastname = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.BooleanField(null=True, blank=True)  # 0 или 1
    idrights = models.ForeignKey(Rights, on_delete=models.CASCADE, db_column='idrights', default=1)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['lastname', 'firstname']

    class Meta:
        db_table = 'tbluser'  

    def __str__(self):
        return self.login

class AcademicYear(models.Model):
    idayear = models.AutoField(primary_key=True) 
    title = models.CharField(max_length=10)

    class Meta:
        db_table = 'tblacademicyear'  

    def __str__(self):
        return self.title

class Emotion(models.Model):
    idemotion = models.AutoField(primary_key=True)  
    emotionname = models.CharField(max_length=100, unique=True)  

    class Meta:
        db_table = 'tblemotion' 

    def __str__(self):
        return self.emotionname  

class Error(models.Model):
    iderror = models.AutoField(primary_key=True)  
    correct = models.TextField(blank=True, null=True)  
    comment = models.TextField(blank=True, null=True) 
    changedate = models.DateField(blank=True, null=True)  
    iderrorlevel = models.ForeignKey('ErrorLevel', on_delete=models.CASCADE, blank=True, null=True, db_column='iderrorlevel')  
    idreason = models.ForeignKey('Reason', on_delete=models.CASCADE, blank=True, null=True, db_column='idreason')  
    iderrortag = models.ForeignKey('ErrorTag', on_delete=models.CASCADE, db_column='iderrortag')  

    class Meta:
        db_table = 'tblerror' 

    def __str__(self):
        return f"Error {self.iderror}"

class ErrorLevel(models.Model):
    iderrorlevel = models.AutoField(primary_key=True)
    errorlevelname = models.CharField(max_length=255)
    errorlevelabbrev = models.CharField(max_length=30, blank=True, null=True)
    errorlevelvalue = models.SmallIntegerField()

    class Meta:
        db_table = 'tblerrorlevel'

    def __str__(self):
        return self.errorlevelname
    
class ErrorTag(models.Model):
    iderrortag = models.AutoField(primary_key=True)
    tagtext = models.TextField()
    tagtextrussian = models.TextField()
    tagtextabbrev = models.TextField()
    tagcolor = models.CharField(max_length=7)
    idtagparent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, db_column='idtagparent')

    class Meta:
        db_table = 'tblerrortag'

    def __str__(self):
        return self.tagtext

class ErrorToken(models.Model):
    iderrortoken = models.AutoField(primary_key=True)
    position = models.IntegerField(blank=True, null=True)
    iderror = models.ForeignKey('Error', on_delete=models.CASCADE, db_column='iderror')
    idtoken = models.ForeignKey('Token', on_delete=models.CASCADE, db_column='idtoken')

    class Meta:
        db_table = 'tblerrortoken'

    def __str__(self):
        return f"ErrorToken {self.iderrortoken}"

class Group(models.Model):
    idgroup = models.AutoField(primary_key=True)
    groupname = models.CharField(max_length=10)
    studycourse = models.SmallIntegerField()
    idayear = models.ForeignKey('AcademicYear', on_delete=models.CASCADE, db_column='idayear')

    class Meta:
        db_table = 'tblgroup'

    def __str__(self):
        return self.groupname

class PosTag(models.Model):
    idpostag = models.AutoField(primary_key=True)
    tagtext = models.TextField()
    tagtextrussian = models.TextField()
    tagtextabbrev = models.TextField()
    tagcolor = models.CharField(max_length=7)

    class Meta:
        db_table = 'tblpostag'

    def __str__(self):
        return self.tagtext

class Reason(models.Model):
    idreason = models.AutoField(primary_key=True)
    reasonname = models.CharField(max_length=255)
    reasonabbrev = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'tblreason'

    def __str__(self):
        return self.reasonname
    
class Sentence(models.Model):
    idsentence = models.AutoField(primary_key=True)
    sentensetext = models.TextField()
    ordernumber = models.IntegerField()
    idtext = models.ForeignKey('Text', on_delete=models.CASCADE, db_column='idtext')

    class Meta:
        db_table = 'tblsentence'

    def __str__(self):
        return f"Sentence {self.idsentence} (Order: {self.ordernumber})"

class Student(models.Model):
    idstudent = models.AutoField(primary_key=True)
    idgroup = models.ForeignKey('Group', on_delete=models.CASCADE, db_column='idgroup')
    iduser = models.ForeignKey('User', on_delete=models.CASCADE, db_column='iduser')

    class Meta:
        db_table = 'tblstudent'

    def __str__(self):
        return f"Student {self.idstudent}"

class Text(models.Model):
    idtext = models.AutoField(primary_key=True)
    header = models.CharField(max_length=255)
    text = models.TextField()
    idstudent = models.ForeignKey('Student', on_delete=models.CASCADE, db_column='idstudent')
    createdate = models.DateField(null=True, blank=True)
    modifieddate = models.DateField(null=True, blank=True)
    educationlevel = models.IntegerField(null=True, blank=True)
    idtexttype = models.ForeignKey('TextType', on_delete=models.CASCADE, db_column='idtexttype', null=True, blank=True)
    idwriteplace = models.ForeignKey('WritePlace', on_delete=models.CASCADE, db_column='idwriteplace', null=True, blank=True)
    idwritetool = models.ForeignKey('WriteTool', on_delete=models.CASCADE, db_column='idwritetool', null=True, blank=True)
    idemotion = models.ForeignKey('Emotion', on_delete=models.CASCADE, db_column='idemotion', null=True, blank=True)
    textgrade = models.IntegerField(null=True, blank=True)
    completeness = models.IntegerField(null=True, blank=True)
    structure = models.IntegerField(null=True, blank=True)
    coherence = models.IntegerField(null=True, blank=True)
    selfrating = models.IntegerField(null=True, blank=True)
    selfassesment = models.IntegerField(null=True, blank=True)
    poscheckflag = models.BooleanField(null=True, blank=True)
    errorcheckflag = models.BooleanField(null=True, blank=True)
    poscheckdate = models.DateField(null=True, blank=True)
    errorcheckdate = models.DateField(null=True, blank=True)
    iduserteacher = models.ForeignKey('User', on_delete=models.CASCADE, db_column='iduserteacher', null=True, blank=True, related_name='teacher_texts')
    idusererrorcheck = models.ForeignKey('User', on_delete=models.CASCADE, db_column='idusererrorcheck', null=True, blank=True, related_name='errorcheck_texts')
    iduserposcheck = models.ForeignKey('User', on_delete=models.CASCADE, db_column='iduserposcheck', null=True, blank=True, related_name='poscheck_texts')

    class Meta:
        db_table = 'tbltext'

    def __str__(self):
        return self.header

class TextType(models.Model):
    idtexttype = models.AutoField(primary_key=True)
    texttypename = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'tbltexttype'

    def __str__(self):
        return self.texttypename

class Token(models.Model):
    idtoken = models.AutoField(primary_key=True)
    tokentext = models.TextField()  # longtext соответствует TextField
    tokenordernumber = models.IntegerField()
    idsentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name='tokens', db_column='idsentence')  # Используем существующую колонку
    idpostag = models.ForeignKey(PosTag, on_delete=models.CASCADE, null=True, blank=True, db_column='idpostag')  # Используем существующую колонку

    class Meta:
        db_table = 'tbltoken'
        indexes = [
            models.Index(fields=['idsentence']),
            models.Index(fields=['idpostag']),
        ]

    def __str__(self):
        return f"Token {self.idtoken}: {self.tokentext}"


class WritePlace(models.Model):
    idwriteplace = models.AutoField(primary_key=True)
    writeplacename = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'tblwriteplace'

    def __str__(self):
        return self.writeplacename
    
class WriteTool(models.Model):
    idwritetool = models.AutoField(primary_key=True)
    writetoolname = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'tblwritetool'

    def __str__(self):
        return self.writetoolname
