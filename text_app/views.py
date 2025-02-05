from django.shortcuts import render, get_object_or_404
from db_editor.models import Text, Token, PosTag, Error, ErrorToken, ErrorTag

def show_text(request, text_id=None):
    # Получаем текст по заданному ID или первый текст, если ID не указан
    if text_id is not None:
        text = get_object_or_404(Text, idtext=text_id)
    else:
        text = Text.objects.first()
    
    # Получаем токены для данного текста
    tokens = Token.objects.filter(idsentence__idtext=text.idtext)
    
    # Параметры для выбора разметки
    selected_markup = request.GET.get('markup', 'tagtext')
    
    # Собираем данные для отображения
    token_data = []
    for token in tokens:
        if selected_markup == 'plain':
            pos = None  # Не показываем часть речи в режиме 'plain'
            tagcolor = None
        else:
            pos_tag = token.idpostag
            pos = None
            tagcolor = None
            if pos_tag:
                if selected_markup == 'tagtextrussian':
                    pos = pos_tag.tagtextrussian
                elif selected_markup == 'tagtextabbrev':
                    pos = pos_tag.tagtextabbrev
                else:
                    pos = pos_tag.tagtext
                tagcolor = pos_tag.tagcolor  # Получаем цвет части речи

        token_data.append({
            'token': token.tokentext,
            'pos': pos,
            'tagcolor': tagcolor,  # Передаем цвет
        })
    
    context = {
        'text': text,
        'token_data': token_data,
        'selected_markup': selected_markup,
    }

    return render(request, 'show_text.html', context)

# 4112
def show_error_markup(request, text_id=None): 
    # Получаем текст по заданному ID или первый текст, если ID не указан
    if text_id is not None:
        text = get_object_or_404(Text, idtext=text_id)
    else:
        text = Text.objects.first()

    tokens = Token.objects.filter(idsentence__idtext=text.idtext)

    selected_markup = request.GET.get('markup', 'tagtext')
    
    # Собираем данные для отображения
    token_data = []
    for token in tokens:
        error_tag = None
        error_tag_abbrev = None 
        error_color = None
        error_level = None
        error_correct = None
        error_comment = None
        
        error_token = ErrorToken.objects.filter(idtoken=token.idtoken).first()
        if error_token:
            error = Error.objects.filter(iderror=error_token.iderror.iderror).first()
            if error:
                error_tag_obj = ErrorTag.objects.filter(iderrortag=error.iderrortag.iderrortag).first()
                if error_tag_obj:
                    if selected_markup == 'tagtextrussian':
                        error_tag = error_tag_obj.tagtextrussian
                    elif selected_markup == 'tagtextabbrev':
                        error_tag = error_tag_obj.tagtextabbrev
                    else:
                        error_tag = error_tag_obj.tagtext  
                    error_color = error_tag_obj.tagcolor
                    error_tag_abbrev = error_tag_obj.tagtextabbrev  
                    error_level = error.iderrorlevel.errorlevelname if error.iderrorlevel else 'Не указано'
                    error_correct = error.correct if error.correct else 'Не указано'
                    error_comment = error.comment if error.comment else 'Не указано'

        token_data.append({
            'token': token.tokentext,
            'error_tag': error_tag,
            'error_tag_abbrev': error_tag_abbrev, 
            'error_color': error_color,
            'error_level': error_level,
            'error_correct': error_correct,
            'error_comment': error_comment,
        })
    
    context = {
        'text': text,
        'token_data': token_data,
        'selected_markup': selected_markup,
    }

    return render(request, 'show_error_markup.html', context)

def show_text_markup(request, text_id=None):
    # Получаем текст по заданному ID или первый текст, если ID не указан
    if text_id is not None:
        text = get_object_or_404(Text, idtext=text_id)
    else:
        text = Text.objects.first()

    # Получаем предложения текста
    sentences = text.sentence_set.all()
    sentence_data = []

    # Получаем значение разметки, выбранное пользователем
    selected_markup = request.GET.get('markup', 'tagtext')

    # Формируем данные для разметки по предложениям
    for sentence in sentences:
        # Используем select_related для оптимизации запросов
        tokens = Token.objects.filter(idsentence=sentence).select_related('idpostag')
        
        tokens_data = []
        for token in tokens:
            # Разметка для частей речи (извлекаем все возможные данные)
            pos_tag = None
            pos_tag_russian = None
            pos_tag_abbrev = None
            pos_tag_color = None
            if token.idpostag:
                pos_tag = token.idpostag.tagtext
                pos_tag_russian = token.idpostag.tagtextrussian
                pos_tag_abbrev = token.idpostag.tagtextabbrev
                pos_tag_color = token.idpostag.tagcolor

            # Разметка для ошибок (если есть ошибки для токена)
            error_tag = None
            error_tag_russian = None
            error_tag_abbrev = None
            error_color = None
            error_level = None
            error_correct = None
            error_comment = None
            error_token = token.errortoken_set.first()
            if error_token:
                error = error_token.iderror
                if error:
                    error_tag_obj = error.iderrortag
                    if error_tag_obj:
                        error_tag = error_tag_obj.tagtext
                        error_tag_russian = error_tag_obj.tagtextrussian
                        error_tag_abbrev = error_tag_obj.tagtextabbrev
                        error_color = error_tag_obj.tagcolor
                        error_level = error.iderrorlevel.errorlevelname if error.iderrorlevel else 'Не указано'
                        error_correct = error.correct if error.correct else 'Не указано'
                        error_comment = error.comment if error.comment else 'Не указано'

            # Добавляем информацию о токене и его частях речи, а также ошибки (если есть)
            tokens_data.append({
                'token': token.tokentext,
                'pos_tag': pos_tag,
                'pos_tag_russian': pos_tag_russian,
                'pos_tag_abbrev': pos_tag_abbrev,
                'pos_tag_color': pos_tag_color,
                'error_tag': error_tag,
                'error_tag_russian': error_tag_russian,
                'error_tag_abbrev': error_tag_abbrev,
                'error_color': error_color,
                'error_level': error_level,
                'error_correct': error_correct,
                'error_comment': error_comment,
            })

        # Добавляем данные по предложению
        sentence_data.append({
            'sentence': sentence,
            'tokens': tokens_data,
        })

    # Получаем дополнительную информацию о тексте
    student = text.idstudent
    user = student.iduser  # Получаем объект User
    group = student.idgroup
    academic_year = group.idayear
    text_type = text.idtexttype
    write_place = text.idwriteplace
    write_tool = text.idwritetool

    # Формируем данные для отображения
    context = {
        'text': text,
        'sentence_data': sentence_data,
        'selected_markup': selected_markup,
        'author': f"{user.lastname} {user.firstname}",  # Имя и фамилия автора
        'group': group.groupname,  # Название группы
        'academic_year': academic_year.title,  # Учебный год
        'create_date': text.createdate,  # Дата создания текста
        'write_place': write_place.writeplacename if write_place else 'Не указано',  # Место написания
        'write_tool': write_tool.writetoolname if write_tool else 'Не указано',  # Инструмент написания
        'text_type': text_type.texttypename if text_type else 'Не указано',  # Тип текста
    }

    return render(request, 'show_text_markup.html', context)

def home_view(request):
    return render(request, 'home.html')