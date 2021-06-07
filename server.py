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
    all_questions = utils.get_formatted_dicts(data_manager.get_all_questions())
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
        count_question_answers=data_manager.count_question_answers
    )


@app.route("/search")
def search():
    background_color, font_color = style_mode()
    questions = data_manager.get_questions_with_phrase(request.values.get("q"))
    question_ids = tuple([q['id'] for q in questions])
    answers = data_manager.get_answers_with_message_by_question_ids(question_ids, request.values.get("q"))
    if request.args:
        session.update({'q': request.args['q']})

    return render_template(
        "index.html",
        answers=answers,
        all_questions=questions,
        background_color=background_color,
        font_color=font_color,
        phrase=request.values.get("q"),
        count_question_answers=data_manager.count_question_answers
    )


@app.route("/question/<question_id>")
def question_page(question_id):
    background_color, font_color = style_mode()
    data_manager.update_views(question_id) if request.method == "GET" else None

    return render_template(
        "question_display.html",
        question=utils.get_formatted_dict(data_manager.get_question(question_id)),
        answers=utils.get_formatted_dicts(data_manager.get_answers_by_question_id(question_id)),
        question_comments=utils.get_formatted_dicts(data_manager.get_question_comments(question_id)),
        latest_question_comment=data_manager.get_latest_comment_from_question(question_id).get('max'),
        answer_comments=data_manager.get_answer_comments,
        latest_answer_comment=data_manager.get_latest_comment_from_answer,
        question_tags=data_manager.get_question_tags(question_id),
        background_color=background_color,
        font_color=font_color,
    )


@app.route('/<page>/delete')
def delete_form(page):
    page_for_redirect = utils.delete_and_get_page(page)
    return redirect(page_for_redirect)


@app.route("/<page>", methods=["GET", "POST"])
def add_form(page):
    background_color, font_color = style_mode()
    page_id = utils.get_page_id(page)
    all_tags, question_tags, question_tags_string = None, None, None

    if page.endswith('new-tag'):
        all_tags, question_tags, question_tags_string = utils.get_tags(page_id)

    if request.form:
        page_for_redirect = utils.add_and_get_page(page, request)
        return redirect(page_for_redirect)

    return render_template(
        "form.html",
        background_color=background_color,
        font_color=font_color,
        page=page,
        action='add_form',
        tags=all_tags,
        question_tags=question_tags_string
    )


@app.route("/<page>/edit", methods=["GET", "POST"])
def edit_form(page):
    page_id = utils.get_page_id(page)
    background_color, font_color = style_mode()

    if request.form:
        page_for_redirect = utils.edit_and_get_page(page, request)
        return redirect(page_for_redirect)

    return render_template(
        "form.html",
        background_color=background_color,
        font_color=font_color,
        page=page,
        selected_question=data_manager.get_question(page_id),
        message=data_manager.get_answer_message(page_id) if 'answer' in page
        else data_manager.get_comment_message(page_id),
        action='edit_form',
    )


@app.route("/vote/")
def vote():
    idx, value = (
        request.values.get("id"),
        request.values.get('value')
    )
    data_manager.vote_question(idx, int(value)) if 'question' not in request.args['page'] \
        else data_manager.vote_answer(idx, int(value))

    return redirect(f"{request.args['page']}#{idx}")


if __name__ == "__main__":
    app.config["UPLOAD_FOLDER"] = "/static/images"
    app.run(debug=True)
