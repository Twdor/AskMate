from datetime import datetime
import data_manager
import os
import uuid
import bcrypt


PAGE_IDX, TAG_IDX = 1, 3
TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_new_user_id():
    user_id = str(uuid.uuid4()).split('-')[4]
    return user_id


def get_user_id(user_name):
    return data_manager.get_user_id(user_name)['id'] if user_name else user_name


def is_already_register(request):
    return True if request.form['username'] in [email['user_name'] for email in data_manager.get_user_names()] \
        else False


def are_valid_credentials(request):
    if is_already_register(request):
        user_password = data_manager.get_user_pass(request.form['username'])['password']
        return True if is_valid_password(request.form['password'], user_password) else False
    return False


def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def is_valid_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


def has_question_privilege(session, question_id):
    if 'username' in session:
        current_user_id = data_manager.get_user_id(session['username']).get('id')
        question_owner_id = data_manager.get_user_id_by_question_id(question_id).get('user_id')
        return question_owner_id == current_user_id


def has_answer_privilege(session, answer_id):
    if 'username' in session:
        current_user_id = data_manager.get_user_id(session['username']).get('id')
        answer_owner_id = data_manager.get_user_id_by_answer_id(answer_id)
        return current_user_id == answer_owner_id


def has_comment_privilege(session, comment_id):
    if 'username' in session:
        current_user_id = data_manager.get_user_id(session['username']).get('id')
        comment_owner_id = data_manager.get_user_id_by_comment_id(comment_id)
        return current_user_id == comment_owner_id


def get_formatted_dict(dictionary):
    dictionary["message"] = dictionary["message"].replace("\n", "<br>")
    return dictionary


def get_formatted_dicts(dicts):
    for d in dicts:
        get_formatted_dict(d)
    return dicts


def get_style(style_mode):
    if style_mode == 'day':
        return 'whitesmoke', 'black'
    else:
        return 'black', 'whitesmoke'


def saved_img(request):
    """Saves image and returns file name"""
    generated_file_name = None
    if request.files["img"]:
        file = request.files["img"]
        path = os.environ.get('VIRTUAL_ENV').replace('venv', 'static/images/')
        generated_file_name = f"{uuid.uuid4()}-{file.filename}"
        file.save(f"{path}{generated_file_name}")
        generated_file_name = f"/static/images/{generated_file_name}"
    return generated_file_name


def get_page_id(page):
    page_id = page.split('-')[PAGE_IDX]
    return page_id


def delete_img(files_path):
    for path in files_path:
        abs_file_path = f"{os.environ.get('VIRTUAL_ENV').replace('/venv', '')}{path.get('image')}"
        if os.path.exists(abs_file_path):
            os.remove(abs_file_path)


def add_and_redirect(page, request, user_name=None):
    page_id = get_page_id(page)
    user_id = get_user_id(user_name)

    if page == 'add-question':
        add_question(request, user_id)
        page_id = data_manager.get_new_question_id()['new_id']

    if page.endswith('new-answer'):
        add_answer(page_id, request, user_id)

    if page.endswith('new-comment'):
        redirect = add_comment_and_redirect(page, page_id, request, user_id)
        return redirect

    if page.endswith('new-tag'):
        add_tag(page_id, request)

    return f"/question/{page_id}"


def add_user(request):
    data_manager.add_user((get_new_user_id(), request.form['username'], TIME, hash_password(request.form['password'])))


def add_tag(page_id, request):
    all_tags, question_tags, question_tags_string = get_tags(page_id)
    if 'tag' in request.form.keys():
        if not request.form['tag'] in [d['name'] for d in question_tags]:
            data_manager.add_tag_to_question(request.form['tag'], page_id)
    else:
        if not request.form['new_tag'] in [d['name'] for d in question_tags]:
            data_manager.add_tag(request.form['new_tag'])
            data_manager.add_tag_to_question(request.form['new_tag'], page_id)


def add_comment_and_redirect(page, page_id, request, user_id):
    if 'answer' in page:
        question_id = data_manager.get_question_id_by_answer_id(page_id).get("question_id")
        new_comment = (None, page_id, user_id, request.form['message'], TIME, None)
        data_manager.add_comment(new_comment)
        return f"/question/{question_id}#{page_id}"

    else:
        new_comment = (page_id, None, user_id, request.form['message'], TIME, None)
        data_manager.add_comment(new_comment)
        return f"/question/{page_id}"


