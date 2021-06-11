from flask import Flask, session, render_template, redirect, request, url_for

import data_manager
import utils
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)


@app.route('/style-mode')
def style_mode():
    if 'style_mode' not in session:
        session.update({'style_mode': 'day'})
    background_color, font_color = utils.get_style(session['style_mode'])

    if request.args and 'style_mode' in request.args:
        session.update({'style_mode': request.args['style_mode']})
        if 'search' in request.args['page']:
            return redirect(url_for('search', q=session['q']))

        return redirect(request.args['page'])

    return background_color, font_color


@app.route("/")
@app.route("/list")
def index():
    all_questions = utils.update_to_pretty_time(
        utils.get_formatted_dicts(data_manager.get_all_questions()))
    background_color, font_color = style_mode()

    if request.args:
        all_questions = utils.get_formatted_dicts(
            data_manager.get_all_questions(
                request.args["order_by"],
                request.args["order_direction"]
            )
        )

    return render_template(
        "index.html",
        all_questions=all_questions if 'list' in request.base_url else all_questions[:5],
        background_color=background_color,
        font_color=font_color,
        count_question_answers=data_manager.count_question_answers,
        session=session,
        has_question_privilege=utils.has_question_privilege,
        question_tags=data_manager.get_question_tags,
        username=utils.get_username(session),
        current_user_id=utils.get_current_user_id(session),
        owner_user_name=data_manager.get_user_name_by_user_id
    )


@app.route('/users')
def users_page():
    background_color, font_color = style_mode()
    day, night = utils.get_table_page_style(session.get('style_mode'))
    users_table = data_manager.get_users_table()

    return render_template(
        'users.html',
        users_table=users_table,
        background_color=background_color,
        page_title='Users page',
        username=utils.get_username(session),
        current_user_id=utils.get_current_user_id(session),
        day=day,
        night=night
    )


@app.route('/user/<user_id>')
def user_page(user_id):
    background_color, font_color = style_mode()
    day, night = utils.get_table_page_style(session.get('style_mode'))
    users_table = data_manager.get_users_table()
    user_details = [user for user in users_table if user['id'] == user_id][0]
    user_questions = data_manager.get_user_questions(user_id)
    user_answers = data_manager.get_user_answers(user_id)
    user_comments = data_manager.get_user_comments(user_id)

    return render_template(
        'users.html',
        users_table=users_table,
        background_color=background_color,
        day=day,
        night=night,
        page_title=f'User {user_id} page',
        user_id=user_id,
        user_details=user_details,
        username=utils.get_username(session),
        current_user_id=utils.get_current_user_id(session),
        user_questions=user_questions,
        user_answers=user_answers,
        user_comments=user_comments,
        question_accepted_answers=data_manager.get_accepted_status_by_question_id,
        is_question_solved=utils.get_keys,
        question_id=data_manager.get_question_id_by_answer_id,
    )


@app.route("/tags")
@app.route("/tags/<selected_tag>")
def tag_list(selected_tag=None):
    background_color, font_color = style_mode()
    day, night = utils.get_table_page_style(session.get('style_mode'))
    tags = data_manager.get_all_tags()
    get_questions_by_tag = data_manager.get_questions_by_tag

    return render_template(
        'tag_list.html',
        tags=tags,
        get_questions_by_tag=get_questions_by_tag,
        selected_tag=selected_tag,
        background_color=background_color,
        day=day,
        night=night,
        username=utils.get_username(session),
        current_user_id=utils.get_current_user_id(session),
        question_accepted_answers=data_manager.get_accepted_status_by_question_id,
        is_question_solved=utils.get_keys
    )


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    background_color, font_color = style_mode()
    already_register_email = False
    user_name_taken = False
    if request.form:
        if utils.is_email_already_register(request):
            already_register_email = True
        elif utils.is_username_taken(request):
            user_name_taken = True
        else:
            utils.add_user(request)
            return redirect('/')

    return render_template(
        "form.html",
        background_color=background_color,
        font_color=font_color,
        page='sign-up',
        action='sign_up',
        already_register_email=already_register_email,
        user_name_taken=user_name_taken
    )


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    background_color, font_color = style_mode()
    invalid_credentials = False

    if request.form:
        if utils.are_valid_credentials(request):
            session.update({'email': request.form['email']})
            return redirect('/')
        else:
            invalid_credentials = True

    return render_template(
        "form.html",
        background_color=background_color,
        font_color=font_color,
        page='sign-in',
        action='sign_in',
        invalid_credentials=invalid_credentials
    )


@app.route('/sign-out')
def sign_out():
    session.pop('email', None)
    return redirect('/')


