import database_common


@database_common.connection_handler
def get_all_questions(cursor, order_by='submission_time', order_dir='DESC'):
    if (order_by in ['title', 'submission_time', 'message', 'view_number', 'vote_number']) \
            and (order_dir.upper() in ['ASC', 'DESC']):
        query = f"""
            SELECT *
            FROM question
            ORDER BY {order_by} {order_dir.upper()}"""
        cursor.execute(query)
        return cursor.fetchall()


@database_common.connection_handler
def get_question(cursor, question_id):
    query = """
        SELECT *
        FROM question
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_question_img(cursor, question_id):
    query = """
        SELECT image
        FROM question
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_question_id_by_answer_id(cursor, answer_id):
    query = """
        SELECT question_id
        FROM answer
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_question_id_by_comment_id(cursor, comment_id):
    query = """
        SELECT question_id
        FROM comment
        WHERE id = %(comment_id)s"""
    cursor.execute(query, {'comment_id': comment_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_answer_id_by_comment_id(cursor, comment_id):
    query = """
        SELECT answer_id
        FROM comment
        WHERE id = %(comment_id)s"""
    cursor.execute(query, {'comment_id': comment_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_all_answers(cursor):
    query = """
        SELECT *
        FROM answer
        ORDER BY submission_time DESC"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_by_question_id(cursor, question_id):
    query = """
        SELECT *
        FROM answer
        WHERE question_id = %(question_id)s
        ORDER BY submission_time DESC"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_img_by_question_id(cursor, question_id):
    query = """
        SELECT image
        FROM answer
        WHERE question_id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_img(cursor, answer_id):
    query = """
        SELECT image
        FROM answer
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchall()


@database_common.connection_handler
def add_answer(cursor, data):
    query = """
        INSERT INTO answer (submission_time, vote_number, question_id, message, image)
        VALUES %(data)s"""
    cursor.execute(query, {'data': data})


@database_common.connection_handler
def add_question(cursor, data):
    query = """
        INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
        VALUES %(data)s"""
    cursor.execute(query, {'data': data})


@database_common.connection_handler
def get_tag_by_name(cursor, name):
    query = """
        SELECT id 
        FROM tag
        WHERE name = %(name)s
    """
    cursor.execute(query, {'name': name})
    return cursor.fetchone()


@database_common.connection_handler
def get_all_tags(cursor):
    query = """
        SELECT name FROM tag
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_question_tags(cursor, question_id):
    query = """
        SELECT * 
        FROM tag 
        WHERE id IN (SELECT tag_id from question_tag WHERE question_id=%(question_id)s)
    """
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def count_question_answers(cursor, question_id=None):
    query = """
        SELECT COUNT(id) 
        FROM answer
        WHERE question_id = %(question_id)s
    """
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchone()


@database_common.connection_handler
def add_tag(cursor, name):
    query = """
        INSERT INTO tag (name)
        VALUES (%(name)s)
    """
    cursor.execute(query, {'name': name})


@database_common.connection_handler
def add_tag_to_question(cursor, tag_name, question_id):
    tag_id = get_tag_by_name(tag_name)['id']
    query = """
        INSERT INTO question_tag
        VALUES (%s, %s)
    """
    cursor.execute(query, (question_id, tag_id))


@database_common.connection_handler
def delete_tag_from_question(cursor,question_id,tag_id):
    query = """
        DELETE FROM question_tag
        WHERE tag_id=%(tag_id)s AND question_id=%(question_id)s
    """
    cursor.execute(query, {'tag_id': tag_id, 'question_id': question_id})


@database_common.connection_handler
def add_comment(cursor, data):
    query = """
        INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count)
        VALUES %(data)s"""
    cursor.execute(query, {'data': data})


@database_common.connection_handler
def get_new_question_id(cursor):
    query = """
        SELECT max(id) as new_id
        FROM question"""
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def update_views(cursor, question_id):
    query = """
        UPDATE question
        SET view_number = view_number + 1
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})


@database_common.connection_handler
def update_question(cursor, question_id, title, message, image):
    query = """
        UPDATE question
        SET title = %(title)s, message = %(message)s, image = %(image)s 
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id, 'title': title, 'message': message, 'image': image})


