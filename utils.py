from datetime import datetime, timedelta
import data_manager
import os
import uuid
import bcrypt

PAGE_IDX, TAG_IDX = 1, 3
TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_new_user_id():
    user_id = str(uuid.uuid4()).split("-")[4]
    return user_id


def get_current_user_id(session):
    return (
        data_manager.get_user_id(session["email"]).get("id")
        if "email" in session
        else None
    )


def get_username(session):
    if "email" in session:
        return data_manager.get_username(session.get("email")).get("user_name")


def is_email_already_register(request):
    return request.form["email"] in [
        email["email_address"] for email in data_manager.get_user_emails()
    ]


def is_username_taken(request):
    return request.form["username"] in [
        username["user_name"] for username in data_manager.get_user_names()
    ]


def are_valid_credentials(request):
    if is_email_already_register(request):
        user_password = data_manager.get_user_pass(request.form["email"])["password"]
        return is_valid_password(request.form["password"], user_password)


def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def is_valid_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_text_password.encode("utf-8"), hashed_bytes_password)


def has_question_privilege(session, question_id):
    if "email" in session:
        current_user_id = data_manager.get_user_id(session["email"]).get("id")
        question_owner_id = data_manager.get_user_id_by_question_id(question_id).get(
            "user_id"
        )
        return question_owner_id == current_user_id


def has_answer_privilege(session, answer_id):
    if "email" in session:
        current_user_id = data_manager.get_user_id(session["email"]).get("id")
        answer_owner_id = data_manager.get_user_id_by_answer_id(answer_id).get(
            "user_id"
        )
        return current_user_id == answer_owner_id


def has_comment_privilege(session, comment_id):
    if "email" in session:
        current_user_id = data_manager.get_user_id(session["email"]).get("id")
        comment_owner_id = data_manager.get_user_id_by_comment_id(comment_id).get(
            "user_id"
        )
        return current_user_id == comment_owner_id


def update_to_pretty_time(real_dict_list):
    for dic in real_dict_list:
        dic.update({"submission_time": get_pretty_time(dic["submission_time"])})

    return real_dict_list


def get_formatted_dict(dictionary):
    dictionary["message"] = dictionary["message"].replace("\n", "<br>")
    return dictionary


def get_formatted_dicts(dicts):
    for d in dicts:
        get_formatted_dict(d)
    return dicts


def get_style(style_mode):
    if style_mode == "day":
        return "whitesmoke", "black"
    else:
        return "black", "whitesmoke"


def get_keys(real_dict_list):
    accepted_status = []
    if real_dict_list:
        for real_dict in real_dict_list:
            accepted_status.append(real_dict["accepted_status"])
    return accepted_status


def get_table_page_style(style_mode):
    if style_mode == "day":
        return "light", "dark"
    else:
        return "dark", "light"


def vote_question(idx, value, session):
    question_owner_id = data_manager.get_user_id_by_question_id(idx).get("user_id")
    current_user_id = get_current_user_id(session)
    vote_status = data_manager.get_vote_status("question_id", idx)
    vote_right = True
    for vote in vote_status:
        if vote["id"] == current_user_id:
            vote_right = False
    if vote_right and (question_owner_id != current_user_id):
        data_manager.add_user_vote_status((current_user_id, idx))
        data_manager.vote_question(idx, int(value))
        data_manager.update_reputation(idx, 5 if int(value) > 0 else -2)


def vote_answer(idx, value, session):
    answer_owner_id = data_manager.get_user_id_by_answer_id(idx).get("user_id")
    current_user_id = get_current_user_id(session)
    vote_status = data_manager.get_vote_status("answer_id", idx)
    vote_right = True
    for vote in vote_status:
        if vote["id"] == current_user_id:
            vote_right = False
    if vote_right and (answer_owner_id != current_user_id):
        data_manager.add_user_vote_status((current_user_id, None, idx))
        data_manager.vote_answer(idx, int(value))
        data_manager.update_reputation(idx, 10 if int(value) > 0 else -2)