@app.route("/search")
def search():
    background_color, font_color = style_mode()
    questions = utils.update_to_pretty_time(
        data_manager.get_questions_with_phrase(request.values.get("q")))
    question_ids = tuple([q['id'] for q in questions])
    answers = utils.update_to_pretty_time(
        data_manager.get_answers_with_message_by_question_ids(question_ids, request.values.get("q")))
    if request.args:
        session.update({'q': request.args['q']})

    return render_template(
        "index.html",
        answers=answers,
        all_questions=questions,
        background_color=background_color,
        font_color=font_color,
        phrase=request.values.get("q"),
        count_question_answers=data_manager.count_question_answers,
        session=session,
        has_question_privilege=utils.has_question_privilege,
        question_tags=data_manager.get_question_tags,
        username=utils.get_username(session),
        current_user_id=utils.get_current_user_id(session),
        owner_user_name=data_manager.get_user_name_by_user_id
    )


@app.route("/question/<question_id>")
def question_page(question_id):
    background_color, font_color = style_mode()
    data_manager.update_views(question_id) if request.method == "GET" else None
    question = utils.get_formatted_dict(data_manager.get_question(question_id))
    question.update({'submission_time': utils.get_pretty_time(question['submission_time'])})
    question_comments = utils.update_to_pretty_time(
        utils.get_formatted_dicts(data_manager.get_question_comments(question_id)))
    answers = utils.update_to_pretty_time(
        utils.get_formatted_dicts(data_manager.get_answers_by_question_id(question_id)))

    return render_template(
        "question_display.html",
        question=question,
        answers=answers,
        question_comments=question_comments,
        answer_comments=data_manager.get_answer_comments,
        question_tags=data_manager.get_question_tags(question_id),
        background_color=background_color,
        font_color=font_color,
        session=session,
        has_question_privilege=utils.has_question_privilege(session, question_id),
        has_answer_privilege=utils.has_answer_privilege,
        has_comment_privilege=utils.has_comment_privilege,
        username=utils.get_username(session),
        current_user_id=utils.get_current_user_id(session),
        update_answers_comments=utils.update_to_pretty_time,
        owner_user_name=data_manager.get_user_name_by_user_id
    )


@app.route('/<page>/delete')
def delete_form(page):
    redirect_page = utils.delete_and_redirect(page)
    return redirect(redirect_page)


@app.route("/<page>", methods=["GET", "POST"])
def add_form(page):
    if 'email' not in session:
        return redirect(url_for('sign_in'))

    background_color, font_color = style_mode()
    page_id = utils.get_page_id(page)
    all_tags, question_tags, question_tags_string = None, None, None

    if page.endswith('new-tag'):
        all_tags, question_tags, question_tags_string = utils.get_tags(page_id)

    if request.form:
        redirect_page = utils.add_and_redirect(page, request, session.get('email'))
        return redirect(redirect_page)

    return render_template(
        "form.html",
        background_color=background_color,
        font_color=font_color,
        page=page,
        action='add_form',
        tags=all_tags,
        question_tags=question_tags_string,
        username=utils.get_username(session),
        current_user_id=utils.get_current_user_id(session)
    )


@app.route("/<page>/edit", methods=["GET", "POST"])
def edit_form(page):
    page_id = utils.get_page_id(page)
    background_color, font_color = style_mode()

    if request.form:
        redirect_page = utils.edit_and_redirect(page, request)
        return redirect(redirect_page)

    return render_template(
        "form.html",
        background_color=background_color,
        font_color=font_color,
        page=page,
        selected_question=data_manager.get_question(page_id),
        message=data_manager.get_answer_message(page_id) if 'answer' in page
        else data_manager.get_comment_message(page_id),
        action='edit_form',
        username=utils.get_username(session),
        current_user_id=utils.get_current_user_id(session)
    )


@app.route("/vote/")
def vote():
    if 'email' not in session:
        return redirect(url_for('sign_in'))
    idx, value, page, answer = (
        request.values.get("id"),
        request.values.get('value'),
        request.values.get('page'),
        request.values.get('answer')
    )
    if not answer:
        utils.vote_question(idx, value, session)
        return redirect(f"{page}#{idx}")

    utils.vote_answer(idx, value, session)
    return redirect(f"{page}#{idx}" if answer else page)


@app.route("/accepted-status")
def accepted_status():
    idx, status, question_id = (
        request.values.get('id'),
        bool(int(request.values.get('status'))),
        request.values.get('question_id')
    )
    answer_owner_id = data_manager.get_user_id_by_answer_id(idx).get('user_id')

    data_manager.update_accepted_status(idx, status)
    data_manager.update_reputation(answer_owner_id, 15 if status else -15)

    return redirect(f'/question/{question_id}#{idx}')


if __name__ == "__main__":
    app.config["UPLOAD_FOLDER"] = "/static/images"
    app.run(debug=True)