@database_common.connection_handler
def delete_question(cursor, question_id):
    query = """
        DELETE FROM question_tag
        WHERE question_id = %(question_id)s;
        DELETE FROM comment
        WHERE answer_id IN (SELECT id FROM answer WHERE question_id = %(question_id)s);
        DELETE FROM comment
        WHERE question_id = %(question_id)s;
        DELETE FROM answer
        WHERE question_id = %(question_id)s;
        DELETE FROM question
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    query = """
        DELETE FROM comment
        WHERE answer_id = %(answer_id)s;
        DELETE FROM answer
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id})


@database_common.connection_handler
def delete_comment(cursor, comment_id):
    query = """
        DELETE FROM comment
        WHERE id = %(comment_id)s"""
    cursor.execute(query, {'comment_id': comment_id})


@database_common.connection_handler
def vote_question(cursor, question_id, value):
    query = """
        UPDATE question
        SET vote_number = vote_number + %(value)s
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id, 'value': value})


@database_common.connection_handler
def vote_answer(cursor, answer_id, value):
    query = """
        UPDATE answer
        SET vote_number = vote_number + %(value)s
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id, 'value': value})


@database_common.connection_handler
def get_question_comments(cursor, question_id):
    query = """
        SELECT id, message, submission_time, edited_count
        FROM comment
        WHERE question_id = %(question_id)s
        ORDER BY submission_time DESC"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_answer_comments(cursor, answer_id=None):
    query = """
        SELECT id, message, submission_time, edited_count
        FROM comment
        WHERE answer_id = %(answer_id)s
        ORDER BY submission_time DESC"""
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchall()


@database_common.connection_handler
def get_latest_comment_from_question(cursor, question_id):
    query = """
        SELECT max(submission_time)
        FROM comment
        WHERE question_id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_latest_comment_from_answer(cursor, answer_id=None):
    query = """
        SELECT max(submission_time)
        FROM comment
        WHERE answer_id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_question_message(cursor, question_id):
    query = """
        SELECT message
        FROM question
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_answer_message(cursor, answer_id):
    query = """
        SELECT message
        FROM answer
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_comment_message(cursor, comment_id):
    query = """
        SELECT message
        FROM comment
        WHERE id = %(comment_id)s"""
    cursor.execute(query, {'comment_id': comment_id})
    return cursor.fetchone()


@database_common.connection_handler
def update_comment(cursor, comment_id, message, submission_time, edited_count):
    query = """
        UPDATE comment
        SET message = %(message)s, submission_time = %(submission_time)s, edited_count = %(edited_count)s
        WHERE id = %(comment_id)s"""
    cursor.execute(query, {'comment_id': comment_id,
                           'message': message,
                           'submission_time': submission_time,
                           'edited_count': edited_count
                           }
                   )


@database_common.connection_handler
def update_answer(cursor, answer_id, submission_time, message, image):
    query = """
        UPDATE answer
        SET submission_time = %(submission_time)s, message = %(message)s, image = %(image)s
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id,
                           'submission_time': submission_time,
                           'message': message,
                           'image': image
                           }
                   )


@database_common.connection_handler
def get_comment_edited_count(cursor, comment_id):
    query = """
        SELECT edited_count
        FROM comment
        WHERE id = %(comment_id)s"""
    cursor.execute(query, {'comment_id': comment_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_questions_with_phrase(cursor, phrase):
    query = """
        SELECT *
        FROM question
        WHERE title ILIKE %(phrase)s 
        OR message ILIKE %(phrase)s
        OR id IN(SELECT question_id FROM answer WHERE message ILIKE %(phrase)s)"""
    cursor.execute(query, {"phrase": f'%{phrase}%'})
    return cursor.fetchall()


@database_common.connection_handler
def get_answers_with_message_by_question_ids(cursor, question_ids, phrase):
    query = """
        SELECT *
        FROM answer
        WHERE question_id IN %(question_ids)s AND message ILIKE %(phrase)s"""
    cursor.execute(query, {"question_ids": question_ids, "phrase": f'%{phrase}%'})
    return cursor.fetchall()