def get_pretty_time(posted_time):
    elapsed_time = datetime.now() - posted_time
    years, days = divmod(elapsed_time.days, 365)
    months, days = divmod(days, 30)
    hours, seconds = divmod(elapsed_time.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if years > 0:
        return f"last year" if years == 1 else f"{years} years ago"
    elif months > 0:
        return f"last month" if months == 1 else f"{months} months ago"
    elif days > 0:
        return f"yesterday" if days == 1 else f"{days} days ago"
    elif hours > 0:
        return f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
    elif minutes > 0:
        return f"{minutes} minute ago" if minutes == 1 else f"{minutes} minutes ago"
    elif seconds > 0:
        return f"just now" if seconds == 1 else f"{seconds} seconds ago"


def saved_img(request):
    """Saves image and returns file name"""
    generated_file_name = None
    if request.files["img"]:
        file = request.files["img"]
        path = os.environ.get("VIRTUAL_ENV").replace("venv", "static/images/")
        generated_file_name = f"{uuid.uuid4()}-{file.filename}"
        file.save(f"{path}{generated_file_name}")
        generated_file_name = f"/static/images/{generated_file_name}"
    return generated_file_name


def get_page_id(page):
    page_id = page.split("-")[PAGE_IDX]
    return page_id


def delete_img(files_path):
    for path in files_path:
        abs_file_path = (
            f"{os.environ.get('VIRTUAL_ENV').replace('/venv', '')}{path.get('image')}"
        )
        if os.path.exists(abs_file_path):
            os.remove(abs_file_path)


def add_and_redirect(page, request, email):
    page_id = get_page_id(page)
    user_id = data_manager.get_user_id(email).get("id")

    if page == "add-question":
        add_question(request, user_id)
        page_id = data_manager.get_new_question_id()["new_id"]

    if page.endswith("new-answer"):
        add_answer(page_id, request, user_id)

    if page.endswith("new-comment"):
        redirect = add_comment_and_redirect(page, page_id, request, user_id)
        return redirect

    if page.endswith("new-tag"):
        add_tag(page_id, request)

    return f"/question/{page_id}"


def add_user(request):
    data_manager.add_user(
        (
            get_new_user_id(),
            request.form["username"],
            request.form["email"],
            TIME,
            hash_password(request.form["password"]),
            0,
        )
    )


def add_tag(page_id, request):
    all_tags, question_tags, question_tags_string = get_tags(page_id)
    if "tag" in request.form.keys():
        if not request.form["tag"] in [d["name"] for d in question_tags]:
            data_manager.add_tag_to_question(request.form["tag"], page_id)
    else:
        if not request.form["new_tag"] in [d["name"] for d in question_tags]:
            data_manager.add_tag(request.form["new_tag"])
            data_manager.add_tag_to_question(request.form["new_tag"], page_id)


def add_comment_and_redirect(page, page_id, request, user_id):
    if "answer" in page:
        question_id = data_manager.get_question_id_by_answer_id(page_id).get(
            "question_id"
        )
        new_comment = (None, page_id, user_id, request.form["message"], TIME, None)
        data_manager.add_comment(new_comment)
        return f"/question/{question_id}#{page_id}"

    else:
        new_comment = (page_id, None, user_id, request.form["message"], TIME, None)
        data_manager.add_comment(new_comment)
        return f"/question/{page_id}"


def add_answer(page_id, request, user_id):
    file_name = saved_img(request)
    new_answer = (TIME, 0, False, page_id, user_id, request.form["message"], file_name)
    data_manager.add_answer(new_answer)


def add_question(request, user_id):
    file_name = saved_img(request)
    new_question = (
        TIME,
        0,
        0,
        user_id,
        request.form["title"],
        request.form["message"],
        file_name,
    )
    data_manager.add_question(new_question)


def get_tags(page_id):
    (
        all_tags,
        question_tags,
    ) = data_manager.get_all_tags(), data_manager.get_question_tags(page_id)
    question_tags_string = ""
    for value in question_tags:
        question_tags_string += value["name"] + " "

    return all_tags, question_tags, question_tags_string


def edit_and_redirect(page, request):
    page_id = get_page_id(page)

    if "question" in page:
        update_question(page_id, request)
        return f"/question/{page_id}"

    if "answer" in page:
        question_id = data_manager.get_question_id_by_answer_id(page_id)["question_id"]
        update_answer(page_id, request)
        return f"/question/{question_id}#{page_id}"

    if "comment" in page:
        page = update_comment_and_redirect(page_id, request)
        return page


def update_question(page_id, request):
    delete_img(data_manager.get_question_img(page_id)) if request.files["img"] else None
    file_name = (
        saved_img(request)
        if request.files["img"]
        else data_manager.get_question_img(page_id)[0]["image"]
    )
    data_manager.update_question(
        page_id, request.form["title"], request.form["message"], file_name
    )


def update_answer(page_id, request):
    delete_img(data_manager.get_answer_img(page_id)) if request.files["img"] else None
    file_name = (
        saved_img(request)
        if request.files["img"]
        else data_manager.get_answer_img(page_id)[0]["image"]
    )
    data_manager.update_answer(page_id, TIME, request.form["message"], file_name)


def update_comment_and_redirect(page_id, request):
    edited_count = data_manager.get_comment_edited_count(page_id)["edited_count"]
    edited_count = 1 if edited_count is None else edited_count + 1
    data_manager.update_comment(page_id, request.form["message"], TIME, edited_count)
    question_id = data_manager.get_question_id_by_comment_id(page_id)["question_id"]
    if question_id is None:
        answer_id = data_manager.get_answer_id_by_comment_id(page_id)["answer_id"]
        question_id = data_manager.get_question_id_by_answer_id(answer_id)[
            "question_id"
        ]
        return f"/question/{question_id}#{answer_id}"

    return f"/question/{question_id}#{page_id}"


def delete_and_redirect(page):
    page_id = get_page_id(page)
    if "question" in page and "tag" not in page:
        delete_question(page_id)
        return "/"

    if "question" in page and "tag" in page:
        delete_tag(page, page_id)
        return f"/question/{page_id}"

    if "answer" in page:
        question_id = data_manager.get_question_id_by_answer_id(page_id).get(
            "question_id"
        )
        delete_answer(page_id)
        return f"/question/{question_id}"

    if "comments" in page:
        page = delete_comment_and_redirect(page_id)
        return page


def delete_question(page_id):
    images_related_to_question = data_manager.get_question_img(
        page_id
    ) + data_manager.get_answers_img_by_question_id(page_id)
    delete_img(images_related_to_question)
    data_manager.delete_question(page_id)


def delete_tag(page, page_id):
    tag_id = page.split("-")[TAG_IDX]
    data_manager.delete_tag_from_question(page_id, tag_id)


def delete_answer(page_id):
    delete_img(data_manager.get_answer_img(page_id))
    data_manager.delete_answer(page_id)


def delete_comment_and_redirect(page_id):
    question_id = data_manager.get_question_id_by_comment_id(page_id).get("question_id")
    if not question_id:
        answer_id = data_manager.get_answer_id_by_comment_id(page_id).get("answer_id")
        question_id = data_manager.get_question_id_by_answer_id(answer_id).get(
            "question_id"
        )
        data_manager.delete_comment(page_id)
        return f"/question/{question_id}#{answer_id}"

    data_manager.delete_comment(page_id)
    return f"/question/{question_id}"