def add_answer(page_id, request, user_id):
    file_name = saved_img(request)
    new_answer = (TIME, 0, page_id, user_id, request.form['message'], file_name)
    data_manager.add_answer(new_answer)


def add_question(request, user_id):
    file_name = saved_img(request)
    new_question = (TIME, 0, 0, user_id, request.form['title'], request.form["message"], file_name)
    data_manager.add_question(new_question)


def get_tags(page_id):
    all_tags, question_tags = data_manager.get_all_tags(), data_manager.get_question_tags(page_id)
    question_tags_string = ''
    for value in question_tags:
        question_tags_string += value['name'] + ' '

    return all_tags, question_tags, question_tags_string


def edit_and_redirect(page, request):
    page_id = get_page_id(page)

    if 'question' in page:
        update_question(page_id, request)
        return f"/question/{page_id}"

    if 'answer' in page:
        question_id = data_manager.get_question_id_by_answer_id(page_id)['question_id']
        update_answer(page_id, request)
        return f"/question/{question_id}#{page_id}"

    if 'comment' in page:
        page = update_comment_and_redirect(page_id, request)
        return page


def update_question(page_id, request):
    delete_img(data_manager.get_question_img(page_id)) if request.files['img'] else None
    file_name = saved_img(request) if request.files['img'] \
        else data_manager.get_question_img(page_id)[0]['image']
    data_manager.update_question(page_id, request.form['title'], request.form["message"], file_name)


def update_answer(page_id, request):
    delete_img(data_manager.get_answer_img(page_id)) if request.files['img'] else None
    file_name = saved_img(request) if request.files['img'] else data_manager.get_answer_img(page_id)[0]['image']
    data_manager.update_answer(page_id, TIME, request.form['message'], file_name)


def update_comment_and_redirect(page_id, request):
    edited_count = data_manager.get_comment_edited_count(page_id)['edited_count']
    edited_count = 1 if edited_count is None else edited_count + 1
    data_manager.update_comment(page_id, request.form['message'], TIME, edited_count)
    question_id = data_manager.get_question_id_by_comment_id(page_id)['question_id']
    if question_id is None:
        answer_id = data_manager.get_answer_id_by_comment_id(page_id)['answer_id']
        question_id = data_manager.get_question_id_by_answer_id(answer_id)['question_id']
        return f"/question/{question_id}#{answer_id}"

    return f"/question/{question_id}#{page_id}"


def delete_and_redirect(page):
    page_id = get_page_id(page)
    if 'question' in page and 'tag' not in page:
        delete_question(page_id)
        return '/'

    if 'question' in page and 'tag' in page:
        delete_tag(page, page_id)
        return f"/question/{page_id}"

    if 'answer' in page:
        question_id = data_manager.get_question_id_by_answer_id(page_id).get('question_id')
        delete_answer(page_id)
        return f"/question/{question_id}"

    if 'comments' in page:
        page = delete_comment_and_redirect(page_id)
        return page


def delete_question(page_id):
    images_related_to_question \
        = data_manager.get_question_img(page_id) + data_manager.get_answers_img_by_question_id(page_id)
    delete_img(images_related_to_question)
    data_manager.delete_question(page_id)


def delete_tag(page, page_id):
    tag_id = page.split('-')[TAG_IDX]
    data_manager.delete_tag_from_question(page_id, tag_id)


def delete_answer(page_id):
    delete_img(data_manager.get_answer_img(page_id))
    data_manager.delete_answer(page_id)


def delete_comment_and_redirect(page_id):
    question_id = data_manager.get_question_id_by_comment_id(page_id).get('question_id')
    if not question_id:
        answer_id = data_manager.get_answer_id_by_comment_id(page_id).get('answer_id')
        question_id = data_manager.get_question_id_by_answer_id(answer_id).get('question_id')
        data_manager.delete_comment(page_id)
        return f"/question/{question_id}#{answer_id}"

    data_manager.delete_comment(page_id)
    return f"/question/{question_id}"
